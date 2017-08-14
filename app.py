from Tkinter import *
from modules.graphs import TimeGraph
import math
import datetime

def callback():
    print "called the callback!"

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

#graph = TimeGraph(root, ymin=-31, ymax=-30)
graph = TimeGraph(root)


def refresh_graph():
    global value
    graph.next(math.sin(value) * 120)
    value += .1
    root.after(50, refresh_graph)

root.after(50, refresh_graph)
root.mainloop()
