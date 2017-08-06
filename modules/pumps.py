import RPi.GPIO as GPIO


class Phd4400(object):
    '''Simple interface for operating with the Phd4400 syringe pump

    The expected inputs and their function are detailed in the pump manual here:
    http://www.harvardapparatus.com/media/harvard/pdf/702200_Syringe%20Pump_PHD_4400_Manual.pdf
    see appendix I

    Communication is not serial, each pin either receives or indicates using a high or low voltage
    (or a transition between such). To prevent any missed events, the controller module should
    check the indicator value to detect if the desired output succeeded each cycle. If it did not,
    the desired pump control methods should be called again. This is left to the controller and
    ommitted here to prevent random delays in the data collection cycle as this module would have to
    retain control until the pump successfully switched states and indicated the same.

    As a more general statement of the preceeding discussion, all control logic should remain
    in the control module. The purpose of this module is strictly to provide an interface to
    execute control logic.

    Upon initialization, the pump will be disabled, the running status set to false, and the
    direction set to withdraw (refill).
    '''
    # This convention is specific to this pump, and makes comparing the values
    # received from the direction indicator pin more convenient.
    INFUSE = False
    WITHDRAW = True
# the Phd4400 pump should have the interface:
    def __init__(self, running_control_pin,
                        running_indicator_pin,
                        direction_control_pin,
                        direction_indicator_pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.running_control_pin = running_control_pin
        GPIO.setup(running_control_pin, GPIO.OUT, initial=GPIO.LOW) # pump control

        self.running_indicator_pin = running_indicator_pin
        GPIO.setup(running_indicator_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.direction_control_pin = direction_control_pin
        GPIO.setup(direction_control_pin, GPIO.OUT)

        self.direction_indicator_pin = direction_indicator_pin
        GPIO.setup(direction_indicator_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.enabled = False
        self.direction = self.WITHDRAW
        self.stop()

        if self.direction == self.INFUSE:
            self.withdraw()

    # Enable/Disable or on/off (if off, start will not work)
    def start(self):
        '''Activate the pump if enabled and not running. If already running, do nothing. '''
        if self.enabled and not self.is_started:
            # check if previous signal was missed, cycle voltage to reset if needed
            if GPIO.input(self.running_control_pin) == GPIO.HIGH:
                GPIO.output(self.running_control_pin, GPIO.LOW)
            GPIO.output(self.running_control_pin, GPIO.HIGH)

    def stop(self):
        '''Deactivate the pump. If already off, do nothing. '''
        if self.is_started:
            # check if previous signal was missed, cycle voltage to reset if needed
            if GPIO.input(self.running_control_pin) == GPIO.LOW:
                GPIO.output(self.running_control_pin, GPIO.HIGH)
            GPIO.output(self.running_control_pin, GPIO.LOW)

    @property
    def is_started(self):
        '''Return running status according to the pump'''
        return GPIO.input(self.running_indicator_pin) == GPIO.HIGH

    def infuse(self):
        '''Switch pump direction to infuse. If the direction is already infuse, do nothing.'''
        if self.direction == self.WITHDRAW:
            if GPIO.input(self.direction_control_pin) == GPIO.HIGH:
                GPIO.output(self.direction_control_pin, GPIO.LOW)
            GPIO.output(self.direction_control_pin, GPIO.HIGH)

    def withdraw(self):
        '''Switch pump direction to withdraw. If the direction is already withdraw, do nothing.'''
        if self.direction == self.INFUSE:
            # check if previous signal was missed, cycle voltage to reset if needed
            if GPIO.input(self.direction_control_pin) == GPIO.LOW:
                GPIO.output(self.direction_control_pin, GPIO.HIGH)
            GPIO.output(self.direction_control_pin, GPIO.LOW)

    @property
    def direction(self):
        '''Return pump direction according to the pump'''
        return GPIO.input(self.direction_indicator_pin) == GPIO.HIGH

    def print_gpio(self):
        '''For debugging purposes, print all current pin values.'''
        print "pump running control pin: %s" % GPIO.input(self.running_control_pin)
        print "pump running ind pin: %s" % GPIO.input(self.running_indicator_pin)
        print "pump direction control pin: %s" %GPIO.input(self.direction_control_pin)
        print "pump direction ind pin: %s" % GPIO.input(self.direction_indicator_pin)


    # start - method
    # stop - method
    # is_started - property
        # this returns whether the pump is set to run or not, not what it's actually doing
    # running_indicator (return true if running indicator true, false if running indicator false)
        # this is a signal from the pump, not the control setting

    # infuse - method
    # withdraw (refill) - method
    # direction - property
        # this is a signal from the pump, not the control setting

    # proprties (for GPIO) these are required arguments for setup
        # running_control_pin
        # running_indicator_pin
        # direction_control_pin
        # direction_indicator_pin

    # dubugging tools... (print all gpio settings e.g. current pin readings
    # define withdraw, infuse convention at top in doc string, also include how all pins work from
        # pump manual appendix I and link.

# some other quick notes:
    # what other classes should be abstracted?
        # ScrollingLineGraph
            # change pop(0) to using collections.deque with popleft and append... this is much faster
        # Indicators
        # Label
        # PressureSensor
        # remove flow sensor for now... it would also logically be it's own class
