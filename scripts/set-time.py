from pijuice import PiJuice

pj = PiJuice(1, 0x14)

alarm = {
    'second': 0,
    'minute_period': 6,
    'hour': 'EVERY_HOUR',
    'day': 'EVERY_DAY'
}

pj.rtcAlarm.SetAlarm(alarm)
pj.rtcAlarm.SetWakeupEnabled(True)
print("Alarm set for every 6 minutes")

