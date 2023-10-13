import machine
import time

# Define the pin for the ESC
ESC_PIN = machine.Pin(2, machine.Pin.OUT)  # Using GP2

# Setup PWM for the ESC
esc_pwm = machine.PWM(ESC_PIN)

# Define duty cycle for "run"
RUN_DUTY = 16384  # Adjust as needed

# List of frequencies to test, add different frequence as needed
frequencies_to_test = [10, 40, 50, 60, 80, 90]

for freq in frequencies_to_test:
    # Set the PWM frequency
    esc_pwm.freq(freq)
    
    # Print the current frequency
    print("Testing frequency:", freq, "Hz")
    
    # Rotate the motor
    esc_pwm.duty_u16(RUN_DUTY)
    time.sleep(10)
    
    # Stop the motor
    esc_pwm.duty_u16(0)
    time.sleep(3)

print("Testing complete.")
