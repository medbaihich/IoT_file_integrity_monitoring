## Overview
This project is a Proof of Concept (PoC) for an **IoT File Integrity Monitoring (FIM)** system running on an ESP32 using MicroPython. The system continuously monitors a critical file (`secret.txt`) for unauthorized modifications or deletion using cryptographic hashing.

If a tampering attempt is detected, the system triggers an **Auto-Heal** mechanism to immediately restore the file from a secure backup and visually alerts the user.

## Features
* **Real-time Monitoring:** Continuously checks file integrity (default every 2 seconds).
* **SHA256 Hashing:** Uses robust hashing to detect any changes in the file content.
* **Auto-Healing:** Automatically restores the compromised file from the latest backup upon detection of an attack.
* **Visual Alert:** Blinks an LED (GPIO 2) when tampering is detected.
* **Attack Simulation:** Includes a built-in simulation that modifies the file after a set time to demonstrate the recovery process.
* **Logging:** Records security events and backups to `security_log.txt`.

## Hardware Required
* **ESP32 Development Board**
* **LED** (Connected to GPIO 2)
* **Resistor** (220Ω or similar for the LED)
* **USB Cable**

## Project Structure
* `main.py`: The core script containing the FIM logic, simulation, and auto-heal functions.
* `diagram.json`: Wokwi simulation diagram configuration.
* `scripts/download_release.py`: Helper script to download MicroPython firmware.

## Installation & Setup

1.  **Flash MicroPython:**
    Ensure your ESP32 is running MicroPython. You can use the provided script to download the firmware:
    ```bash
    python scripts/download_release.py 20240602-v1.23.0
    ```

2.  **Upload Files:**
    Upload `main.py` to the root directory of your ESP32 using a tool like Thonny IDE or `ampy`.

3.  **Hardware Connection:**
    * Connect the LED Anode (longer leg) to GPIO 2.
    * Connect the LED Cathode to GND via a resistor.

## Usage

1.  **Run the System:**
    * **Physical Hardware:** Reset the board or run `main.py` via your IDE (like Thonny).
    * **Wokwi Simulator:** While the simulator is running, open a command prompt and type:
        ```bash
        python -m mpremote connect port:rfc2217://localhost:4000 run main.py
        ```

2.  **Initialization:**
    * The system will ask for "secret content" to save in `secret.txt`.
    * It will create an initial backup in the `backups/` folder.
    * The monitoring loop starts immediately.

3.  **Simulation:**
    * By default, the system simulates an attack after **8 seconds**.
    * You will see the LED blink, and the console will show "ALERT! TAMPER DETECTED".
    * The system will automatically restore the file and print "SUCCESS: System Healed".

## Configuration
You can tweak the following variables at the top of `main.py`:
* `CHECK_INTERVAL_SECONDS`: Time between integrity checks.
* `SIMULATED_ATTACK_SECONDS`: Delay before the fake attack triggers.
* `LED_PIN`: GPIO pin for the alert LED.
