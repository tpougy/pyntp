import os
import sys
import math
import time
import ntplib
import threading
import iter_backoff

class NTPTime:
    DEFAULT_ADJUST_INTERVAL = 60  # Synchronization interval (seconds)
    DEFAULT_MERGE_TIME = 10       # Time to merge into synchronized time (seconds)
    DEFAULT_NTP_SERVER_URL = "pool.ntp.org"

    def __init__(self,
                 ntp_server_url: str = DEFAULT_NTP_SERVER_URL,
                 adjust_interval: int = DEFAULT_ADJUST_INTERVAL,
                 merge_time: int = DEFAULT_MERGE_TIME,
                 threaded: bool = True):
        self.ntp_server_url = ntp_server_url
        self.adjust_interval = adjust_interval
        self.merge_time = merge_time
        self.threaded = threaded

        self.prev_offset = 0.0
        self.new_offset = 0.0
        self.switch_time_local = -math.inf  # Time when offset information was updated (local clock)

        self.lock = threading.Lock()
        self.client = ntplib.NTPClient()

        if self.threaded:
            self._start_adjust_loop_thread()
        else:
            # For non-threaded mode, perform an initial synchronization upon instantiation.
            # This ensures that the first `now()` call has a reasonable offset.
            try:
                self._recv_once()
            except Exception as e:
                # In a real scenario, this could be logged or handled with a more robust error policy.
                # For example, allowing the user to know that the first synchronization failed.
                print(f"[NTPTime Warning] Initial synchronization failed in non-threaded mode: {e}")

    def _get_offset(self) -> float:
        # Exponential backoff
        for _ in iter_backoff.iter_backoff(s0=1, r=3, n=5):
            try:
                # Perform time synchronization
                response = self.client.request(self.ntp_server_url, version=3)
                new_offset = response.offset
                return new_offset
            except Exception:
                # print(f"Error during NTP request: {e}") # For debug
                continue
        raise Exception(f"[NTPTime error] Exceeded exponential backoff attempts for NTP server communication with {self.ntp_server_url}")

    def _recv_once(self):
        # Get offset (with iter_backoff)
        new_offset = self._get_offset()
        # Rewrite offset
        with self.lock:
            self.prev_offset = self.new_offset
            self.switch_time_local = time.time()
            self.new_offset = new_offset

    def _adjust_loop(self):
        while True:
            try:
                # Perform one reception and switch offset information
                self._recv_once()
            except Exception as e:
                # If server connection fails, in class mode, we don't terminate the whole program.
                # Just log or raise a specific exception that can be handled.
                print(f"[NTPTime error] Failed to obtain information for time synchronization during adjust_loop: {e}")
                # Could have thread stopping logic here or more sophisticated retry.
                # For now, the thread continues to try after the interval.
            # Wait until the next time adjustment
            time.sleep(self.adjust_interval)

    def _start_adjust_loop_thread(self):
        # Periodically adjust time in a separate thread
        self.thread = threading.Thread(target=self._adjust_loop, daemon=True)  # Sub-thread also terminates when main thread terminates
        self.thread.start()

    def _get_smoothed_offset(self, local_time: float) -> float:
        with self.lock:
            # Calculate offset mixing ratio
            passed_time = local_time - self.switch_time_local  # Elapsed time since switch time
            raw_alpha = passed_time / self.merge_time if self.merge_time > 0 else 1.0
            alpha = max(0.0, min(raw_alpha, 1.0))  # Clipping
            # Correct offset
            fixed_offset = self.prev_offset * (1.0 - alpha) + self.new_offset * alpha
        return fixed_offset

    def now(self) -> float:
        # Time before correction
        local_time = time.time()

        if not self.threaded:
            try:
                self._recv_once()  # Update offset before each call in synchronous mode
            except Exception as e:
                # If synchronization fails, we can choose to return local time without correction
                # or raise the exception. For now, log and use the last known offset.
                print(f"[NTPTime Warning] Synchronization failed in non-threaded now(): {e}. Using last known offset.")

        # Correct time
        fixed_time = local_time + self._get_smoothed_offset(local_time)  # Get smoothly changing offset
        return fixed_time
