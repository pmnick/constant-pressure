

class VirtualPhd4400(object):
    INFUSE = False
    WITHDRAW = True
# the Phd4400 pump should have the interface:
    def __init__(self, running_control_pin,
                 running_indicator_pin,
                 direction_control_pin,
                 direction_indicator_pin):

        # these should take place in the controller
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(False)
        # also gpio.cleanup should take place in the controller

        self.v_is_started = False
        self.v_direction = self.WITHDRAW

        self.running_control_pin = running_control_pin
        self.running_indicator_pin = running_indicator_pin
        self.direction_control_pin = direction_control_pin
        self.direction_indicator_pin = direction_indicator_pin

        self.stop()

        if self.direction == self.INFUSE:
            self.withdraw()


    def start(self):
        '''Activate the pump if enabled and not running. If already running, do nothing. '''
        if not self.is_started:
            self.v_is_started = True

    def stop(self):
        '''Deactivate the pump. If already off, do nothing. '''
        if self.is_started:
            self.v_is_started = False

    def set_running(self, run):
        '''Start pump if run is True, else stop'''
        self.start() if run else self.stop()

    @property
    def is_started(self):
        '''Read and return running status from pump'''
        return self.v_is_started

    def infuse(self):
        '''Switch pump direction to infuse. If the direction is already infuse, do nothing.'''
        if self.direction == self.WITHDRAW:
            self.v_direction = self.INFUSE

    def withdraw(self):
        '''Switch pump direction to withdraw. If the direction is already withdraw, do nothing.'''
        if self.direction == self.INFUSE:
            self.v_direction = self.WITHDRAW

    def set_direction(self, direction):
        self.infuse() if direction == self.INFUSE else self.withdraw()

    @property
    def direction(self):
        '''Read and return direction from pump'''
        return self.v_direction
