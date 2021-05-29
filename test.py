import krpc
import time
import math

# FUNCTION DEFINITIONS

def speed(frame):
    return vessel.flight(frame).speed

def velocity(frame):
    return vessel.flight(frame).velocity

def verticallyAccelerate(acceleration, angle = 0):
    shipWeight = vessel.mass*9.802
    vessel.control.throttle = (shipWeight + (acceleration*vessel.mass)) / vessel.available_thrust

def keepVelocity(targetVelocity, aggression = 5, axis = 0):
    targetVelocityDelta = aggression*(targetVelocity - velocity(veloframe)[axis])
    verticallyAccelerate(targetVelocityDelta)

def suicideVelocity():
    squareRoot = 2 * (((vessel.available_thrust) - (vessel.mass*9.802)) / vessel.mass) * (sl_alt() - start_alt - 1)
    if (squareRoot > 0):
        return -1 * math.sqrt(squareRoot) + 1
    else:
        return 0

def adj_alt():
    return sl_alt() - vessel.flight().elevation - alt_adj

def ground_alt():
    return vessel.flight().elevation + alt_adj

#log = open("flightLog.txt", "w+")

conn = krpc.connect(name='controller')
vessel = conn.space_center.active_vessel
print("controlling: " + vessel.name)

time.sleep(3)

# set up reference frames
obt = vessel.orbit.body.non_rotating_reference_frame
srf = vessel.orbit.body.reference_frame

veloframe = conn.space_center.ReferenceFrame.create_hybrid(
    position=vessel.orbit.body.reference_frame,
    rotation=vessel.surface_reference_frame)

# set up telemetry
sl_alt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
surf_alt = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')

vessel.control.sas = True

start_alt = sl_alt()
start_elevation = vessel.flight().elevation
alt_adj = start_alt - start_elevation

vessel.control.throttle = 1
time.sleep(1)

print('launch')
vessel.control.activate_next_stage()

time.sleep(2)

while True:
    if (sl_alt() > 15000):
        break
    keepVelocity(1000)
    time.sleep(0.1)

vessel.control.throttle = 0

while True:
    if (abs(velocity(veloframe)[0]) < 5):
        break

while True:
    if (abs(velocity(veloframe)[0]) > 50):
        break

vessel.control.sas_mode = vessel.control.sas_mode.retrograde

while True:
    if (abs(velocity(veloframe)[0]) < 50):
        break
    keepVelocity(suicideVelocity(), 20)
    time.sleep(0.02)

vessel.control.sas_mode = vessel.control.sas_mode.stability_assist

while True:
    if (abs(velocity(veloframe)[0]) < 2.5):
        break
    keepVelocity(suicideVelocity(), 20)
    time.sleep(0.02)

while True:
    if (adj_alt() < 0.3):
        break
    keepVelocity(-1, 20)
    time.sleep(0.02)

vessel.control.throttle = 0

vessel.control.sas = False