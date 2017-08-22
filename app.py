import math
from Tkinter import Tk
from modules.gui.interfaces import UserInterface
import numpy as np
from pdb import set_trace as debugger
#from modules.pumps import Phd4400
from modules.virtual_pumps import VirtualPhd4400

''' documentation:
        - instructions on priming
        - how to start he system
        - notes on setting speed of syringe pump

 '''

 # NEXT STEPS:
     # organize file structure and imports
     # create a virtual pump for testing
     # add shutdown protocols
     # test the system
     # write docs and add to the menu (just have func calls to open text files so others could modify them as desired)
     # add calibration features
     # implement with real system
         # setup GPIO
         # initialize pump
# Initialize UI

root = Tk()
ui = UserInterface(root)
ui.grid(row=0, column=0)

# temp values for mock
value = 1.0
previous_value = 1.0

#initialize GPIO here
pump = VirtualPhd4400(running_control_pin=17,
                      running_indicator_pin=22,
                      direction_control_pin=23,
                      direction_indicator_pin=24)

# Configuration settings
sample_period = 20 #milliseconds
refresh_period = 75
averaged_samples = 5
cumulative_pressure = np.zeros(averaged_samples)

def direction_to_text(direction):
    return 'withdraw' if direction == pump.WITHDRAW else 'infuse'

class State(object):
    '''Assess inputs and determine the state of the controller'''
    def __init__(self, pressure, setpoint, pump_enabled):
        self.run_pump = self._run_pump(pressure, setpoint, pump_enabled)
        self.pump_direction = pump.WITHDRAW if setpoint <= 0 else pump.INFUSE

    def _run_pump(self, pressure, setpoint, pump_enabled):
        if not pump_enabled: return False
        if setpoint > 0:
            return True if pressure < setpoint else False
        return True if pressure > setpoint else False

def mock_read_pressure():
    global value, pump
    if pump.is_started:
        if pump.direction == pump.INFUSE:
            value += 4.4
        else:
            value -= 4.4
    else:
        value += -6.7 if value > 0 else 6.7
    return value

def avg_pressure():
    global cumulative_pressure
    cumulative_pressure = np.append(cumulative_pressure[1:], mock_read_pressure())
    return np.average(cumulative_pressure)

def refresh():
    pressure = avg_pressure()
    ui.graph.next(pressure)
    ui.indicators.pressure_ind.set_value(round(pressure, 2))

    state = State(pressure, ui.controls.pressure_setpoint, ui.controls.pump_enabled)
    if state.run_pump != pump.is_started:
        pump.set_running(state.run_pump)
        ui.indicators.pump_running_output_ind.set_state(state.run_pump)
    ui.indicators.pump_running_input_ind.set_state(pump.is_started)

    if state.pump_direction != pump.direction:
        pump.set_direction(state.pump_direction)
        ui.indicators.pump_direction_output_ind.set_value(direction_to_text(state.pump_direction))
    ui.indicators.pump_direction_input_ind.set_value(direction_to_text(pump.direction))

    root.after(refresh_period, refresh)

root.after(refresh_period, refresh)
#root.after(sample_period, acquire_data)
root.mainloop()
