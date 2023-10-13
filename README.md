# flysky_iBus_Pico
Pico to read values from Flysky FS-IAB10B receiver iBus protocol
Receiver used FS-IA10B, pinout:
gnd - 5V (VBUS) - Signal (GP1)

To be implemented:
forward/reverse
BLDC/ESC signal transform
DC/Signal transform with polarity change using a motor driver and an encoder

Attention:
-It is very important to activate failsafe and turn on for critical channels in order to reset channel values to default in event of signal lose!
-Some of these eBike controllers behave erratically due to signal frequency. You may want to consider testing frequencies. Mine appears to be proficient with 50Hz but may differ for other ESCs.

![image](https://github.com/SerdarAbali/flysky_iBus_Pico/assets/13032037/29b412cc-4580-452b-9a2e-9f0deb9e0d63)

