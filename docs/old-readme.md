## 📘 `ntp-time` Documentation (English)

### Overview

`ntp-time` is a lightweight Python library that provides relatively accurate current time using NTP (Network Time Protocol) servers. It mimics `time.time()` by returning UNIX timestamps (floats), while internally handling synchronization, delay compensation, and background updates.

### Features

- `ntp_time.now()` does **not** perform any network access at the time of the call — making it fast and safe for frequent use.
- Provides accurate current time using NTP servers.
- Returns UNIX timestamp as `float`, just like `time.time()`.
- Internet communication delays are compensated (note: not guaranteed to be perfectly accurate).
- To prevent issues from "time going backward," corrections are smoothed over 10 seconds.
- By default, synchronization happens every minute in a **background thread** — no need to manage it manually.
- Synchronizes with `pool.ntp.org`, which provides access to multiple reliable NTP servers.
- On connection failure, automatic retries occur after 1s, 3s, 9s, and 27s. If all fail, the program raises an exception and exits.
- Accurate time is typically established within the first ~10 seconds of runtime.

### Installation

```bash
pip install ntp-time
```

### Usage

```python
import ntp_time

# Get the accurate current time
t = ntp_time.now()

print(t)  # e.g., 1743499065.294967 (float UNIX timestamp)
```

### Notes

- `now()` may return slightly inaccurate values for the first few seconds after startup, until synchronization completes.
- Time correction does not guarantee only forward movement; if time goes "backward", the library interpolates smoothl
