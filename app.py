import math
from Tkinter import Tk, Menu, LabelFrame, Button, W
from modules.graphs import TimeGraph
from modules.indicators import LightIndicator, TextIndicator

''' documentation:
        - instructions on priming
        - how to start he system
        - notes on setting speed of syringe pump

 '''

def callback():
    print "called the callback!"

def cycle_pump_enable():
    global enable_pump
    enable_pump = not enable_pump
    enable_ind.set_state(enable_pump)
    if enable_pump == False:
        pump_direction_ind.set_value('disabled')
    else:
        pump_direction_ind.set_value('normal')

root = Tk()
value = 0


# create a menu
menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=callback)
filemenu.add_command(label="Open...", command=callback)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=callback)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=callback)

graph = TimeGraph(root)

# Control Panel
enable_pump = False
control_panel = LabelFrame(root, text="Control Panel", padx=5, pady=5)
control_panel.pack()
enable_button = Button(control_panel, text="Enable Pump", command=cycle_pump_enable)
enable_button.pack()
enable_button.grid(row=0, column=0, sticky=W)
enable_ind = LightIndicator(control_panel)
enable_ind.pack()
enable_ind.grid(row=0, column=1)
pump_direction_ind = TextIndicator(control_panel, "Pump Direction", "test value")
pump_direction_ind.pack()
pump_direction_ind.grid(row=1, column=0, columnspan=2, sticky=W)

# final layout
graph.canvas.grid(row=0, column=0)
control_panel.grid(row=0, column=1)



def refresh_graph():
    global value
    graph.next(math.sin(value) * 120)
    value += .1
    root.after(50, refresh_graph)

root.after(50, refresh_graph)
root.mainloop()
