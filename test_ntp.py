import time
from pyntp import NTPTime

def run_sync_test():
    print("--- Testando Modo Síncrono (time.google.com) ---")
    try:
        ntp_client_sync = NTPTime(threaded=False, ntp_server_url="time.google.com")
        print(f"Offset inicial (sync, time.google.com): {ntp_client_sync.new_offset}")

        for i in range(2): # Reduzido o número de iterações
            print(f"Chamando now() - Iter {i+1} (sync)...")
            current_time_sync = ntp_client_sync.now()
            local_time_sync = time.time()
            print(f"Iter {i+1}: NTP Time: {current_time_sync:.4f} ({time.ctime(current_time_sync)}), "
                  f"Local Time: {local_time_sync:.4f} ({time.ctime(local_time_sync)}), "
                  f"Diff (NTP-Local): {current_time_sync - local_time_sync:.4f}s")
            print(f"Offset após now() (sync): {ntp_client_sync.new_offset}")
            time.sleep(0.5) # Reduzido o sleep
    except Exception as e:
        print(f"Erro no teste síncrono: {e}")
        print("Verifique sua conexão com a internet e se o servidor time.google.com está acessível.")

if __name__ == "__main__":
    run_sync_test()
