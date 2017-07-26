import RPi.GPIO as GPIO
from time import sleep
from Tkinter import *
import math
import time
import numpy as np
import spidev
from datetime import datetime, timedelta
import sys, os
from pdb import set_trace as debugger

#this is a test web edit

#To Do
## Make graph handle different ranges (pos and neg?)
## Add control of pump direction (using pin 8, rising edge sets infuse, falling edge sets refill
## Remove comments
## Check math on flow and pressure sensor (callibrate the pressure sensor
## fingernail polish pressure sensor so it doesn't get plugged in backwards
## order backup RPis
## order backup Differential op amps and ADCs
## Specify location of popup (for some reason its currently random)
#______________________________________________________________________________________________________________________
#----------------------------------------------------------------------------------------------------------------------


print("start")

#Setting up Global Variables
PressureSetpoint = 0 # mBar
PumpStatus = False # false = off, true = on
PumpControl = False

#-------------------------------- Initializations --------------------------------------
#Setting up Spi to read ADC
spi_0 = spidev.SpiDev()
spi_0.open(0, 0)  #the second number indicates which SPI pin CE0 or CE1
#to_send = [0x01,0x02,0x03] # speed Hz,Delay, bits per word
#spi_0.xfer(to_send)

#Setting up Global Variables
ForwardFlowCount = 0.0
oldForwardFlowCount= 0.0
forwardflow = 0.0
StartTime = datetime.now()
samplePeriod = 100  #milliseconds, time between data points written to txt file
minimumtime = 1000
destination = "/home/pi/Desktop/Data/"
tempFileName = "AutosavedData.txt"
# a=open(destination + tempFileName,'w') #a means append to existing file, w means overwrite old data
# a.write("\n\n"+ str(datetime.now()))
Average = 3 #number of samples over which the "show" variables will be averaged
flowshow = 0.0
Diffshow= 0.0
maxPressure = 0.0


#Setting up GUI

#popup window for entering sample name
class popupWindow(object):
    def __init__(self,master,**kwargs):
        if 'desc' not in kwargs:
            kwargs['desc'] = 'Enter a value: '
        if 'confirm_text' not in kwargs:
            kwargs['confirm_text'] = 'Submit'
        top=self.top=Toplevel(master)
        self.l=Label(top,text = kwargs['desc'])
        self.l.pack()
        self.e=Entry(top)
        self.e.focus()
        self.e.pack()
        self.b=Button(top,text=kwargs['confirm_text'],command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()

class mainWindow(object):
    def __init__(self,master):
        self.master=master
        self.b=Button(C,text="Exit",command= callback_end)
        self.b.place(x=500,y=350)
        self.b2=Button(C,text="Update Setpoint",command=updateSetpoint)
        self.b2.place(x=350,y=300)

    def popup(self,**kwargs):
        self.w=popupWindow(self.master,**kwargs)
        self.master.wait_window(self.w.top)

    def entryValue(self):
        return self.w.value

def updateSetpoint():
    global PressureSetpoint
    m.popup(desc='Enter a new pressure setpoint in mbar:',confirm_text='update')
    PressureSetpoint = int(m.entryValue())
    SP_current_text.set('Current Setpoint = ' + str(PressureSetpoint))


root = Tk()
root.title("Constant Pressure Controller")

#----initializing GUI------------------
##background_image = PhotoImage(file='/home/pi/Desktop/Code/background.gif')
##w=background_image.width()
##h=background_image.height()
C = Canvas(root, bg='#333',height=513,width=600) #<------- i changed heigt and width... need updating
C.focus_set() # Sets the keyboard focus to the canvas
#frame=Frame(root)
#frame= LabelFrame(root, text="Readouts",height=400,width=screenWidth)
#frame.pack(side="bottom")
#Readouts=Canvas(frame, bg= "gray", height = 399, width = screenWidth-1)
DL= StringVar()
DL.set('0')
differential_label = Label(C, textvariable=DL, padx=5,font=("Helvetica",16))
differential_label.place(x=50,y=150)

FRL= StringVar()
FRL.set('0')
Flowrate_label = Label(C, textvariable=FRL,pady=3,font=("Helvetica",16))
Flowrate_label.place(x=50,y=200)

FL= StringVar()
FL.set('0')
Filtrate_label = Label(C, textvariable=FL, padx=5,font=("Helvetica",16))
Filtrate_label.place(x=50,y=250)

MP = StringVar()
MP.set('0')
MaxP_label = Label(C, textvariable= MP, padx=5, font=("Helvetica",16))
MaxP_label.place(x=50, y=100)

SP_current_text = StringVar()
SP_current_text.set('Current Setpoint = '+ str(PressureSetpoint))
SP_current = Label(C, textvariable=SP_current_text, padx=5, font=("Helvetica",16))
SP_current.place(x=50, y=300)

#--- Graph settings
screenWidth = 450 # should name graphWidth
resolution = 1 #number of pixels between data points, for visual purposes only
timeRange = .5 #minutes
baseTime = int(timeRange*60*1000/screenWidth)
x0Coords = []
y0Coords = []
xy0Coords = []
FlowrateAvg = []
DiffAvg = []

coordLength = int(screenWidth/resolution)
#---initiation of lists
for i in range(0,coordLength):
    x0Coords.append(i*resolution)
    y0Coords.append(249)
    xy0Coords.append(0)
    xy0Coords.append(0)
for i in range(0,Average):
    FlowrateAvg.append(0.0)
    DiffAvg.append(0)

#putting X and Y corrdinites in a list
def coordinate():
    global x0Coords, y0Coords, xy0Coords
    for i in range(0,coordLength*2,2):
        xy0Coords[i] = x0Coords[i/2]
        xy0Coords[i+1] = y0Coords[i/2]


#---End initiation of lists
graph_height = 500

Graph= LabelFrame(root, text="Pressure Graph",height=graph_height+1,width=screenWidth)
Graph.pack(side="left")
graph_height = 500
ymin = -100
ymax = 100
axis_increment = 20

def to_px(y):
    global ymin,ymax,graph_height
    return int(graph_height - (1.0*y-ymin)/(ymax-ymin)*graph_height)

#debugger()

GraphC=Canvas(Graph, bg = "gray", height = graph_height, width = screenWidth-1)
maxP = GraphC.create_rectangle(0,0,20,50)
cl0 = GraphC.create_line(xy0Coords,smooth=True)

for y in range(ymin,ymax,axis_increment):
    y_px = to_px(y)
    if y_px < height and y_px > 0:
        if y >= 0:
            label = ' ' + str(y)
        else:
            label = str(y)
        GraphC.create_text(25,y_px,anchor=W,text=label + '  -')



#setting up GPIO pins
ForwardFlow = 21
PumpTrigger = 12
PumpRunningInd = 16
on = GPIO.LOW
off = GPIO.HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ForwardFlow, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Generally reads LOW
GPIO.setup(PumpTrigger,GPIO.OUT,initial=GPIO.LOW)# pump control
GPIO.setup(PumpRunningInd, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


#---------------------------------------------------------------------------------------
#                                 Definitions
#---------------------------------------------------------------------------------------


#-------------------------------- Read ADC --------------------------------------
def readadc_0(adcnum_0): #this fucntion can be used to find out the ADC value on ADC 0
    if adcnum_0 > 7 or adcnum_0 < 0:
        return -1

    r_0 = spi_0.xfer2([1, 8 + adcnum_0 << 4, 0]) #start bit, Single/Differential mode, Don't care bit OR
    adcout_0 = ((r_0[1] & 3) << 8) + r_0[2]
    return adcout_0

#-------------------------------- Increment Flow Count --------------------------
def callback_fflow(ForwardFlow):
    global ForwardFlowCount
    ForwardFlowCount+=1

#-------------------------------- update line graph -----------------------------
#shifts y values down in index in array to represent time moved forward
def shiftCoords(nextValue):

    global y0Coords, xy0Coords
    y0Coords.pop(0)
    y0Coords.append(int(nextValue))
    coordinate()

#-------------------------------- Update Graph --------------------------------------
#updates the GUI based on the new time
def move_time():
    global maxP,MP,cl0,xy0Coords,resolution,baseTime,forwardflow,Diffshow,maxPressure,flowshow,screenWidth, PressureSetpoint
    GraphC.delete(maxP)
    GraphC.delete(cl0)
    if maxPressure < Diffshow:
        maxPressure = Diffshow
    SP_line = GraphC.create_line(0,screenWidth,to_px(PressureSetpoint),to_px(PressureSetpoint), fill="red")
    MP.set("Max Pressure: " + str(maxPressure) + " psi")
    #PressureSetpoint = int(SP_content.get())
    shiftCoords(249-(Diffshow*250/100))
    cl0 = GraphC.create_line(xy0Coords)
    #c11 = Graph2C.create_oval(Diffshow*screenWidth/100-2,250-flowshow*250/20-2,Diffshow*screenWidth/100+2,250-flowshow*250/20+2)
    #print(float(readadc_0(0))/1023*250)
    #title="V= " , str(round(3.3*float(readadc_0(2)-readadc_0(0))/1023,2)) , str(round(3.3*float(readadc_0(2))/1023,2)), str(round(3.3*float(readadc_0(0))/1023,2))
    #root.title(title)
    root.after(baseTime*resolution,move_time)

#-------------------------------- Write Data --------------------------------------
def writeData():
    global destination,Diffshow,samplePeriod,ForwardFlowCount,oldForwardFlowCount,forwardflow,FlowrateAvg,flowshow,PressureSetpoint, PumpStatus, PumpControl

    ##Calibration of sensor: Real Pressure = reading-(-1.06+.1007xreading) this was Marks
    ## Calibration done Jul 9, 2015 by nick
    ## equation y=actual, x = pi, y=0.843x - 0.356

    Reading = (3.3*float(readadc_0(1)-readadc_0(2))/1023)*100 #conduct calibration here
    DifferentialPressure=round(0.843*Reading-0.356,1) # to PSI - 100 psi sensor (for burst tester)
    #DifferentialPressure=round(4207.1 * Reading - 2.6812,1) #to mbarr - 1 psi sensor (for cell filtration)
    DiffAvg.pop(0)
    DiffAvg.append(DifferentialPressure)
    Diffshow=np.mean(DiffAvg)
    DL.set("Diff Pressure: "+str(round(Diffshow,1)) + " psi")
    #DL.set("Diff Pressure: "+str(round(Diffshow,1)) + " mbar")

    if PressureSetpoint > 0:
        if DifferentialPressure < PressureSetpoint:
            PumpControl = True
        else:
            PumpControl = False
    else:
        if DifferentialPressure > PressureSetpoint:
            PumpControl = True
        else:
            PumpControl = False

    # Current pump status detected on pin 3 of PhD 4400 syringe pump
    PumpStatus = GPIO.input(PumpRunningInd) == GPIO.HIGH

    # Pump control sent to Pin 7 on PhD 4400 syringe pump
    # Rising edge starts pump
    # Falling edge stops pump
    if PumpStatus != PumpControl:
        if PumpControl == True:
            # check if previous signal was missed, cycle voltage to reset if needed
            if GPIO.input(PumpTrigger) == GPIO.HIGH:
                GPIO.output(PumpTrigger,GPIO.LOW)
            GPIO.output(PumpTrigger,GPIO.HIGH)
        else:
            # check if previous signal was missed, cycle voltage to reset if needed
            if GPIO.input(PumpTrigger) == GPIO.LOW:
                GPIO.output(PumpTrigger,GPIO.HIGH)
            GPIO.output(PumpTrigger,GPIO.LOW)

    forwardflow=((ForwardFlowCount-oldForwardFlowCount)/samplePeriod)*13.0435 #13.0435 = 1000/4600*60 #FTB2003 gets 4600 pulses per liter
    FlowrateAvg.pop(0)
    FlowrateAvg.append(forwardflow)
    flowshow = np.mean(FlowrateAvg)
    FRL.set("Flow rate: "+str(round(flowshow,1)) + " LPM")
    FL.set("Volume filtered: "+str(round(ForwardFlowCount/4600,4)) + " liters")
    data = str(round(DifferentialPressure,1)) + "\t" + str(round(forwardflow,1)) + "\t" + str(round(ForwardFlowCount/4600,4))
    # a.write("\n"+ str(datetime.now()) + "\t" + str(data))
    oldForwardFlowCount=ForwardFlowCount
    root.after(samplePeriod,writeData)

#-------------------------------- End Sequence --------------------------------------
def callback_end():
    global FlowCount, StartTime, popupDesc
    # GPIO.cleanup()#i think this would get get rid of the draining process
    print("max pressure was: " + str(maxPressure))
    #m.popup()
##    while m.entryValue() == "": #prevents entry of "" as file name.
##        m.popup()
##    while os.path.isfile(destination + m.entryValue()+".txt"):
##        popupDesc = "A file already exists for that sample. Please enter a different sample name: "
##        m.popup()
    #print (m.entryValue())
    spi_0.close()
    # a.write("\n" + str("Max Pressure was: ") + str(maxPressure))
    # a.close()
    #os.rename(destination + tempFileName, destination + m.entryValue() + ".txt")
    print("shutting down")
    quit()

#Setting up event detection
GPIO.add_event_detect(ForwardFlow, GPIO.RISING, callback=callback_fflow)



#----------------------------------Main loop----------------------------------------
#C.bind("e",callback_end)
C.pack()
##SP_content.set(str(PressureSetpoint))
GraphC.pack(anchor=W)
#Graph2C.pack(anchor=E)
#Readouts.pack(anchor=S)
root.after(baseTime,move_time)
root.after(samplePeriod,writeData)
m=mainWindow(root)
root.mainloop()
