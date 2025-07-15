from pijuice import PiJuice

pijuice = PiJuice(1, 0x14)

print("Fault before clear:", pijuice.status.GetStatus())

# Clear fault (this method exists)
pijuice.power.ClearFault()

print("Fault after clear:", pijuice.status.GetStatus())
