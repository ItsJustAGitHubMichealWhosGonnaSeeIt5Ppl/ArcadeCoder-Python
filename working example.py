# THIS CODE WORKSA
import board
import digitalio
import time

# Define HC595 shift register pins
data_pin = digitalio.DigitalInOut(board.IO5)
clock_pin = digitalio.DigitalInOut(board.IO17)
latch_pin = digitalio.DigitalInOut(board.IO16)
output_enable_pin = digitalio.DigitalInOut(board.IO4)

data_pin.direction = digitalio.Direction.OUTPUT
clock_pin.direction = digitalio.Direction.OUTPUT
latch_pin.direction = digitalio.Direction.OUTPUT
output_enable_pin.direction = digitalio.Direction.OUTPUT
output_enable_pin.value = False  # Enable output

# Define LS138 row control pins
row_a0 = digitalio.DigitalInOut(board.IO19)
row_a1 = digitalio.DigitalInOut(board.IO18)
row_a2 = digitalio.DigitalInOut(board.IO21)

row_a0.direction = digitalio.Direction.OUTPUT
row_a1.direction = digitalio.Direction.OUTPUT
row_a2.direction = digitalio.Direction.OUTPUT

def shift_out(byte):
    """Send 8 bits to the shift register."""
    for i in range(8):
        bit = (byte >> (7 - i)) & 1
        data_pin.value = bit
        clock_pin.value = True
        clock_pin.value = False

def latch():
    """Latch the shift register output."""
    latch_pin.value = False
    latch_pin.value = True
    latch_pin.value = False

def set_row(row):
    """Set the active row for multiplexing (handling 12 rows)."""
    if row >= 5: # Offset by 5 to get all the LEDs working
        row -= 5  
    row_a0.value = (row & 0x01) > 0
    row_a1.value = (row & 0x02) > 0
    row_a2.value = (row & 0x04) > 0

def clear_matrix():
    """Clear the shift registers."""
    for _ in range(9):
        shift_out(0x00)  # Send 9 bytes of zeros
    latch()

def set_leds(color_data):
    """Set LED matrix data by sending color bytes per row."""
    for row in range(12):  # Handling all 12 rows
        set_row(row)
        for byte in color_data[row]:
            shift_out(byte)
        latch()
        time.sleep(.002)  # Small delay for multiplexing

# Example: Basic red display
def test_pattern():
    red_data = [[0xFF, 0x00, 0x00] * 3 for _ in range(12)]  # Red pattern across 12 rows
    while True:
        set_leds(red_data)
        #time.sleep(1.2)

test_pattern()