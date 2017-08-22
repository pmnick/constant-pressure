from Tkinter import LabelFrame, Frame, Button, Entry, W, N, Menu, Toplevel, Label, StringVar
from modules.gui.graphs import TimeGraph
from modules.gui.indicators import LightIndicator, TextIndicator
from pdb import set_trace as debugger

def placeholder():
    pass

class UserInterface(Frame, object):
    def __init__(self, parent):
        super(UserInterface, self).__init__(parent)
        self.parent = parent
        # Menu
        self.menu = Menu(parent)
        self.parent.config(menu=self.menu)
        # Docs Menu
        self.doc_menu = Menu(self.menu)
        self.menu.add_cascade(label="Documentation", menu=self.doc_menu)
        self.doc_menu.add_command(label="TBD", command=placeholder)
        # Settings Menu
        self.settings_menu = Menu(self.menu)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Calibrate Pressure", command=placeholder)

        # Panel items
        self.panel = Frame(self)

        self.controls = ControlPanel(self.panel, self)
        self.controls.grid(row=0, column=0, sticky=W)

        self.indicators = IndicatorPanel(self.panel, self)
        self.indicators.grid(row=1,  column=0, sticky=W)

        # Top Level Layout
        self.graph = TimeGraph(self)
        self.graph.grid(row=0, column=0)
        self.panel.grid(row=0, column=1, sticky=N)

    def callback_end(self):
        pass

class IndicatorPanel(LabelFrame, object):
    def __init__(self, parent, master, text="Indicators", padx=5, pady=5, bg='white'):
        super(IndicatorPanel, self).__init__(parent, text=text, padx=padx, pady=pady, bg=bg)
        self.parent = parent
        self.master = master
        self.direction = ''

        self.pressure_ind = TextIndicator(self, 'Pressure (mbar): ', '--')
        self.pressure_ind.grid(row=0, sticky=W)

        self.pressure_setpoint_ind = TextIndicator(self, 'Pressure Setpoint: ',
                                                   self.master.controls.pressure_setpoint)
        self.pressure_setpoint_ind.grid(row=1, sticky=W)

        self.table = Frame(self)
        self.table.grid(row=2)

        # table header
        l1 = Label(self.table, text='Controller\nOutput')
        l1.grid(row=0, column=1)

        l2 = Label(self.table, text='Pump\nFeedback')
        l2.grid(row=0, column=2)

        # row 1
        l3 = Label(self.table, text='Pump Running')
        l3.grid(row=1, column=0)


        self.pump_running_output_ind = LightIndicator(self.table)
        self.pump_running_output_ind.grid(row=1, column=1)

        self.pump_running_input_ind = LightIndicator(self.table)
        self.pump_running_input_ind.grid(row=1, column=2)

        # row 2
        l4 = Label(self.table, text='Pump Direction')
        l4.grid(row=2, column=0)

        self.pump_direction_output_ind = TextIndicator(self.table, '', 'initializing')
        self.pump_direction_output_ind.grid(row=2, column=1, sticky=W)

        self.pump_direction_input_ind = TextIndicator(self.table, '', 'initializing')
        self.pump_direction_input_ind.grid(row=2, column=2, sticky=W)

class ControlPanel(LabelFrame, object):
    '''Container for control features
        Control features currently consist of:
        - pump enable/disable
        - setting the target pressure (setpoint)
    '''
    def __init__(self, parent, master, text="Control Panel", padx=5, pady=5, bg='white'):
        super(ControlPanel, self).__init__(parent, text=text, padx=padx, pady=pady, bg=bg)
        self.pump_enabled = False
        self.pressure_setpoint = 0
        self.parent = parent
        self.master = master

        self.enable_button = Button(self, text="Enable Pump", command=self.toggle_pump)
        self.enable_button.grid(row=0, column=0, sticky=W)

        self.enable_ind = LightIndicator(self)
        self.enable_ind.grid(row=0, column=1)

        self.set_pressure_button = Button(self, text="Set Pressure", command=self.update_setpoint)
        self.set_pressure_button.grid(row=1, column=0, columnspan=2, sticky=W)

    def toggle_pump(self):
        '''Switches the pump entire control process on and off'''
        self.pump_enabled = not self.pump_enabled
        self.enable_ind.set_state(self.pump_enabled)

    def pump_on(self):
        self.pump_enabled = True
        self.enable_ind.set_state(self.pump_enabled)

    def pump_off(self):
        self.pump_enabled = False
        self.enable_ind.set_state(self.pump_enabled)

    def update_setpoint(self):
        self.sp_dialog = PopupWindow(self, self.master,
                                     desc='Enter a new pressure setpoint in mbar:',
                                     confirm_text='update')
        #debugger()
        x = self.master.winfo_width() / 2 + self.master.winfo_x()
        y = self.master.winfo_y()
        w = 250
        self.sp_dialog.top.geometry("%dx%d+%d+%d" % (w, 100, x - w/2 , y))
        self.parent.wait_window(self.sp_dialog.top)
        value = self.sp_dialog.value
        if value:
            try:
                self.pressure_setpoint = int(value)
            except ValueError as error:
                pass
        self.master.indicators.pressure_setpoint_ind.set_value(self.pressure_setpoint)
        self.master.graph.update_setpoint(self.pressure_setpoint)

class PopupWindow(object):
    def __init__(self, parent, master, **kwargs):
        if 'desc' not in kwargs:
            kwargs['desc'] = 'Enter a value: '
        if 'confirm_text' not in kwargs:
            kwargs['confirm_text'] = 'Submit'

        # create the inteface
        self.top = Toplevel(master)
        self.label = Label(self.top, text=kwargs['desc'])
        self.label.grid(row=0)
        self.entry = Entry(self.top)
        self.entry.focus()
        self.entry.grid(row=1)
        self.submit_button = Button(self.top, text=kwargs['confirm_text'], command=self.submit)
        self.submit_button.grid(row=2)
        self.top.grab_set()

        # specify ending behavior
        self.top.protocol("WM_DELETE_WINDOW", self.exit)
        self.top.bind("<Return>", self.submit)
        self.top.bind("<Escape>", self.exit)

    def submit(self, *args):
        if self.entry.get():
            self.value = self.entry.get()
        else:
            self.value = None
        self.top.destroy()

    def exit(self, *args):
        self.value = None
        self.top.destroy()
