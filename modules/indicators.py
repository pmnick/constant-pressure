from Tkinter import Label, Canvas, StringVar
from pdb import set_trace as debugger

class TextIndicator(Label, object):
    '''Provides a simple interface for working with labels that are updated frequently'''
    def __init__(self, parent, prefix, initial_value=""):
        self.parent = parent
        self.prefix = prefix
        self.value = StringVar()
        self.value.set('{}: {}'.format(prefix, initial_value))
        super(TextIndicator, self).__init__(parent, textvariable=self.value,
                                            padx=5, font=("Helvetica", 14))

    def set_value(self, new_value):
        self.value.set('{}: {}'.format(self.prefix, new_value))


class LightIndicator(Canvas, object):
    def __init__(self, parent, r=10, state='disabled'):
        # valid_states = ['normal', 'disabled', 'hidden']
        super(LightIndicator, self).__init__(parent, width=r * 2 + 2, height=r * 2 + 2)
        self.parent = parent
        self.r = r

        # create indicator
        self.light = self.create_oval(3, 3, r * 2 + 3, r * 2 + 3,\
            fill="green", disabledfill="red", state=state)

    def set_state(self, turn_on):
        if turn_on:
            self.itemconfig(self.light, state='normal')
        else:
            self.itemconfig(self.light, state='disable')
