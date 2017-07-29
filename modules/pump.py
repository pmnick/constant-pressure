#   RESEARCH FIRST:
    # When should something be a property vs. a method?
    # How to run unit tests? (this will require mock)

# the phd4400 pump should have the interface:

    # Enable/Disable or on/off (if off, start will not work)

    # start - method
    # stop - method
    # is_started - property
        # this returns whether the pump is set to run or not, not what it's actually doing
    # running_indicator (return true if running indicator true, false if running indicator false)
        # this is a signal from the pump, not the control setting

    # infuse - method
    # withdraw (refill) - method
    # direction - property
        # this is the direction it is set to, not what it's actually doing
    # direction_indicator - property
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
        # scrolling_line_graph
        # indicators
        # label
        # pressure_sensor
