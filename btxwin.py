#!/usr/bin/python


from PyQt4.QtCore import *		# Qt core
from PyQt4.QtGui import *		# Qt GUI interface
from PyQt4.uic import *			# ui files realizer
from PyQt4 import QtGui, uic
from brewtroller import *
from mash import *
from functools import *

import sys				# system support


UI_FILE = 'lodda.ui'		# qt ui descriptor

class XTun(Tun):
     
     setpointsaved = True
     manualsetpoint = 0 

     def setSetpointManually(self, value):
          self.setpointsaved = False
          self.setPointWidget.display(value)
          self.setPointWidget.setStyleSheet("QLCDNumber{color:blue;}")
          self.manualsetpoint = value

     def __init__(self, w, bt, myid, setpoint, temperature, setbutton, dial):
          Tun.__init__(self,bt, myid)
          self.setPointWidget = setpoint
          self.dialWidget = dial
          self.temperatureWidget = temperature

          w.connect(dial,SIGNAL("valueChanged(int)"), partial(XTun.setSetpointManually,self))

     def update(self):
          if self.setpointsaved:
               Tun.update(self)
               if self.newsetpoint != self.setpoint:
                    self.setPointWidget.display(self.newsetpoint)
                    self.setPointWidget.setStyleSheet("QLCDNumber{color:green;}")
                    self.setpoint = self.newsetpoint
                    self.manualsetpoint = self.setpoint
#                    print(self.setpoint)

               if (self.newtemperature < 200) and (self.newtemperature > -20): # disconnected onewire results in weird numbers.
                    if self.newtemperature != self.temperature:
                         self.temperatureWidget.setDecMode()
                         self.temperatureWidget.display(self.newtemperature)
                         self.temperatureWidget.setStyleSheet("QLCDNumber{color:red;}")
                         self.temperature = self.newtemperature
               else:
                    self.temperatureWidget.setHexMode()
                    self.temperatureWidget.display(int("dead",16))
                    
class XProgramStatus:

     oldstep=255
     
     def __init__(self, w, bt,stepWidgets):
          self.BrewStep = BrewStep(bt)
          self.stepWidgets = stepWidgets
          self.bt = bt

     def update(self):
          # if the brewstep is 255 the system is idle
          brewstep = self.BrewStep.getStep()


          if brewstep != 255:
               # need to update the progress bars and display which step is active
               fullstatus = self.bt.getFullStatus()
               print ("step" + str(brewstep))
               print (fullstatus)

               # put text on the active step
               if self.oldstep != brewstep:
                    for key in self.stepWidgets:
                         if key == brewstep:
                              self.stepWidgets[key].setTextVisible(True) 
                         else:
                              self.stepWidgets[key].setTextVisible(False)
                    self.oldstep = brewstep

          
class MainWin(QtGui.QMainWindow):
     def __init__(self,bt):
         QtGui.QMainWindow.__init__(self)
         self.bt = bt

         # Set up the user interface from Designer.
         self.ui = uic.loadUi(UI_FILE)
         self.ui.show()

         self.HLT = XTun(self.ui, bt, 0, self.ui.HLTSet, self.ui.HLTTemp, self.ui.toggleHLT, self.ui.HLTdial)
         self.MLT = XTun(self.ui, bt, 1, self.ui.MLTSet, self.ui.MLTTemp, self.ui.toggleMLT, self.ui.MLTdial)
         
         stepwidgets = {
              2: self.ui.progresspreheat,
              5: self.ui.progressdoughin,
              6: self.ui.progressacidrest,
              7: self.ui.progressproteinrest,
              8: self.ui.progressacc1,
              9: self.ui.progressacc2,
              10: self.ui.progressmashout
              }
         self.programstatus = XProgramStatus(self.ui, bt, stepwidgets)

         # init callbacks


     # callback functions

     def updateui(self):
          self.MLT.update()
          self.HLT.update()
          self.programstatus.update()


### main

# create a connection to the btnic daemon
bt = BrewTroller("http://10.168.0.10/cgi-bin/btnic.cgi")
app = QtGui.QApplication(sys.argv)
window = MainWin(bt)
timer = QTimer()
timer.timeout.connect(window.updateui)
timer.start(1000)


sys.exit(app.exec_())

