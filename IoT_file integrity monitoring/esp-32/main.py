# File Integrity Monitor (Auto-Heal + Restored Hash Display)
import uos as os
import sys
import time
import hashlib
import ubinascii

try:
    import machine
except ImportError:
    machine = None

# ---------- Configuration ----------
TARGET_FILE = "secret.txt"
LOG_FILE = "security_log.txt"
BACKUP_DIR = "backups"
CHECK_INTERVAL_SECONDS = 2
KEEP_BACKUPS = 3
LED_PIN = 2
LED_ACTIVE_LOW = False 

# Simulation Settings
SIMULATED_ATTACK_SECONDS = 8
SIMULATED_ATTACK_PAYLOAD = "HACKED BY GHOST!\n"
# -----------------------------------

def fmt_two(n):
    return "{:02d}".format(n)

def now_ts():
    try:
        t = time.localtime()
        return "{}-{}-{} {}:{}:{}".format(t[0], fmt_two(t[1]), fmt_two(t[2]),
                                          fmt_two(t[3]), fmt_two(t[4]), fmt_two(t[5]))
    except Exception:
        return str(time.time())

def ts_for_filename():
    try:
        t = time.localtime()
        return "{}{}{}_{}{}{}".format(t[0], fmt_two(t[1]), fmt_two(t[2]),
                                      fmt_two(t[3]), fmt_two(t[4]), fmt_two(t[5]))
    except Exception:
        return str(int(time.time()))

def log_event(message):
    timestamp = now_ts()
    line = "{} - {}\n".format(timestamp, message)
    print("[LOG] " + line.strip())
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass

def ensure_backup_dir():
    try:
        if BACKUP_DIR not in os.listdir():
            os.mkdir(BACKUP_DIR)
    except Exception:
        pass

def calculate_hash(filename):
    """Calculates SHA256 hash of the file."""
    try:
        h = hashlib.sha256()
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                h.update(chunk)
        return ubinascii.hexlify(h.digest()).decode()
    except Exception:
        return None

def create_backup():
    ensure_backup_dir()
    ts = ts_for_filename()
    bname = "{}_{}".format("secret", ts)
    dest = BACKUP_DIR + "/" + bname
    try:
        with open(TARGET_FILE, "rb") as src:
            data = src.read()
        with open(dest, "wb") as dst:
            dst.write(data)
        log_event("Backup created: {}".format(dest))
        return dest
    except Exception as e:
        log_event("Backup FAILED: {}".format(e))
        return None

def restore_latest_backup():
    try:
        backups = sorted([fn for fn in os.listdir(BACKUP_DIR) if fn.startswith("secret_")])
        if not backups:
            log_event("No backups available to restore.")
            return False
        latest = backups[-1]
        src = BACKUP_DIR + "/" + latest
        with open(src, "rb") as s:
            data = s.read()
        
        # Restore the file
        with open(TARGET_FILE, "wb") as t:
            t.write(data)
            
        # --- New update: Calculate and print the hash of the restored file ---
        restored_hash = calculate_hash(TARGET_FILE)
        log_event("Restored from: {} | Hash: {}".format(src, restored_hash))
        print(">> [CONFIRMATION] Restored File Hash: {}".format(restored_hash))
        # -----------------------------------------------------

        return True
    except Exception as e:
        log_event("Restore FAILED: {}".format(e))
        return False

led = None
def led_init():
    global led
    if machine is None: return
    try:
        led = machine.Pin(LED_PIN, machine.Pin.OUT)
        led.value(0)
    except Exception: pass

def led_blink(times=3, delay=0.15):
    if not led: return
    for _ in range(times):
        led.value(1); time.sleep(delay)
        led.value(0); time.sleep(delay)

# ---------- Main flow ----------
print("\n--- IOT - FIM ---\n")

# Write the initial content
print("Type secret content (or press Enter): ", end="")
try:
    user_text = input()
    if not user_text: user_text = "My Super Secret Data"
except Exception:
    user_text = "My Super Secret Data"

try:
    with open(TARGET_FILE, "w") as f:
        f.write(user_text)
    log_event("User content saved.")
except Exception as e:
    print("Error:", e)
    sys.exit()

ensure_backup_dir()
create_backup()
baseline_hash = calculate_hash(TARGET_FILE)
log_event("Baseline hash: {}".format(baseline_hash))

# Enable automatic self-repair
self_heal = True 
log_event("Self-heal: ENABLED (Auto)")

led_init()
print("\nMonitoring started. Attack in {}s...".format(SIMULATED_ATTACK_SECONDS))

start_time = time.time()
simulated_attack_done = False
last_check = time.time()

try:
    while True:
        now = time.time()

        #SIMULATION
        if (not simulated_attack_done) and (now - start_time >= SIMULATED_ATTACK_SECONDS):
            print("\n[SIMULATION] Attacking file now...")
            try:
                with open(TARGET_FILE, "w") as f:
                    f.write(SIMULATED_ATTACK_PAYLOAD)
                log_event("SIMULATION: File hacked.")
            except Exception as e:
                print("Attack failed:", e)
            simulated_attack_done = True

        # Checking
        if now - last_check >= CHECK_INTERVAL_SECONDS:
            current_hash = calculate_hash(TARGET_FILE)
            
            if current_hash is None:
                print("ALERT: File missing!")
                if self_heal:
                    restore_latest_backup()

            elif current_hash != baseline_hash:
                print("\n" + "!"*50)
                print("🚨 ALERT! TAMPER DETECTED")
                print("Baseline: {}".format(baseline_hash))
                print("Current : {}".format(current_hash))
                
                led_blink(5, 0.1)

                if self_heal:
                    print(">> Auto-Heal Triggered: Restoring backup...")
                    time.sleep(1.5) 
                    if restore_latest_backup():
                        print(">> SUCCESS: System Healed. ✅")
                        # Update the current hash
                        current_hash = calculate_hash(TARGET_FILE)
                    else:
                        print(">> FAIL: Restore failed.")
                
                print("!"*50 + "\n")
            else:
                sys.stdout.write(".")
                
            last_check = now
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped.")