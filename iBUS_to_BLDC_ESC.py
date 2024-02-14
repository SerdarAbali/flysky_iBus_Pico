import machine
import time

#Pico GP1 to RC receiver RX, right hand side, iBus mid pid vcc, left pin ground
#Pico GP2 to ESC pwm (also ground)
#Pico GP3/4 to ESC reverse (also ground)


class IBUS:
    def __init__(self, uart):
        self.uart = uart
        self.channels = bytearray(14 * 2)  # 2 bytes per channel
        for i in range(0, 28, 2):
            self.channels[i:i+2] = bytes([0xDC, 0x05])  # Default to 1500 for all channels
        self.channels[4:6] = bytes([0xE8, 0x03])  # Set channel 3 default to 1000
        self.last_received = time.ticks_ms()
        self.timeout = 500  # Timeout in milliseconds

    def read_channels(self):
        data_length = self.uart.any()
        if data_length >= 32:
            data = self.uart.read(data_length)
            if data[0] == 0x20 and data[1] == 0x40:
                self.channels[:28] = data[2:30]
                self.last_received = time.ticks_ms()

    def check_timeout(self):
        if time.ticks_diff(time.ticks_ms(), self.last_received) > self.timeout:
            for i in range(0, 28, 2):
                self.channels[i:i+2] = bytes([0xDC, 0x05])
            self.channels[4:6] = bytes([0xE8, 0x03])  # Reset channel 3 to 1000

    def get_channel(self, channel):
        if 1 <= channel <= 14:
            return int.from_bytes(self.channels[(channel-1)*2:channel*2], 'little')
        else:
            return None

uart = machine.UART(0, baudrate=115200, rx=machine.Pin(1)) #Pico GP1
gp3 = machine.Pin(3, machine.Pin.IN) #Pico GP2
reverse_pin = machine.Pin(4, machine.Pin.IN)  # #Pico GP3

def process_throttle_value(value):
    min_duty = 0
    max_duty = 65025
    return int((value - 1000) / 1000 * (max_duty - min_duty) + min_duty)

def get_switch_status(value):
    if value < 1200:
        return "Position 1"
    elif value < 1800:
        return "Position 2"
    else:
        return "Position 3"

ibus = IBUS(uart)

while True:
    ibus.read_channels()
    ibus.check_timeout()
    
    ch1_value = ibus.get_channel(1)
    
    if 1000 <= ch1_value <= 2000:
        if gp3.value() == machine.Pin.IN:
            gp3.init(mode=machine.Pin.OUT)
            esc_pwm_pin = machine.Pin(2, machine.Pin.OUT)
            esc_pwm = machine.PWM(esc_pwm_pin)
            esc_pwm.freq(50)
            neutral_duty = process_throttle_value(1500)
            esc_pwm.duty_u16(neutral_duty)
        
        throttle_value = process_throttle_value(ibus.get_channel(3))
        esc_pwm.duty_u16(throttle_value)
        
        swa_status = get_switch_status(ibus.get_channel(7))
        swb_status = get_switch_status(ibus.get_channel(8))
        swc_status = get_switch_status(ibus.get_channel(9))
        swd_status = get_switch_status(ibus.get_channel(10))
        
        if swa_status == "Position 3":
            reverse_pin.init(mode=machine.Pin.OUT)
            reverse_pin.low()  # Connect the brown wire to GND
        else:
            reverse_pin.init(mode=machine.Pin.IN)  # Disconnect the brown wire

        print("Ch1: {} | Ch2: {} | Ch3: {} | SWA: {} | SWB: {} | SWC: {} | SWD: {}".format(
            ibus.get_channel(1),
            ibus.get_channel(2),
            ibus.get_channel(3),
            swa_status,
            swb_status,
            swc_status,
            swd_status
        ), end='\r')
    else:
        if gp3.value() == machine.Pin.OUT:
            gp3.init(mode=machine.Pin.IN)
    
    time.sleep(0.1)



