import _thread
from machine import UART, Pin, PWM
import utime

# Global variable for encoder position
global position
position = 0

# Function to update encoder position
def update_encoder():
    global position
    clk = Pin(6, Pin.IN, Pin.PULL_UP)  # Using GP6 for CLK
    dt = Pin(7, Pin.IN, Pin.PULL_UP)  # Using GP7 for DT
    clk_last = clk.value()

    while True:
        clk_state = clk.value()
        if clk_state != clk_last:
            if dt.value() != clk_state:
                position += 1
            else:
                position -= 1
            clk_last = clk_state
        utime.sleep(0.01)  # Short delay for stability

# Function to read iBus data
def read_ibus(uart):
    if uart.any():
        ibus_data = uart.read(32)
        return ibus_data
    else:
        return None

# Function to get channel value from iBus data
def get_channel_value(ibus_data, channel):
    value = int.from_bytes(ibus_data[2:4], 'little')
    return value

# Function to map RC input to target encoder position
def map_rc_to_position(rc_value):
    # Map 1000-2000 to -7 to 7
    return (rc_value - 1500) / (500 / 7)

# Function to control motor based on RC input and encoder position
def control_motor(uart, pwm_pin, dir_pin):
    global position
    deadband = 0.2  # Tolerance for target position
    max_pwm = 65535  # Maximum PWM duty cycle
    ramp_distance = 1  # Distance from target to start slowing down
    valid_rc_range = (1000, 2000)  # Define valid RC signal range
    speed = 0  # Default motor speed
    target_position = 0  # Default target position
    rc_channel_value = 1500  # Default RC channel value (neutral position)

    while True:
        ibus_data = read_ibus(uart)
        if ibus_data:
            rc_channel_value = get_channel_value(ibus_data, 1)

            # Check if RC signal is valid
            if valid_rc_range[0] <= rc_channel_value <= valid_rc_range[1]:
                target_position = map_rc_to_position(rc_channel_value)
            else:
                # If RC signal is not valid, default to center position
                target_position = 0

        distance_to_target = abs(position - target_position)

        if distance_to_target < deadband:
            speed = 0  # Stop motor if within deadband
        else:
            # Adjust speed when close to target or changing direction
            if distance_to_target < ramp_distance:
                speed = max(0, int((max_pwm * distance_to_target) / ramp_distance))
            else:
                speed = max_pwm

            if position < target_position:
                dir_pin.value(0)  # Move right
            elif position > target_position:
                dir_pin.value(1)  # Move left

        pwm_pin.duty_u16(speed)  # Set motor speed

        # Print for diagnostics
        print(f"Encoder Position: {position}, RC Value: {rc_channel_value}, Target: {target_position}, Speed: {speed}", end='\r')
        
        utime.sleep(0.05)  # Short delay for responsiveness

# Initialize UART for RC control
uart1 = UART(1, baudrate=115200, tx=4, rx=5)

# Initialize GPIO pins for motor control
pwm_pin = PWM(Pin(0))  # PWM for speed control
dir_pin = Pin(1, Pin.OUT)  # DIR for direction control
pwm_pin.freq(1000)  # Set PWM frequency

# Start the encoder thread
_thread.start_new_thread(update_encoder, ())

# Main thread for RC control and motor operation
control_motor(uart1, pwm_pin, dir_pin)

