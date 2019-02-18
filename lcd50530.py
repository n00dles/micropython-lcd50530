import utime
import machine

class LCD50530:

    # Full commands
    LCD_NOOP = 0x00
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x03

    # Partial commands (with flags)
    LCD_BLINKFREQSET = 0x04		# with flags
    LCD_WRITERAMULINESET = 0x08	# with flags
    LCD_UNDERLINEMODESET = 0x0C	# with flags
    LCD_SHIFTCOMMAND = 0x10		# with flags
    LCD_DISPLAYMODESET = 0x20		# with flags
    LCD_ENTRYMODESET = 0x40		# with flags
    LCD_FUNCTIONMODESET = 0xC0	# with flags

    # LCD_SETCGRAMADDR 0x40
    # LCD_SETDDRAMADDR 0x80

    # flags for function mode set
    LCD_8BITMODE = 0x20
    LCD_4BITMODE = 0x00
    LCD_4LINE = 0x08
    LCD_2LINE = 0x04
    LCD_1LINE = 0x00
    LCD_5x12DOTS = 0x00
    LCD_5x8DOTS = 0x10
    LCD_160CHAR = 0x03
    LCD_192CHAR = 0x02
    LCD_224CHAR = 0x01
    LCD_256CHAR = 0x00

    # TODO: RAM -- setting region (page 28/29 of datasheet)

    # flags for display set entry mode
    LCD_DISPLAYMOVEREAD = 0x01	# Update display address after reading RAM data
    LCD_DISPLAYMOVEWRITE = 0x02	# Update display address after writing RAM data
    LCD_CURSORMOVEREAD = 0x08		# Update cursor address after reading RAM data
    LCD_CURSORMOVEWRITE = 0x10	# Update cursor address after writing RAM data


    LCD_DISPLAYMOVERIGHT = 0x00	# Display address decremented after instruction
    LCD_DISPLAYMOVELEFT = 0x04	# Display address incremented after instruction
    LCD_CURSORMOVELEFT = 0x20		# Cursor address decremented after instruction
    LCD_CURSORMOVERIGHT = 0x00	# Cursor address incremented after instruction

    LCD_LEFT	= 0x04
    LCD_RIGHT	= 0x00
    LCD_READ	= 0x01
    LCD_WRITE	= 0x02

    # flags for display on/off control
    LCD_DISPLAYON = 0x10		# Turn all displays on
    LCD_DISPLAYOFF = 0x00		# Turn all displays off
    LCD_CURSORON = 0x08		# Turn on cursor display
    LCD_CURSOROFF = 0x00		# Turn off cursor display
    LCD_UNDERLINEON = 0x04	# Turn on underline display
    LCD_UNDERLINEOFF = 0x00	# Turn off underline display
    LCD_CURSORBLINKON = 0x02	# Blinking cursor display
    LCD_CURSORBLINKOFF = 0x00	# Cursor display without blinking
    LCD_CHRBLINKON = 0x01		# Blinking Character display of cursor position
    LCD_CHRBLINKOFF = 0x00	# Character display without blinking
    
    # flags for display/cursor shift command
    LCD_DISPLAYSHIFT = 0x02
    LCD_CURSORSHIFT = 0x08
    LCD_SHIFTLEFT = 0x01
    LCD_SHIFTRIGHT = 0x00

    _ioc1_pin = 0 # 0: command.  1: character.
    _ioc2_pin = 0 # 0: command.  1: character.
    _rw_pin = 0   # 0: write to LCD.  1: read from LCD.
    _ex_pin = 0   # activated by a 1 pulse.
    _data_pins = [0,0,0,0] 

    _functionmode = 0
    _displaymode = 0 
    _entrymode = 0

    _initialized = 0

    _numlines = 0 
    _currline = 0
    _cols = 0

    #lcd = LCD50530(15,5,4,0,2,14,12,13)
    def __init__(self,ioc1, ioc2, rw, ex, d4, d5, d6, d7):
        self._ioc1_pin = ioc1
        self._ioc2_pin = ioc2
        self._rw_pin = rw
        self._ex_pin = ex
        
        self._data_pins[0] = d4
        self._data_pins[1] = d5
        self._data_pins[2] = d6
        self._data_pins[3] = d7 

        self.setDDRD(0b11111111)

        #DDRD = B11111111     # Default: Set all ports to output (Atmel shortcut)    

        print (self._data_pins)

    def setDDRD(self,state):  
        if (state & 128):
            print("pin 8 out")
            self.ioc1 = machine.Pin(self._ioc1_pin, machine.Pin.OUT)
        else: 
            self.ioc1 = machine.Pin(self._ioc1_pin, machine.Pin.IN)
        
        if (state & 64):
            print("pin 7 out")
            self.ioc2 = machine.Pin(self._ioc2_pin, machine.Pin.OUT)
        else:
            self.ioc2 = machine.Pin(self._ioc2_pin, machine.Pin.IN)

        if (state & 32):
            print("pin 6 out")
            self.rw = machine.Pin(self._rw_pin, machine.Pin.OUT)
        else: 
            self.rw = machine.Pin(self._rw_pin, machine.Pin.IN)

        if (state & 16):
            print("pin 5 out")
            self.ex = machine.Pin(self._ex_pin, machine.Pin.OUT)
        else: 
            self.ex = machine.Pin(self._ex_pin, machine.Pin.IN)

        if (state & 8):
            print("pin 4 out")
            self.data1 = machine.Pin(self._data_pins[0], machine.Pin.OUT)
        else: 
            self.data1 = machine.Pin(self._data_pins[0], machine.Pin.IN)

        if (state & 4):
            print("pin 3 out")
            self.data2 = machine.Pin(self._data_pins[1], machine.Pin.OUT)
        else: 
            self.data2 = machine.Pin(self._data_pins[1], machine.Pin.IN)

        if (state & 2):
            print("pin 2 out") 
            self.data3 = machine.Pin(self._data_pins[2], machine.Pin.OUT)
        else: 
            self.data3 = machine.Pin(self._data_pins[2], machine.Pin.IN)

        if (state & 1):
            print("pin 1 out")
            self.data4 = machine.Pin(self._data_pins[3], machine.Pin.OUT)
        else: 
            self.data4 = machine.Pin(self._data_pins[3], machine.Pin.IN)

    def setPORTD(self,state ):  
        if (state & 128):
            self.ioc1.value(1)
        else: 
            self.ioc1.value(0)
        
        if (state & 64):
            self.ioc2.value(1)
        else:
            self.ioc2.value(0)

        if (state & 32):
            self.rw.value(1)
        else: 
            self.rw.value(0)

        if (state & 16):    
            self.ex.value(1)
        else: 
            self.ex.value(0)

        if (state & 8):
            self.data1.value( 1)
        else: 
            self.data1.value(0)


        if (state & 4):
            self.data2.value(1)
        else: 
            self.data2.value(0)

        if (state & 2): 
            self.data3.value(1)
        else: 
            self.data3.value(0)

        if (state & 1):
            self.data4.value(1)
        else: 
            self.data4.value(0)


    def begin(self,cols, lines, dotsize = 0x10): 
        totalChar = cols*lines

        displaySize = 0x00
        
        if(lines <= 1):
            displaySize |= self.LCD_1LINE
        elif (lines == 2):
            displaySize |= self.LCD_2LINE
        else:
            displaySize |= self.LCD_4LINE
        
        if(totalChar <= 160):
            displaySize |= self.LCD_160CHAR
            _cols = 160/lines
        elif(totalChar <= 192):
            displaySize |= self.LCD_192CHAR	
            _cols = 192/lines	
        elif(totalChar <= 224):
            displaySize |= self.LCD_224CHAR 
            _cols = 224/lines	
        else: # 256 characters - 
            displaySize |= self.LCD_256CHAR
            _cols = 256/lines
        

        _functionmode = self.LCD_4BITMODE | self.LCD_5x8DOTS | displaySize
        self.command(self.LCD_FUNCTIONMODESET | _functionmode) 
        
        _displaymode = self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYMODESET | _displaymode)


        _entrymode = self.LCD_CURSORMOVEWRITE | self.LCD_CURSORMOVERIGHT
        self.command(self.LCD_ENTRYMODESET | _entrymode) 
        
        self.command(self.LCD_CLEARDISPLAY) 

    def command(self,value):
        print(value)
        self.send(value, 0)

    def clear(self):
        self.command(self.LCD_CLEARDISPLAY)

    # set cursor position to zero
    def home(self):
        self.command(self.LCD_RETURNHOME)

    def send(self, value, controlpins):
        #while(self.busyState())
        self.write4bits(value, controlpins)
        self.write4bits(value<<4, controlpins)    

    def pulseExecute(self):
        self.ex.value(1)
        utime.sleep_us(2)
        self.ex.value(0)
        utime.sleep_us(2)

    def write4bits(self, value, controlpins):
        self.setPORTD(value & 0b11110000 | controlpins)
        self.pulseExecute()

    def busyState():
        state = 0
        #self.DDRD = 0b00001111 # Set data pins to input
        self.setDDRD(0b00001111)
        self.setPORTD(1<<self.rw.value())
        
        self.ex.value(1)
        utime.sleep_us(2)
        state = self.data3.value()
        self.ex.value(0)
        utime.sleep_us(2)
        
        self.setPORTD(1<<self.rw.value())
        
        self.ex.value(1)
        utime.sleep_us(2)
        state |= self.data3.value()

        self.ex.value(0)
        utime.sleep_us(2)
        self.setDDRD(0b11111111)
        #self.DDRD = B11111111  # Reset pins to output
        return state

#ioc1, ioc2, rw, ex, d4, d5, d6, d7

lcd = LCD50530(15,5,4,0,2,14,12,13)
lcd.begin(40,3,1)
lcd.clear()
lcd.home()
