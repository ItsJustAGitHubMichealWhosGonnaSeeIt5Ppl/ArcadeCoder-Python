# WILL BE PACKAGE FOR ARCADE CODER LEDs
import board
import digitalio
import time
import analogio

#TODO implement SPI correctly 
#TODO text scroller

# Define HC595 shift register pins
HC595_DATA = digitalio.DigitalInOut(board.IO5)
HC595_CLOCK = digitalio.DigitalInOut(board.IO17)
HC595_LATCH = digitalio.DigitalInOut(board.IO16)
HC595_OE = digitalio.DigitalInOut(board.IO4)

HC595_DATA.direction = digitalio.Direction.OUTPUT
HC595_CLOCK.direction = digitalio.Direction.OUTPUT
HC595_LATCH.direction = digitalio.Direction.OUTPUT
HC595_OE.direction = digitalio.Direction.OUTPUT
HC595_OE.value = False #IDK it got whiney when this wasn't here
HC595_LATCH.value = False

# IF OUTPUT ENABLE IS SET TO TRUE, THEN FALSE, 0 WILL BE ON, 255 WILL BE OFF.  IF INVERTED, YOUR COLORS WILL BE AS WELL


# IC2012 Pins
ICN_A0 = digitalio.DigitalInOut(board.IO19)
ICN_A1 = digitalio.DigitalInOut(board.IO18)
ICN_A2 = digitalio.DigitalInOut(board.IO21)

ICN_A0.direction = digitalio.Direction.OUTPUT
ICN_A1.direction = digitalio.Direction.OUTPUT
ICN_A2.direction = digitalio.Direction.OUTPUT

# Button Rows
BTN1_7 = analogio.AnalogIn(board.I39)
BTN2_8 = analogio.AnalogIn(board.I36)
BTN3_9 = analogio.AnalogIn(board.I35)
BTN4_10 = analogio.AnalogIn(board.I34)
BTN5_11 = analogio.AnalogIn(board.IO33)
BTN6_12 = analogio.AnalogIn(board.IO32)


def set_row(row:int):
    """Set the active rows (1 - 6)"""
    # Assuming top of board is farthest from the IO, and top of board is row 1
    
    #if row > 7 or row < 0: # Basic input validation
        #raise ValueError("Please enter a row between 1 and 6")
    
    # This is terrible and should be fixed
    if row == 1: # 6/12 = False, True, True #TODO this one doesn't work
        ICN_A0.value = False
        ICN_A1.value = True
        ICN_A2.value = True

    elif row == 6: # 5/11 = True, False, False
        ICN_A0.value = True
        ICN_A1.value = False
        ICN_A2.value = False
    
    elif row == 5: # 4/10 = False, False, True
        ICN_A0.value = False
        ICN_A1.value = False
        ICN_A2.value = True
    
    elif row == 4: # 3/9 = True, False, True
        ICN_A0.value = True
        ICN_A1.value = False
        ICN_A2.value = True
        
    elif row == 3: # 2/8 = True, True, False
        ICN_A0.value = True
        ICN_A1.value = True
        ICN_A2.value = False
        
    elif row == 2: # 1/7 = False, True, False
        ICN_A0.value = False
        ICN_A1.value = True
        ICN_A2.value = False
        
    elif row == 7: # ALL TRUE
        ICN_A0.value = True
        ICN_A1.value = True
        ICN_A2.value = True
        
    elif row == 0: # ALL TRUE
        ICN_A0.value = False
        ICN_A1.value = False
        ICN_A2.value = False
    #print(f"ROWS SET {row}")
    
# Very optimised loop for testing
byetes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
set_row(1)
while False:
    set_row(1)
    time.sleep(0.002)
    HC595_LATCH.value = False
    HC595_OE.value = False
    for bit in byetes:
        HC595_DATA.value = bit
        HC595_CLOCK.value = True
        HC595_CLOCK.value = False
    
    HC595_LATCH.value = True
    HC595_OE.value = True
    time.sleep(0.002)




class TechDidntSaveUs:
    def __init__(self, size_x:int=11, size_y:int=11):
        """Matrix controller for the Arcade Coder made by TWSU.
        
        Default grid size is 12x12 (single Arcade Coder).
        
        Partially translated from padraigfl's C++ libray.  Lots of help from the TWSU Support Group Discord.

        Args:
            size_x (int, optional): The LED grid horizontal size (assuming that the grid starts at 0,0). Defaults to 11.
            size_y (int, optional): The LED grid vertical size (assuming that the grid starts at 0,0). Defaults to 11.
        """
        # Assuming coords starts at 0, 0
        self.matrix_sixe_x = size_x
        self.matrix_sixe_y = size_y
        #TODO make an array for the love of god
        self.led_matrix_rgb = [[[1,1,1] for _ in range(self.matrix_sixe_x+1)] for _ in range(self.matrix_sixe_y + 1)]# blank grid to start
        #self.blank_row_data = self.create_grid() # Create a blank set of data to clear the panel
        
        
        self.btn_pressed_counts = [0,0,0,0,0,0] # Counts rows where buttons are pressed

    def _send_data_to_controllers(self, data):
        """Send 8 bits to the shift register."""
        HC595_LATCH.value = False
        for byte in data: # Data is sent as a list of lists
            for bit_raw in byte: # for each list we iterate through and set the value
                
                HC595_DATA.value = bit_raw
                HC595_CLOCK.value = True
                HC595_CLOCK.value = False
    def _latch(self):
        """Latch the shift register output."""
        HC595_LATCH.value = True
        HC595_OE.value = True
        
    
    def _parse_matrix(self, row):
        #Get the data and convert it to chunks of 8, with the colors vertically aligned
        formatted_rgb =[]
        # A row is actually 2 rows, the first row is the one requested, and the second one is row + 6
        #row -=1
        #print(f"GRABBING row {row}, {row + 6}")
        rows = self.led_matrix_rgb[row]  + self.led_matrix_rgb[row + 6][8:] + self.led_matrix_rgb[row + 6][:8] # combine both rows into a single list and reorder the second row
        # Split the colors into their own lists
        led_row_red = [i[0] for i in rows]
        led_row_grn = [i[1] for i in rows]
        led_row_blu = [i[2] for i in rows]
        for a in range(int(len(led_row_red)/8)): # Find out how many times we need to split
            offset_start = a * 8
            offset_end = (a+1) * 8 # end of offset chunk
            #print(f"Offset: {offset_start} > {offset_end}")
            formatted_rgb.append(led_row_red[offset_start:offset_end])
            formatted_rgb.append(led_row_grn[offset_start:offset_end])
            formatted_rgb.append(led_row_blu[offset_start:offset_end])
        return formatted_rgb
        
    def set_led_by_coord(self, x_coord:int, y_coord:int, red:bool, green:bool, blue:bool, validate_coords:bool=False): 
        """Set a single LEDs color by coords (starts 0, 0).  Optionally, coordinates can be validated and return an error if an invalid coordinate is sent.

        Args:
            x_coord (int): X coordinate of LED
            y_coord (int): y coordinate of LED
            red (bool): Red LED on
            green (bool): Green LED on
            blue (bool): Blue LED on
            validate_coords (bool, optional): If invalid coordinate is sent, return an error. Defaults to False.
        """
        #TODO instead of setting RGB, just offer a choice of colors
        if x_coord > self.matrix_sixe_x or y_coord > self.matrix_sixe_y or x_coord < 0 or y_coord < 0: # Simple coordinate validation
            if validate_coords: 
                raise ValueError(f"Invalid Coordinates! The maximum value is X:{self.matrix_sixe_x},y:{self.matrix_sixe_y}")
            else:
                return None
        
        # At this point only valid coords should be possible.
        # 1 = LED off, 0 = LED on.  It seems to crash alot less with this.  I think this can be flipped with the OE pin, but I need to test more
        self.led_matrix_rgb[y_coord][x_coord] = [0 if green == True else 1, 0 if red == True else 1, 0 if blue == True else 1] # The colors are sent as GRB, idk why


    def create_grid(self): # Create the grid once
        self.row_data = {}
        for row in range(6): # Prep data all at once, may help with stutter
            self.row_data[row] = self._parse_matrix(row)
        
        return self.row_data

    def update_matrix(self, static=False): # Update the actual LED Matrix
        """Update the LED matrix with new data"""
        if static: # If using a static image/dataset, skip creating the grid again.  Speeds up the process a bit, should hopefully reduce flicker
            row_data = self.row_data
        else:
            row_data = {}
            for row in range(6): # Prep data all at once, may help with stutter
                row_data[row] = self._parse_matrix(row)
        
        for row in range(6): #6 rows to cycle through (each row is 2 rows of LEDs)
            
            set_row(row+1) # Remember that each row is actually 2 rows
            time.sleep(0.002) # 0.002 seems to be the sweet spot of making it look solid and still letting the data changes register
            HC595_OE.value = False # Must be within row, the higher it is, the brighter the LEDs
            self._send_data_to_controllers(row_data[row])
            
            self._latch() # This locks in (and hopfully displays) the LEDs
            
            reset_row() # May not be needed
            
    def reset_matrix(self): # set ALL LEDs for off, might be too slow
        set_row(7)
        self.led_matrix_rgb = [[[1,1,1] for _ in range(self.matrix_sixe_x+1)] for _ in range(self.matrix_sixe_y + 1)]
        self.update_matrix()

          
    def is_button_pressed(self, threshold:int=5): #INCOMPLETE, will return X and Y of the button being pressed
        #TODO add additional verification by confirming the value is above 30,000 but not between 53700 and 54000 (Roughly the value if LATCH is True)
        #TODO grab the current values of both the LEDs and latch/OE and set them back once the check is completed
        
        HC595_LATCH.value = False
        HC595_OE.value = False
        button_rows = [BTN1_7, BTN2_8, BTN3_9, BTN4_10, BTN5_11, BTN6_12]
        threshold = threshold # How many loops should the button be pressed before we consider it a true positive
        for row_num, button_row in enumerate(button_rows):
            debug_string = f"[ROW {row_num} VALUE {button_row.value}]: "
            #print(debug_string, "CHECKING")
            if button_row.value > 30000: # Value should be 2819 when not pressed, and above 30,000 if a single button is pressed
                
                if self.btn_pressed_counts[row_num] >= threshold: # Button has been pressed for longer than threshold
                    #print(debug_string, "PRESSED, ABOVE THRESHOLD")
                    
                    coords = self._button_press_finder(button_row,row_num)
                    if coords != False: # Will either be the coordinate, or false
                        #print(debug_string, f"FOUND LOCATION {coords}")
                        return coords
                    else: # No coord being returned means button isn't pressed anymore
                        self.btn_pressed_counts[row_num] = 0
                        
                else:
                    #print(debug_string, f"PRESSED BUT BELOW THRESHOLD {self.btn_pressed_counts[row_num]}")
                    self.btn_pressed_counts[row_num] += 1
                
            else: # Reset row back to zero if button isn't pressed
                self.btn_pressed_counts[row_num] = 0 
        
        return False
                
    def _button_press_finder(self, button_analog, pressed_row): # Will send 24 red LEDs one at a time to each LED in the selected row(s) to find the X coordinate
        self.reset_matrix()
        for x in range(24):
            HC595_LATCH.value = False
            HC595_OE.value = False
            
            y = pressed_row
            
            if x > 11:
                y += 6 # Offset!
                x-=12
            
            
            #if button_row.value < 30000: # Button has been released while we were looking, so return False
                #print('BTNFIND - NO LONGER PRESSED (midway)')
                #return False
            #print(f"SETTING {x},{y}")
            #self.led_matrix_rgb = self.blank_matrix.copy()
            matrix.set_led_by_coord(x,y,True,False,False)
            
            row_data = self._parse_matrix(pressed_row) # This should save time
            
            #time.sleep(0.002) # 0.002 seems to be the sweet spot of making it look solid and still letting the data changes register
            self._send_data_to_controllers(row_data)
            self._latch()
            HC595_LATCH.value = False
            HC595_OE.value = False
            #print(f'BTNF - VAL {x}, {button_analog.value}')
            if button_analog.value < 30000: # Button has either been released or this is the one thats being held down
                #print(f'BTNF - POSSIBLE MATCH {x}, {button_analog.value}')
                
                set_row(7) # May not be needed
                matrix.reset_matrix()  # Reset the grid and check again
                #print(f'BTNF - POSSIBLE MATCH2 {x}, {button_analog.value}')
                time.sleep(0.002) # Hold for a second
                if button_analog.value > 30000: # Button value returned to a high level, so we can assume the button is being pressed
                    return (x, y) # Return the coordinate, plus true if the row should be offset by 6
        #print('BTNFIND - NO LONGER PRESSED (end)')
        return False # No coord found
        
            

    

# "each LED is spread across 3 shift registers at the same index"
matrix = TechDidntSaveUs()
#print("RUNNING!")
#matrix.reset_matrix()
while False: # Is the button being pushed? Yes?  Make a ring around it!
    button = matrix.is_button_pressed()
    if button != False: # Light of the 4 LEDs around the button
        i = 0
        matrix.reset_matrix()
        matrix.set_led_by_coord(button[0],button[1],False,True,False)
        matrix.set_led_by_coord(button[0]+1,button[1],False,False,True)
        matrix.set_led_by_coord(button[0]-1,button[1],False,False,True)
        matrix.set_led_by_coord(button[0],button[1]-1,False,False,True)
        matrix.set_led_by_coord(button[0],button[1]+1,False,False,True)
        matrix.create_grid()
        while i < 20: # I just wanna keep it lit up for a bit
            i+=1
            matrix.update_matrix(static=True)
            time.sleep(.02)

            
            


def simple_animation():
    global matrix
    
    pos_x = 0
    increase_x = True
    pos_y = 0
    increase_y = True
    move_count = 8
    while True:
        if move_count < 1:
            move_count = 8
            if increase_x and pos_x < 11:
                pos_x +=1
                
            elif increase_x and pos_x >= 11:
                increase_x = False
                pos_x -=1
                if increase_y and pos_y < 11:
                    pos_y+=1
                elif increase_y and pos_y >= 11:
                    increase_y = False
                    pos_y -=1
                elif not increase_y and pos_y > 0:
                    pos_y -=1
                elif not increase_y and pos_y <= 0:
                    increase_x = True
                    pos_y +=1
                
            elif not increase_x and pos_x > 0:
                pos_x -=1
            elif not increase_x and pos_x <= 0:
                increase_x = True
                pos_x +=1
                pass
            
            matrix.reset_matrix()
            matrix.set_led_by_coord(pos_x,pos_y,False,True,True)
        else:
            move_count -=1
            
        matrix.update_matrix()
    
#simple_animation()
if True:
    
    
    grid = [
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [1,1,1,1,1,0,0,1,0,0,1,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [1,0,0,0,1,0,0,1,0,0,0,0],
    [1,0,0,0,1,0,0,1,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0]]
    
    for y_coord, x_coords in enumerate(grid):
        for x_coord, led in enumerate(x_coords):
            if led:
                matrix.set_led_by_coord(x_coord,y_coord,False,False,True)
        
    matrix.create_grid()
    while True:
        matrix.update_matrix(static=True)
        time.sleep(0.005)
        HC595_LATCH.value = False
        HC595_OE.value = False
        