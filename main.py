import machine
import time

class IBUS:
    def __init__(self, uart):
        self.uart = uart
        self.channels = bytearray(14 * 2)  # 2 bytes per channel
        for i in range(0, 28, 2):
            self.channels[i:i+2] = bytes([0xDC, 0x05])  # Default to 1500
        self.last_received = time.ticks_ms()
        self.timeout = 500  # Timeout in milliseconds

    def read_channels(self):
        data_length = self.uart.any()
        if data_length >= 32:
            data = self.uart.read(data_length)
            # Check for IBUS header bytes
            if data[0] == 0x20 and data[1] == 0x40:
                self.channels[:28] = data[2:30]  # Update all channels
                self.last_received = time.ticks_ms()

    def check_timeout(self):
        if time.ticks_diff(time.ticks_ms(), self.last_received) > self.timeout:
            for i in range(0, 28, 2):
                self.channels[i:i+2] = bytes([0xDC, 0x05])  # Reset to 1500

    def get_channel(self, channel):
        if 1 <= channel <= 14:
            return int.from_bytes(self.channels[(channel-1)*2:channel*2], 'little')
        else:
            return None

def get_switch_status(value):
    if value < 1200:
        return "Position 1"
    elif value < 1800:
        return "Position 2"
    else:
        return "Position 3"

# Setup UART for RX only
uart = machine.UART(0, baudrate=115200, rx=machine.Pin(1))

ibus = IBUS(uart)

while True:
    ibus.read_channels()
    ibus.check_timeout()
    
    swa_status = get_switch_status(ibus.get_channel(7))
    swb_status = get_switch_status(ibus.get_channel(8))
    swc_status = get_switch_status(ibus.get_channel(9))
    swd_status = get_switch_status(ibus.get_channel(10))
    
    print("Ch1: {} | Ch2: {} | Ch3: {} | Ch4: {} | SWA: {} | SWB: {} | SWC: {} | SWD: {}".format(
        ibus.get_channel(1),
        ibus.get_channel(2),
        ibus.get_channel(3),
        ibus.get_channel(4),
        swa_status,
        swb_status,
        swc_status,
        swd_status
    ), end='\r')  # Overwrite the current line
    time.sleep(0.1)  # Adjust this delay for faster/slower updates

