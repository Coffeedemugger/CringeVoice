from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import framebuf
import math
import utime
import uasyncio as asyncio
import threading
import struct


class Sample:
    def __init__(self):
        """
        Set up the timer interrupt for the sampling. In the IRQ
        it will check if global bool 'rec' is True, and if
        it is it records analog samples in a buffer.
        """
        # Set up timer to trigger ADC sampling at 44.1 kHz
        sampling_rate = 8000  # Hz
        buffer_size = 4000
        self.samples = bytearray(buffer_size * 2)  # store 12-bit samples as 2 bytes
        self.sample_index = 0
        
        # Define the coroutine function to be called when the timer fires
        async def timer_interrupt():
            while True:
                # Read the raw 16-bit value from the ADC
                raw_value = main.adc.read_u16()
                # Convert the raw value to a voltage
                sample = raw_value 
                # Add the new sample to the circular buffer
                self.samples[self.sample_index * 2] = (sample >> 8) & 0xFF  # high byte
                self.samples[self.sample_index * 2 + 1] = sample & 0xFF  # low byte
                self.sample_index = (self.sample_index + 1) % buffer_size
                # Wait for the next sampling interval
                await asyncio.sleep_ms(1000 // sampling_rate)
                
        # Create a new event loop and run it in a separate thread
        loop = asyncio.new_event_loop()
        task = loop.create_task(timer_interrupt())
        
        


        def run_loop(loop):
            loop.run_until_complete(task)

        self.thread = threading.Thread(target=run_loop, args=(loop,))
        self.thread.start()
        
        
        
    def print_buffer(self):
        
        # Convert the 12-bit values to 16-bit integers by shifting the high byte 4 bits to the left
        # and OR-ing with the low byte
        sample_list = [(self.samples[i] << 4) | (self.samples[i+1] >> 4) for i in range(0, len(self.samples), 2)]

        # Unpack the 16-bit integers as a list of unsigned short integers
        sample_list = struct.unpack('>' + str(len(self.samples)//2) + 'H', self.samples)
        print(sample_list)
                
        
        
        
        
class MainWindow():
    
    def __init__(self):
        
        """
        Class Variables
        """
        self.menu_options = [
        self.sample,
        self.voice_modulator,
        self.test_speaker,
        ]
        
        
        self.show_sounds = False
        self.main_menu = True
        self.menu_choice = 0
            
            
            
        self.initiate_pins()
        self.start_OLED()
        self.sampler = Sample()
    

    """
    Set up the I2C pins and the ssd1306 display. It also will
    show a splash screen for 2 seconds. If you want to add something
    to take place during bootup, put it here. 
    """
    def start_OLED(self):
        sda=machine.Pin(12)
        scl=machine.Pin(13)
        i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
        from ssd1306 import SSD1306_I2C
        self.oled = SSD1306_I2C(128, 64, i2c)

        # Clear the oled display in case it has junk on it.
        self.oled.fill(0) # Black
        self.oled.text("DSPain",40,5)
        self.oled.text("Voice Modulator", 3,20)
        self.oled.text("Spring 2023",18,47)
        self.oled.show()

        utime.sleep(3)
        self.oled.fill(0) # Black
        self.oled.show()
        self.menu_options[0]()
        
        
        
    """
    Set up the other pins attached to the pico.
    The LED is on pin 4, and is on when driven low.
    The mic input is on analog pin 26, and the speaker
    output is on pin 28. 
    """
    def initiate_pins(self):
        # Set up LED on pin 4
        self.led_pin = machine.Pin(4, machine.Pin.OUT)
        self.led_pin.on()

        # Set up ADC on pin 26 for microphone
        self.mic_pin = machine.Pin(27)
        self.adc = machine.ADC(self.mic_pin)

        # Set up the speaker output
        self.spkr_pin = machine.Pin(28)
        
        # Set up button on pin 0
        self.button_pin = machine.Pin(0, machine.Pin.IN)
        self.button_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.button_pressed)
            


    

         
    """
    Set up the menu functions, for the different options for processing
    """
    def sample(self):
        if self.main_menu:
            self.oled.fill(0) # Black
            self.oled.text("Sample the Mic",10,5)
            self.oled.show()
        else:
            self.sampler.print_buffer()
            self.main_menu = True
            self.oled.text("Sent",50,35)
            self.oled.show()
            utime.sleep(.5)
            self.oled.text("Sent",50,35,0)
            self.oled.show()
            

            


    def voice_modulator(self):
        if self.main_menu:
            self.oled.fill(0) # Black
            self.oled.text("Modulator",28,5)
            self.oled.show()
        else:
            self.main_menu = True
        

    def test_speaker(self):
        if self.main_menu:
            self.oled.fill(0) # Black
            self.oled.text("Test Speaker",18,5)
            self.oled.show()
        else:
            self.main_menu = True





    

    """
    This block of code creates an interrupt attached
    to the button pin (GPIO0). When the button is pulled
    low, a timer measurement is made so that when it is
    released we have the overall length of the button press.
    Either the short or the long functions are called
    depending on the length.

    """
    # Define functions for short and long button presses
    def short_press(self):
        if self.main_menu:
            self.menu_choice+=1
            if 0 <= self.menu_choice < len(self.menu_options):
                
                self.menu_options[self.menu_choice]()
                
            else:
                self.menu_choice=0
                self.menu_options[self.menu_choice]()

    def long_press(self):
        if self.main_menu:
            self.oled.rect(1,1,126,62,1)
            self.oled.show()
            utime.sleep(.25)
            self.oled.rect(1,1,126,62,0)
            self.oled.show()
            self.main_menu = False
            self.menu_options[self.menu_choice]()
        else:
            self.oled.rect(1,1,126,62,1)
            self.oled.show()
            utime.sleep(.25)
            self.oled.rect(1,1,126,62,0)
            self.oled.show()
            self.main_menu = True
            self.menu_options[self.menu_choice]()

    # Define IRQ function for button press
    def button_pressed(self, pin):
        if not self.button_pin.value(): # Only start measuring if the button is low
            # Measure duration of button press
            start_time = utime.ticks_us()
            while not self.button_pin.value():
                pass
            end_time = utime.ticks_us()
            press_duration = utime.ticks_diff(end_time, start_time)
            # Call appropriate function based on press duration
            if 10000 < press_duration < 250000 :
                self.short_press()
            elif 250000 < press_duration < 1000000 :
                self.long_press()

    
    




"""
Main while loop to run the main menu
"""
if __name__ == '__main__':
    main = MainWindow()
    