'''
Thoughts on graph interface:
    - all graphs
        - title
        - y range(min, max)
        - x range(min, max)
        - x,y dimensions
        - axes with labels
        - x grid lines
        - y grid lines
        - graphical display
        - data
        s

    - scrolling_line_graph
        - new value which causes scroll and update

    - parameters I should be able to set:
        -

    - what about compressing the data left-to-right?
        - is this exlicitly declared? Or is it inherently controlled by the width and the length of the
            data returned.

'''
from Tkinter import *
import numpy as np
from pdb import set_trace as debugger

# CONVERT TO ACTUAL INHERITANCE FROM CANVAS

class TimeGraph(object):
    '''Plots a scrolling line graph as each new datapoint is received'''
    def __init__(self, parent, width=450, height=500, ymin=-100, ymax=100, dt=-1, time_range=30):
        # dt and time_range both in seconds
        self.width = width
        self.axis_offset = 80 # region where y-axis labels are without any plotting
        self.plot_width = width - self.axis_offset
        self.height = height
        self.ymin = ymin
        self.ymax = ymax
        self.time_range = time_range
        if  dt < 0:
            self.dt = time_range / float(self.plot_width)
        data_length = int(time_range / self.dt)
        self.data_x = self._initial_x(data_length)
        self.data_y = np.zeros(data_length)
        self.setpoint = 0
        self.canvas = Canvas(parent, width=self.width, height=self.height)
        self.canvas.pack()

        # add initial elements to the canvas
        self.setpoint_line = self.canvas.create_line(0, 0, 1, 0)
        self.line = self.canvas.create_line(0, 0, 1, 0)

        self.update_y_axis()
        self.draw_setpoint()
        self.draw_line()

    def _initial_x(self, data_length):
        x = np.zeros(data_length)
        for i in range(0, data_length):
            x[i] = float(self.plot_width / data_length * i + self.axis_offset)
        return x

    def to_px(self, y):
        '''Converts value into pixels'''
        return self.height - (1.0 * y - self.ymin) / (self.ymax - self.ymin) * self.height

    def update_y_axis(self, increment=-1):
        '''Removes all from canvas and Plots y axis scale on graph'''
        if increment < 0:
            increment = (self.ymax - self.ymin) / 20.0
        self.canvas.delete(ALL)

        y = self.ymin
        while y < self.ymax:
            y_px = self.to_px(y)
            if y_px < self.height and y_px > 0:
                if y >= 0:
                    label = ' {0:.5g}'.format(y)
                else:
                    label = '{0:.5g}'.format(y)
                self.canvas.create_text(10, y_px, anchor=W, text=label)
                fill = 'gray1' if y == 0 else 'gray70'
                self.canvas.create_line(len(label) * 15, y_px, self.width, y_px, fill=fill)
            y += increment

        # add back other permanent features
        self.draw_setpoint()

    def draw_line(self):
        '''Draws data to canvas'''
        self.canvas.delete(self.line)
        xy_coords = np.reshape(np.column_stack((self.data_x, self.to_px(self.data_y))),
                               (1, self.data_x.shape[0] * 2))
        self.line = self.canvas.create_line(xy_coords[0].tolist(), smooth=True, fill="blue")

    def update_setpoint(self, value):
        self.check_range(value)
        self.setpoint = value
        self.draw_setpoint

    def draw_setpoint(self):
        '''Adds indication of setpoint to canvas'''
        self.canvas.delete(self.setpoint_line)
        self.setpoint_line = self.canvas.create_line(self.axis_offset, self.to_px(self.setpoint),
                                                     self.width, self.to_px(self.setpoint),
                                                     fill="red")

    def next(self, value):
        '''Delete oldest value and append new value to data array'''
        # TODO probably should track max and min and shrink the range
        # back down if a large spike has left the screen
        self.check_range(value)
        self.data_y = np.append(self.data_y[1:], value)
        self.draw_line()

    def check_range(self, value):
        if value > self.ymax:
            self.ymax = int(value + (self.ymax - self.ymin) * .05)
            self.update_y_axis()
        if value < self.ymin:
            self.ymin = int(value - (self.ymax - self.ymin) * .05)
            self.update_y_axis()
