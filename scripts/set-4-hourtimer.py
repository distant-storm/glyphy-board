from pijuice import PiJuice

pj = PiJuice(1, 0x14)

# Set alarm to trigger every 4 hours at minute 0, second 0
alarm = {
    'second': 0,
    'minute': 0,
    'hour_period': 4,      # Every 4 hours
    'day': 'EVERY_DAY'
}

# Set the alarm and enable wakeup
pj.rtcAlarm.SetAlarm(alarm)
pj.rtcAlarm.SetWakeupEnabled(True)
print("Alarm set to wake up every 4 hours")

