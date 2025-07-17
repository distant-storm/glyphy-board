#!/usr/bin/env python3

from pijuice import PiJuice
from datetime import datetime
import logging
import sys

# === Setup logging ===
logfile = "/var/log/pijuice_wakeup_debug.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler(sys.stdout)
    ]
)

def log_heading(title):
    logging.info("\n" + "=" * 40)
    logging.info(title)
    logging.info("=" * 40)

# === Initialize PiJuice ===
try:
    pijuice = PiJuice(1, 0x14)
except Exception as e:
    logging.error("PiJuice not detected. Is it connected and powered?")
    logging.error(e)
    sys.exit(1)

# === 1. Power Status ===
log_heading("1. PiJuice Power Status")
try:
    status = pijuice.status.GetStatus()
    logging.info(status)
except Exception as e:
    logging.error("Error getting power status.")
    logging.error(e)

# === 2. RTC Alarm Time ===
log_heading("2. RTC Alarm & Time")
try:
    rtc_alarm = pijuice.rtcAlarm.GetAlarm()
    logging.info(f"RTC Alarm: {rtc_alarm}")
except Exception as e:
    logging.error("Error reading RTC alarm.")
    logging.error(e)

try:
    rtc_time = pijuice.rtcAlarm.GetDateTime()
    logging.info(f"RTC Time Raw: {rtc_time}")
    rtc_data = rtc_time.get("data", {})
    if rtc_data:
        rtc_dt = datetime(rtc_data["year"], rtc_data["month"], rtc_data["day"],
                          rtc_data["hour"], rtc_data["minute"], rtc_data["second"])
        logging.info(f"RTC Time Parsed: {rtc_dt}")
except Exception as e:
    logging.error("Error reading RTC time.")
    logging.error(e)

# === 3. System Time Comparison ===
log_heading("3. System vs RTC Time")
try:
    system_time = datetime.now()
    logging.info(f"System Time: {system_time}")
    if 'rtc_dt' in locals():
        delta = system_time - rtc_dt
        logging.info(f"Time Difference: {delta}")
except Exception as e:
    logging.error("Error comparing system and RTC times.")
    logging.error(e)

# === 4. Wake Triggers (Charge, GPIO) ===
log_heading("4. Wakeup Triggers")
try:
    wake_on_charge = pijuice.power.GetWakeUpOnCharge()
    logging.info(f"Wake on Charge: {wake_on_charge}")
except Exception as e:
    logging.error("Error reading Wake on Charge.")
    logging.error(e)

try:
    wake_on_gpio = pijuice.power.GetWakeUpOnGpio()
    logging.info(f"Wake on GPIO: {wake_on_gpio}")
except Exception as e:
    logging.error("Error reading Wake on GPIO.")
    logging.error(e)

# === 5. Battery & Input ===
log_heading("5. Battery & Power Input")
try:
    charge_level = pijuice.status.GetChargeLevel()
    logging.info(f"Charge Level: {charge_level}")
    voltage = pijuice.status.GetBatteryVoltage()
    logging.info(f"Battery Voltage: {voltage}")
    current = pijuice.status.GetBatteryChargeCurrent()
    logging.info(f"Charge Current: {current}")
except Exception as e:
    logging.error("Error reading battery or input stats.")
    logging.error(e)

# === 6. Button Config (SW1) ===
log_heading("6. Button Configuration (SW1)")
try:
    button_config = pijuice.config.GetButtonConfiguration('SW1')
    logging.info(f"SW1 Config: {button_config}")
except Exception as e:
    logging.error("Error reading button configuration.")
    logging.error(e)

# === End ===
log_heading("✅ Wakeup Check Complete")

