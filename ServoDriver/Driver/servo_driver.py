import smbus2, time

class Servo_Driver():
    """
    This is for 0--180 deg micro servo
    based on Sparkfun Pi Hat driver board.
    tested on AdeeptAD002 and FS90 9g motor
    """
    _bus = smbus2.SMBus(1)
    _addr = 0x40
    def __init__(self) -> None:
        #the degree 180 and 0 val is tested for AdeeptAD002
        #other servo needs calibration.
        self.degree_180_val = 480
        self.degree_0_val = 100
        self.enable_chip(self._bus, self._addr)
        time.sleep(0.5)

    def test_ch(self, ch):
        if ch >= 0:
            while True:
                for y in range(180):
                    self.move_to(ch, y) # set 0, then 45, then 90 as y increments
                    time.sleep(0.05)
                time.sleep(2.5) # allow time to move to next channel during testing
                for z in range (180, -1, -1):
                    self.move_to(ch, z)
                    time.sleep(0.05)
                time.sleep(2.5)

    def enable_chip(self,bus=None, addr=None):
        if bus is not None and addr is not None:
            ## Running this program will move the servo to 0, 45, and 90 degrees with 5 second pauses in between with a 50 Hz PWM signal.
            bus.write_byte_data(addr, 0, 0x20) # enable the chip
            time.sleep(.25)
            bus.write_byte_data(addr, 0, 0x10) # enable Prescale change as noted in the datasheet
            time.sleep(.25) # delay for reset
            bus.write_byte_data(addr, 0xfe, 0x79) #changes the Prescale register value for 50 Hz, using the equation in the datasheet.
            bus.write_byte_data(addr, 0, 0x20) # enables the chip
    
    def move_to(self, channel, position):
        self.__set_servo(self._bus, self._addr,channel=channel,position=position)

    def __set_servo(self, bus, addr, channel, position):
        if bus is not None and addr is not None:
            #print("channel: " + str (channel) + "\t" + "position: " + str (position))
            #shift address to correct channel start and stop addresses
            start_addr = 0x06 + (4*channel)
            stop_addr = 0x08 + (4*channel)
            #print("start_addr: " + str (start_addr) + "\t" + "stop_addr: " + str (stop_addr))
            #convert position (degrees 0-180) to a fraction of the 5ms period, which can be 0-4095
            degree_180_val = 480
            degree_0_val = 100
            full_swing_difference = (degree_180_val - degree_0_val)
            # position comes in as 0 - 180, and this is a fraction of the full_swing_difference
            degree_offset_val = round(full_swing_difference * (position / 180 ))   
            position_val = (degree_0_val + degree_offset_val)
            #print("full_swing_difference: " + str (full_swing_difference) + "\t" + "degree_offset_val: " + str (degree_offset_val) + "\t" + "position_val: " + str (position_val))
            #write start and stop to channel
            bus.write_word_data(addr, start_addr, 0) # channel start time = 0us for all
            bus.write_word_data(addr, stop_addr, position_val) # channel stop time is a special position val calculated above

    def servo_example(self, bus, addr):
        bus.write_word_data(addr, 0x08, 100) # chl 0 end time = .0ms (0 degrees)
        time.sleep(1)
        bus.write_word_data(addr, 0x08, 250) # chl 0 end time = .50ms (90 degrees)
        time.sleep(1)
        bus.write_word_data(addr, 0x08, 350) # chl 0 end time = 1.0ms (135 degrees)
        time.sleep(1)
        bus.write_word_data(addr, 0x08, 480) # chl 0 end time = 1.5ms (180 degrees)               

# while 1:
#     for x in range(16):
#         for y in range(180):
#             set_servo(x, y) # set 0, then 45, then 90 as y increments
#             time.sleep(0.01)
#         time.sleep(5) # allow time to move to next channel during testing
#         for z in range (180, -1, -1):
#             set_servo(x, z)
#             time.sleep(0.01)  
#     #servo_example