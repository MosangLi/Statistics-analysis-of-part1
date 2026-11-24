'''
==========================================================================
MPHY0044 - REACTION TIME LAB

Aim of the code:
Run experiment 1 as defined in the lab handout
Pilar's notes: It works. It is easy to define how many stimulus or ticks we
want to have, but it gives "holes" in the data.
=========================================================================
'''

# Import libraries
#====================
from time import sleep_ms, ticks_ms
from machine import Pin, ADC
import random

memory_set = ["1010", "0110"]
distractor_set = ["0000", "0001", "0010", "0011", "0100", "0101", "0111", "1000", "1001", "1011", "1100", "1101", "1110", "1111"]

# Define general variables
# ============================
N_data = 800 # Total number of readings in the experiment
N_data_per_cycle = 100 # Total number of readings for each tick cycle
delta_t= 50 # Time in between readings, given in milliseconds
N_stimulus1 = 3 # Total number of ticks in the force sensor1 expected from volunteer
time_start= ticks_ms() # Time at the start of running the code
F_threshold = 50 # Threshold that indicates when a force sensor has been touched (obtained from earlier)

#Define temporal variables


#Define the LEDs and force sensors according to their pin numbers
# ===============================================
#LEDs start from left to right (LEDs 1-4) and then the LED in the second row (LED5).
# Force sensors start from left to right (sensor 1-4).

led1 = Pin(10, Pin.OUT)  # Colour = Red
led2 = Pin(9, Pin.OUT)  # Colour = Yellow
led3 = Pin(26, Pin.OUT)  # Colour = Green
led4 = Pin(25, Pin.OUT)  # Colour = Blue
led5 = Pin(27, Pin.OUT)   # Colour = White

# ADC force sensors, from the Analogue to Digital pins (IN order).
sensor1 = ADC(Pin(36))
sensor2 = ADC(Pin(39))
sensor3 = ADC(Pin(34))
sensor4 = ADC(Pin(35))

# Controlling the LEDs : Count down from 4
# =========================================
#Note:
#LED.value(0) sets the LED to OFF
#LED.value(1) sets the LED to ON

# Set all LEDs to OFF
led1.value(0)
led2.value(0)
led3.value(0)
led4.value(0)
led5.value(0)
sleep_ms(1000) #delay of 1000ms = 1s

# Set up count down for data recording. LEDs 1 to 4 switch ON one at the time 
# in intervals of 1 second. Then LED 5 goes ON, and the recording start.

led1.value(1)
sleep_ms(1000)
led2.value(1)
sleep_ms(1000)
led3.value(1)
sleep_ms(1000)
led4.value(1)
sleep_ms(1000)


led1.value(0)
led2.value(0)
led3.value(0)
led4.value(0)
led5.value(1) #Indicate that recording starts by switching LED5 ON
sleep_ms(1000)


# Experimental protocol for data collection
# ==========================================

#Set up temporal variables
time_of_trigger = 0 # Time at which a trigger occurs (LED1 turns ON)
time_of_reaction = 0 # Time at which the reaction occurs (volunteer first touches sensor 1)
reaction_time = 0 # Time from trigger to start of reaction


# Main loop, running data collection for the desired number of ticks in sensor 1 (N_ticks1)
for n in range(1, N_stimulus1+1):
    tick_ON = False # Binary parameter. Indicates if the sensor 1 has been touched (value =TRUE) or not (value =FALSE). In every iteration we start it as FALSE
    
    led1.value(1) # This is the triger for the volunteer to press the sensor 1
    time_of_trigger = ticks_ms() - time_start # Time at which the trigger took place
    choice = random. randint(a, b)
    # Second loop for data collection
    for i in range(1, N_data_per_cycle):
        
        sensor1_value = sensor1.read() # Read sensor value
                
        timestamp = ticks_ms() - time_start # Time since boot (in ms)

        # Format data string to record data
        #------------------------------------------
        # One row of data contains: (N_cycle, i or datapoint, timestamp, Sensor1, Led1)
        data = (
            f"{n}, {i}, {timestamp}, {sensor1_value}, {led1.value()}"
        )

        # Log and print data
        print(data) #This prints the row of data in the Shell screen
        #------------------------------------------------
        
        # Check if the sensor has been touched for first time since the trigger,
        # and record the time when this happened
        #------------------------------------------------------------------------------
        if ((sensor1_value >= F_threshold) and (tick_ON == False)):
            time_of_reaction = timestamp
            reaction_time = time_of_reaction - time_of_trigger
            print(f"Reaction time for trigger {n}= {reaction_time} ms")
            tick_ON = True
        #------------------------------------------------------------------------------
            
        sleep_ms(delta_t)
        
    led1.value (0)
    sleep_ms(3000) # Leave 3 seconds gap between triggers

#Indicate that recording stops
led5.value(0)

