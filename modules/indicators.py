from Tkinter import Label, Canvas, StringVar, Frame,W
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


class LightIndicator(Frame, object):
    def __init__(self, parent, r=10, text='', state='disabled'):
        # valid_states = ['normal', 'disabled', 'hidden']
        super(LightIndicator, self).__init__(parent)
        self.parent = parent
        # initialize label
        if text:
            self.value = StringVar()
            self.value.set(text)
            self.label = Label(self, textvariable=self.value, padx=5, font=("Helvietica", 14))
            self.label.pack()
            self.label.grid(row=0, column=0)

        # initialize indicator
        self.canvas = Canvas(self, width=r * 2 + 2, height=r * 2 + 2)
        self.canvas.pack()
        self.canvas.grid(row=0, column=1)
        self.r = r
        self.light = self.canvas.create_oval(3, 3, r * 2 + 3, r * 2 + 3,\
            fill="green", disabledfill="red", state=state)

    def set_state(self, turn_on):
        if turn_on:
            self.canvas.itemconfig(self.light, state='normal')
        else:
            self.canvas.itemconfig(self.light, state='disable')
