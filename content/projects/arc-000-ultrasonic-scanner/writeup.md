## Overview

ARC-000 was my first scanning rangefinder. I built a servo-swept ultrasonic scanner with Arduino control, 3D-printed mounting hardware, and a radar-style visualization of the serial output.

## Troubleshooting

The scanner reported false-positive distances clustered within 0.3 cm of each other. I worked through the problem by isolating one variable at a time: I checked readings against a tape measure, increased the reading resolution, averaged five pings per point, and finally ran a minimal test in open space. That process traced the fault to off-axis echoes within the sensor's ±15° beam cone. I designed extended printed shrouds in several lengths to trade interference rejection against signal strength.

## Iterating the hardware

I iterated the printed fixtures from a dovetail-locking desk clamp to a threaded-spindle clamp, and redesigned the sensor-to-servo bracket for wire clearance after a servo change. On the software side, I integrated the NewPing library, which removed a custom function and 10 lines of code while producing smoother scans, and I consolidated the power and ground wiring to eliminate the breadboard.

Switching to a time-of-flight sensor fixed the scans, and the difference between the two sensors became the subject of ARC-001.
