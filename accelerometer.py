# ACCELEROMETER CLASS/PACKAGE (WIP)
import board
import busio
import time

# SDO seems to be floating/pulled high?

i2c = busio.I2C(board.IO27, board.IO26)
acclr = 0x19 # Looks like its 0x19 for main functionality
config = 0x20 # I think this is for configuring?

# Register Map
register_map = {
    "OUT_TEMP_L": 0x0C,
    "OUT_TEMP_H": 0x0D,
    "WHO_AM_I": 0x0F,
    "NVM_WR": 0x1E,
    "TEMP_CFG": 0x1F,
    "CTRL_REG1": 0x20,
    "CTRL_REG2": 0x21,
    "CTRL_REG3": 0x22,
    "CTRL_REG4": 0x23,
    "CTRL_REG5": 0x24,
    "CTRL_REG6": 0x25,
    "REFERENCE": 0x26,
    "STATUS_REG": 0x27,
    "OUT_X_L": 0x28,
    "OUT_X_H": 0x29,
    "OUT_Y_L": 0x2A,
    "OUT_Y_H": 0x2B,
    "OUT_Z_L": 0x2C,
    "OUT_Z_H": 0x2D,
    "FIFO_CTRL_REG": 0x2E,
    "FIFO_SRC_REG": 0x2F,
    "INT1_CFG": 0x30,
    "INT1_SOURCE": 0x31,
    "INT1_THS": 0x32,
    "INT1_DURATION": 0x33,
    "INT2_CFG": 0x34,
    "INT2_SOURCE": 0x35,
    "INT2_THS": 0x36,
    "INT2_DURATION": 0x37,
    "CLICK_CFG": 0x38,
    "CLICK_SRC": 0x39,
    "CLICK_THS": 0x3A,
    "TIME_LIMIT": 0x3B,
    "TIME_LATENCY": 0x3C,
    "TIME_WINDOW": 0x3D,
    "ACT_THS": 0x3E,
    "ACT_DURATION": 0x3F,
}



# Library for Motion Sensor in I2C
class SC7A20():

    def __init__(self, scale:int=4, x_axis:bool=True, y_axis:bool=True, z_axis:bool=True, debug:bool=False):
        
        # Valid scales are 2, 4, 8, and 16.  8 seems best, but 4 is the default 
        #### START OF SET UP ####

        # Replicate Accelerometer set up from stock firmware (Thanks @20goto10!)
        
        while not i2c.try_lock():
            pass
        # READ TEMP CONFIG, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["TEMP_CFG"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: TEMP_CFG: {result} - EXPECT: 0x00")

        # WRITE TEMP CONFIG TO 0x00
        i2c.writeto(acclr, bytes([register_map["TEMP_CFG"], 0x00]))
        print(f" W: TEMP_CFG TO 0x00")

        # READ CTRL REG1, EXPECT RESPONSE 0x07 (Probably 00000111).  Basically means the chip is turned off?
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG1"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG1: {result} - EXPECT: 0x07")

        # READ CTRL REG2, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG2"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG2: {result} - EXPECT: 0x00")

        # READ CTRL REG3, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG3"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG3: {result} - EXPECT: 0x00")

        # READ CTRL REG4, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG4"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG4: {result} - EXPECT: 0x00")

        # READ CTRL REG5, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG5"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG5: {result} - EXPECT: 0x00")

        # READ CTRL REG6, EXPECT RESPONSE 0x00
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG6"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG6: {result} - EXPECT: 0x00")


        # WRITE CTRL REG1 TO 0x4F (Probably 01001111) This could be settings the output rate setting to "Normal l / low power passition mode (50 Hz)"
        i2c.writeto(acclr, bytes([register_map["CTRL_REG1"], 0x4F]))
        print(f" W: CTRL_REG1 TO 0x4F")

        # READ CTRL REG1 - The original code doesn't do this, but I don't trust that I've done this right
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["CTRL_REG1"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: CTRL_REG1: {result} - EXPECT: 0x4F (ASCII FORMAT IS O)")

        # WRITE CTRL REG2 TO 0x00 - Seems to leave it as default
        i2c.writeto(acclr, bytes([register_map["CTRL_REG2"], 0x00]))
        print(f" W: CTRL_REG2 TO 0x00")

        # WRITE CTRL REG3 TO 0x00 - Seems to leave it as default
        i2c.writeto(acclr, bytes([register_map["CTRL_REG3"], 0x00]))
        print(f" W: CTRL_REG3 TO 0x00")

        # WRITE CTRL REG4 TO 0x10 (Probably 00010000) I think this is setting the scale to +/-4Gs
        i2c.writeto(acclr, bytes([register_map["CTRL_REG4"], 0x30])) #30 should set scale to 16Gs
        print(f" W: CTRL_REG4 TO 0x10")

        # WRITE CTRL REG5 TO 0x00 - Seems to leave it as default
        i2c.writeto(acclr, bytes([register_map["CTRL_REG5"], 0x00]))
        print(f" W: CTRL_REG5 TO 0x00")

        # WRITE CTRL REG6 TO 0x00 - Seems to leave it as default
        i2c.writeto(acclr, bytes([register_map["CTRL_REG6"], 0x00]))
        print(f" W: CTRL_REG6 TO 0x00")
        


        # READ WHO AM I, EXPECT RESPONSE 0x11
        result = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["WHO_AM_I"]]))
        i2c.readfrom_into(acclr, result)
        print(f" R: WHO_AM_I: {result}")
        
        i2c.unlock()
    
    def _ai_2s_complement_thing(self, _l, _h): # Ok FINE maybe AI is kinda useful every once and awhile # SCALING IS WRONG FUCK YOU AI
        msb = _h[0]
        lsb = _l[0]

        # Combine the two bytes into a 16-bit integer
        combined_value = (msb << 8) | lsb

        # Check if the combined value is negative (based on the most significant bit of the 16-bit value)
        if (combined_value & 0x8000):  # Check if the 15th bit is set
            # It's a negative number, so perform 2's complement conversion
            inverted_value = ~combined_value & 0xFFFF  # Invert all bits and mask to 16 bits
            signed_value = -(inverted_value + 1)
        else:
            # It's a positive number
            signed_value = combined_value
        
        fixed_scale = signed_value / 128 # Fix scaling
        
        return int(fixed_scale)
    
    def get_data(self): # Return tuple containing X, Y, Z

        #status = bytearray(1)
        #i2c.writeto(acclr, bytes([register_map["STATUS_REG"]]))
        #i2c.readfrom_into(acclr, status) # Status of 0xff seems to be what we're after
        #TODO validate the status, if it isnt 0xff, throw an error or something idk
        # THIS DATA IS IN "2's COMPLEMENT NUMBER" I DONT KNOW WHAT THE FUCK THAT MEANS
        
        # X BYTES
        xl = bytearray(1)
        xh = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["OUT_X_L"]]))
        i2c.readfrom_into(acclr, xl)
        
        i2c.writeto(acclr, bytes([register_map["OUT_X_H"]]))
        i2c.readfrom_into(acclr, xh)
        x_real = self._ai_2s_complement_thing(xl,xh)
        
        # Y BYTES
        yl = bytearray(1)
        yh = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["OUT_Y_L"]]))
        i2c.readfrom_into(acclr, yl)
        
        i2c.writeto(acclr, bytes([register_map["OUT_Y_H"]]))
        i2c.readfrom_into(acclr, yh)
        y_real = self._ai_2s_complement_thing(yl,yh)
        
        # Z BYTES
        zl = bytearray(1)
        zh = bytearray(1)
        i2c.writeto(acclr, bytes([register_map["OUT_Z_L"]]))
        i2c.readfrom_into(acclr, zl)

        i2c.writeto(acclr, bytes([register_map["OUT_Z_H"]]))
        i2c.readfrom_into(acclr, zh)
        z_real = self._ai_2s_complement_thing(zl,zh)
        
        return (x_real, y_real, z_real)
        #print(f"X: {x_real}, Y {y_real}, Z {z_real}")
        #time.sleep(0.01)







