# flysky_iBus_Pico
Pico to read values from Flysky FS-IAB10B receiver iBus protocol
Receiver used FS-IA10B, pinout:
gnd - 5V (VBUS) - Signal (GP1)

To be implemented:
forward/reverse
BLDC/ESC signal transform
DC/Signal transform with polarity change using a motor driver and an encoder

Attention:
It is very important to activate failsafe and turn on for critical channels in order to reset channel values to default in event of signal lose!
