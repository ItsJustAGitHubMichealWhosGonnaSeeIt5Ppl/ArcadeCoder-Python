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


def ctrl_reg1(Ord30,LPen:bool,Xen:bool,Yen:bool,Zen:bool): #Temp working
    valid_power_modes = ['off','1hz','10hz','25hz','50hz','100hz','200hz','400hz','1.6khz','1.25khz','5khz']
    
    #LPen = Low Power Dissipation
    
    
    
    # Set with ORD3-0 bits
    psu_mode = {
        '0000': 'off',
        '0001': '1Hz',
        '0010': '10Hz',
        '0011': '25Hz',
        '0100': '50Hz',
        '0101': '100Hz',
        '0110': '200Hz',
        '0111': '400Hz',
        '1000': 'LP1.6KHz',
        '1001': '1.25kHz/LP5KHz' # Will need to figure out how to deal with these
    } 

while not i2c.try_lock():
    pass



# Library for Motion Sensor in I2C
class SC7A20():
    def __init__(self, i2c, low_power:bool=True, power_mode:str='50hz', g_scale:int=4, x_axis:bool=True, y_axis:bool=True, z_axis:bool=True, debug:bool=False):
        self.acclr = 0x19
        self.i2c = i2c
        # Valid scales are 2, 4, 8, and 16.  8 seems best, but 4 is the default 
        #### START OF SET UP ####

        # Replicate Accelerometer set up from stock firmware (Thanks @20goto10!)
        pass
    
    def _lock_i2c(self, timeout:int=None):
        while not self.i2c.try_lock():
            print("Failed to lock I2C")
            if timeout != None and timeout > 0:
                timeout-=1
            elif timeout != None and timeout <= 0:
                raise Exception("Reached Timeout!")
            
    def _read_settings(self): # Read current settings (control registers)
        #self._lock_i2c()
        creg_1 = bytearray(1)
        creg_2 = bytearray(1)
        creg_3 = bytearray(1)
        creg_4 = bytearray(1)
        creg_5 = bytearray(1)
        creg_6 = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG1"]]))
        self.i2c.readfrom_into(self.acclr, creg_1) # DEFAULT RESPONSE 0x07
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG2"]]))
        self.i2c.readfrom_into(self.acclr, creg_2) # DEFAULT RESPONSE 0x00
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG3"]]))
        self.i2c.readfrom_into(self.acclr, creg_3) # DEFAULT RESPONSE 0x00
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG4"]]))
        self.i2c.readfrom_into(self.acclr, creg_4) # DEFAULT RESPONSE 0x00
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG5"]]))
        self.i2c.readfrom_into(self.acclr, creg_5) # DEFAULT RESPONSE 0x00
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG6"]]))
        self.i2c.readfrom_into(self.acclr, creg_6) # DEFAULT RESPONSE 0x00
        return (creg_1, creg_2, creg_3, creg_4, creg_5, creg_6)
    
    def _bits_options_parse(self, options,choice): #Choice must already be formatted
        if choice not in options:
            raise ValueError("Invalid Option!")
        else:
            return options[choice]
    def _set_creg4(self,scale:int=2, bdu:bool=False, ble:bool=False, hr:bool=False, self_test:str='normal'):
        #BDU: Block Data Update - Uutput is not updated until both MSB and LSB are read
        #BLE: Big/Little-Endians. Enabling will send high byte data in low byte address?
        #HR: High Resolution (test to see what this does)
        #Self_test: Lots of options to go over

        byte = None
    
        # Get the scaling bits
        g_scales = {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}
        scale_bits = self._bits_options_parse(g_scales, int(scale))
       
        self_test_modes = {'normal': 0b00,
                    'test0': 0b01,
                    'test1': 0b10}
        self_test_bits = self._bits_options_parse(self_test_modes, self_test.lower())
            
        bdu_bit = 0b1 if bdu else 0b0
        ble_bit = 0b1 if ble else 0b0
        hr_bit = 0b1 if hr else 0b0
        
        byte = (bdu_bit << 7) + (ble_bit << 6) + (scale_bits << 4) + (hr_bit << 3) + self_test_bits
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG4"], byte]))
        
        
        

    def write_settings(self):
        pass
    
    def _default_settings(self): # Match default settings from the ArcadeCoder
        #self._lock_i2c()
        
        # WRITE CTRL REG1 TO 0x4F (Probably 01001111) This could be settings the output rate setting to "Normal l / low power passition mode (50 Hz)"
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG1"], 0x4F]))
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG2"], 0x00]))
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG3"], 0x00]))
        # WRITE CTRL REG4 TO 0x10 (Probably 00010000) I think this is setting the scale to +/-4Gs
        #i2c.writeto(self.acclr, bytes([register_map["CTRL_REG4"], 0x10])) #30 should set scale to 16Gs
        self._set_creg4(scale=16) # Default settings
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG5"], 0x00]))
        self.i2c.writeto(self.acclr, bytes([register_map["CTRL_REG6"], 0x00]))
        
        # VERIFY
        new_settings = self._read_settings()
        
        
        # READ TEMP CONFIG, EXPECT RESPONSE 0x00
        result = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["TEMP_CFG"]]))
        self.i2c.readfrom_into(self.acclr, result)
        print(f" R: TEMP_CFG: {result} - EXPECT: 0x00")

        # WRITE TEMP CONFIG TO 0x00
        self.i2c.writeto(self.acclr, bytes([register_map["TEMP_CFG"], 0x00]))
        print(f" W: TEMP_CFG TO 0x00")



        print(f" W: CTRL_REG1 TO 0x4F")

        # READ CTRL REG1 - The original code doesn't do this, but I don't trust that I've done this right
        result = bytearray(1)


        # READ WHO AM I, EXPECT RESPONSE 0x11
        result = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["WHO_AM_I"]]))
        self.i2c.readfrom_into(self.acclr, result)
        print(f" R: WHO_AM_I: {result}")
        
        #self.i2c.unlock() 
    
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
        #self._lock_i2c()
        #status = bytearray(1)
        #i2c.writeto(self.acclr, bytes([register_map["STATUS_REG"]]))
        #i2c.readfrom_into(self.acclr, status) # Status of 0xff seems to be what we're after
        #TODO validate the status, if it isnt 0xff, throw an error or something idk
        
        
        # THIS DATA IS IN "2's COMPLEMENT NUMBER" I DONT KNOW WHAT THE FUCK THAT MEANS
        
        # X BYTES
        xl = bytearray(1)
        xh = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["OUT_X_L"]]))
        self.i2c.readfrom_into(self.acclr, xl)
        
        self.i2c.writeto(self.acclr, bytes([register_map["OUT_X_H"]]))
        self.i2c.readfrom_into(self.acclr, xh)
        x = self._ai_2s_complement_thing(xl,xh)
        
        # Y BYTES
        yl = bytearray(1)
        yh = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["OUT_Y_L"]]))
        self.i2c.readfrom_into(self.acclr, yl)
        
        self.i2c.writeto(self.acclr, bytes([register_map["OUT_Y_H"]]))
        self.i2c.readfrom_into(self.acclr, yh)
        y = self._ai_2s_complement_thing(yl,yh)
        
        # Z BYTES
        zl = bytearray(1)
        zh = bytearray(1)
        self.i2c.writeto(self.acclr, bytes([register_map["OUT_Z_L"]]))
        self.i2c.readfrom_into(self.acclr, zl)

        self.i2c.writeto(self.acclr, bytes([register_map["OUT_Z_H"]]))
        self.i2c.readfrom_into(self.acclr, zh)
        z = self._ai_2s_complement_thing(zl,zh)
        #self.i2c.unlock() 
        return (x, y, z)


accelerometer = SC7A20(i2c=i2c)
accelerometer._default_settings()

while True:
    time.sleep(0.01)
    x,y,z = accelerometer.get_data()
    print(f"X{x},Y{y},Z{z}")




