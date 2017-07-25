import RPi.GPIO as GPIO
from time import sleep
from Tkinter import *
import math
import time
import numpy as np
import spidev
from datetime import datetime, timedelta
import sys, os

#this is a test web edit

#To Do
## Check math on flow and pressure sensor (callibrate the pressure sensor
## beware of faulty wires... causes extreme noise
## fingernail polish pressure sensor so it doesn't get plugged in backwards
## order backup RPis
## order backup Differential op amps and ADCs
## Specify location of popup (for some reason its currently random)
#______________________________________________________________________________________________________________________
#----------------------------------------------------------------------------------------------------------------------
                                                                                                                                                                                                                      

print("start")

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
a=open(destination + tempFileName,'w') #a means append to existing file, w means overwrite old data
a.write("\n\n"+ str(datetime.now()))
Average = 3 #number of samples over which the "show" variables will be averaged
flowshow = 0.0
Diffshow= 0.0
maxPressure = 1.0
popupDesc = "Enter Sample Name (ie 31-A)"

#Setting up GUI

#popup window for entering sample name
class popupWindow(object):
    def __init__(self,master):
        global popupDesc
        top=self.top=Toplevel(master)
        self.l=Label(top,text = popupDesc)
        self.l.pack()
        self.e=Entry(top)
        self.e.focus()
        self.e.pack()
        self.b=Button(top,text='OK',command=self.cleanup)
        self.b.pack()
        
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()
    
class mainWindow(object):
    def __init__(self,master):
        self.master=master
        self.b2=Button(Controls,text="Update Pressure Target",command=lambda: PSdisplay.set((str(self.entryValue()))))
        self.b2.place(x=85,y=223)

    def popup(self):
        self.w=popupWindow(self.master)
        self.master.wait_window(self.w.top)

    def entryValue(self):
        return self.w.value

root = Tk()
root.title("Burst Tester")

#----initializing GUI------------------
##background_image = PhotoImage(file='/home/pi/Desktop/Code/background.gif')
##w=background_image.width()
##h=background_image.height() 
C = Canvas(root, bg='#333',height=400,width=1200) #<------- i changed heigt and width... need updating
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
SP = StringVar()
SP.set('0')
SP_label = Label(C, textvariable= SP, padx=5, font=("Helvetica",16))
SP_label.place(x=50, y=100)

#--- Graph settings
screenWidth = 450
resolution = 1 #number of pixels between data points, for visual purposes only
timeRange = .5 #minutes
baseTime = int(timeRange*60*1000/screenWidth)
x0Coords = []
y0Coords = []
xy0Coords = []
FlowrateAvg = []
##BackflowAvg = []
##FPumpAvg = []
##BPumpAvg = []
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
##    BackflowAvg.append(0)
##    FPumpAvg.append(ForwardPumpTarget)
##    BPumpAvg.append(BackwashPumpTarget)
    DiffAvg.append(0)
    
#putting X and Y corrdinites in a list
def coordinate():
    global x0Coords, y0Coords, xy0Coords
    for i in range(0,coordLength*2,2):
        xy0Coords[i] = x0Coords[i/2]
        xy0Coords[i+1] = y0Coords[i/2]


# setup thresholds
Controls= LabelFrame(root,text='Controls',height=270,width=w-450)
Controls.pack_propagate(False)
Controls.place(x=0,y=0)


PSdisplay = StringVar()
PSdisplay.set((str(PressureTarget)))
PSlabel = Label(Controls, textvariable=Pressure setpoint)
PSlabel.pack()

#---End initiation of lists

Graph= LabelFrame(root, text="Pressure Graph",height=250,width=screenWidth)
Graph.pack(side="left")
GraphC=Canvas(Graph, bg = "gray", height = 249, width = screenWidth-1)
Graph2= LabelFrame(root, text = "Flow vs. Pressure", height = 250, width=screenWidth)
Graph2.pack(side="right")
Graph2C=Canvas(Graph2, bg= "gray", height = 249, width = screenWidth-1)
maxP = GraphC.create_rectangle(0,0,20,50)
cl0 = GraphC.create_line(xy0Coords,smooth=True)
c11 = Graph2C.create_oval(Diffshow*screenWidth/100-2,250-flowshow*250/20-2,Diffshow*screenWidth/100+2,250-flowshow*250/20+2)
scale5 = Label(GraphC, text=' 100-', bg = "gray")
scale5.place(x=0,y=(240-20*12))
scale7 = Label(GraphC, text=' 90-', bg = "gray")
scale7.place(x=0,y=(240-18*12))
scale9 = Label(GraphC, text=' 80-', bg = "gray")
scale9.place(x=0,y=(240-16*12))
scale11 = Label(GraphC, text=' 70-', bg = "gray")
scale11.place(x=0,y=(240-14*12))
scale12 = Label(GraphC, text=' 60-', bg = "gray")
scale12.place(x=0,y=(240-12*12))
scale10 = Label(GraphC, text=' 50-', bg = "gray")
scale10.place(x=0,y=(240-10*12))
scale8 = Label(GraphC, text=' 40-', bg = "gray")
scale8.place(x=0,y=(240-8*12))
scale6 = Label(GraphC, text=' 30-', bg = "gray")
scale6.place(x=0,y=(240-6*12))
scale4 = Label(GraphC, text=' 20-', bg = "gray")
scale4.place(x=0,y=(240-4*12))
scale2 = Label(GraphC, text=' 10-', bg = "gray")
scale2.place(x=0,y=(240-2*12))
scale0 = Label(GraphC, text=' 0-', bg = "gray")
scale0.place(x=0,y=(240-0*20))

x2Axis = Label(Graph2C, text="Pressure (psi)")
x2Axis.place(x=screenWidth/2-10,y=230)

y2Axis = Label(Graph2C, text="Flowrate", wraplength=1)
y2Axis.place(x= 0,y=250/2-50)

#setting up GPIO pins                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
ForwardFlow = 21
PumpTrigger = 12
on = GPIO.LOW
off = GPIO.HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ForwardFlow, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Generally reads LOW
GPIO.setup(PumpTrigger,GPIO.OUT,initial=GPIO.HIGH)


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
    global maxP,MP,cl0,xy0Coords,resolution,baseTime,forwardflow,Diffshow,maxPressure,flowshow,screenWidth, c11
    GraphC.delete(maxP)
    GraphC.delete(cl0)
    if maxPressure < Diffshow:
        maxPressure = Diffshow
    maxP = GraphC.create_rectangle(0,250,480,249-int(maxPressure*250/100), outline="red") #why dividing backwashflow?? <--------------------------
    MP.set("Max Pressure: " + str(maxPressure) + " psi")
    SP.set("Pressure Setpoint: " + str(SPdisplay.get()) + " mBar")
    shiftCoords(249-(Diffshow*250/100))
    cl0 = GraphC.create_line(xy0Coords)
    c11 = Graph2C.create_oval(Diffshow*screenWidth/100-2,250-flowshow*250/20-2,Diffshow*screenWidth/100+2,250-flowshow*250/20+2)
    #print(float(readadc_0(0))/1023*250)
    #title="V= " , str(round(3.3*float(readadc_0(2)-readadc_0(0))/1023,2)) , str(round(3.3*float(readadc_0(2))/1023,2)), str(round(3.3*float(readadc_0(0))/1023,2))
    #root.title(title)
    root.after(baseTime*resolution,move_time)

#-------------------------------- Write Data --------------------------------------
def writeData(): 
    global destination,Diffshow,samplePeriod,ForwardFlowCount,oldForwardFlowCount,forwardflow,FlowrateAvg,flowshow

    ##Calibration of sensor: Real Pressure = reading-(-1.06+.1007xreading) this was Marks
    ## Calibration done Jul 9, 2015 by nick
    ## equation y=actual, x = pi, y=0.843x - 0.356

    Reading = (3.3*float(readadc_0(1)-readadc_0(2))/1023)*100 #conduct calibration here
    DifferentialPressure=round(0.843*Reading-0.356,1)
    DiffAvg.pop(0)
    DiffAvg.append(DifferentialPressure)
    Diffshow=np.mean(DiffAvg)
    DL.set("Diff Pressure: "+str(round(Diffshow,1)) + " psi")
    
     
    forwardflow=((ForwardFlowCount-oldForwardFlowCount)/samplePeriod)*13.0435 #13.0435 = 1000/4600*60 #FTB2003 gets 4600 pulses per liter
    FlowrateAvg.pop(0)
    FlowrateAvg.append(forwardflow)
    flowshow = np.mean(FlowrateAvg)
    FRL.set("Flow rate: "+str(round(flowshow,1)) + " LPM")
    FL.set("Volume filtered: "+str(round(ForwardFlowCount/4600,4)) + " liters")
    data = str(round(DifferentialPressure,1)) + "\t" + str(round(forwardflow,1)) + "\t" + str(round(ForwardFlowCount/4600,4))
    a.write("\n"+ str(datetime.now()) + "\t" + str(data))
    oldForwardFlowCount=ForwardFlowCount
    root.after(samplePeriod,writeData)

#-------------------------------- End Sequence --------------------------------------
def callback_end(event):
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
    a.write("\n" + str("Max Pressure was: ") + str(maxPressure))
    a.close()
    os.rename(destination + tempFileName, destination + m.entryValue() + ".txt")
    quit()

#Setting up event detection
GPIO.add_event_detect(ForwardFlow, GPIO.RISING, callback=callback_fflow)



#----------------------------------Main loop----------------------------------------
C.bind("e",callback_end)
C.pack()
GraphC.pack(anchor=W)
Graph2C.pack(anchor=E)
#Readouts.pack(anchor=S)
root.after(baseTime,move_time)
root.after(samplePeriod,writeData)
m=mainWindow(root)
root.mainloop()
