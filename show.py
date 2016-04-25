#-*- coding: UTF-8 -*-
import wx
import serial
import sys,time,math,random
import signal
from time import ctime,sleep
import glob,struct
from multiprocessing import Process,Manager,Array
import threading
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
import numpy as np
from matplotlib.backends.backend_wxagg import  FigureCanvasWxAgg as FigureCanvas
ser = serial.Serial('/dev/ttyAMA0',115200,timeout=10)
TIMER_ID = wx.NewId()
POINTS = 300
msg = ""
arr = [0]
def __onRead():
  global msg,arr;
  while True:
      try:	
          if ser.isOpen()==True:
              n = ser.inWaiting()
              for i in range(n):
                  c = ser.read()
                  if (c=='\r'):             
                    arr = msg.split()      
                    msg = ""
                  else:      
                    msg+=c
              #print s
              sleep(0.01)
          else:	
              sleep(0.5)
      except Exception,ex:
          print str(ex)
          sleep(1)
th = threading.Thread(target=__onRead)
th.start()

class PlotFigure(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Sensor Monitor", size=(800, 600))
        #设置窗口大小
        #初始化MegaPi
        self.fig = Figure((8, 6), 100)
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim([0, 100])
        self.ax.set_xlim([0, POINTS])
        self.ax.set_autoscale_on(False)
        self.ax.set_xticks([])
        self.ax.set_yticks(range(0, 101, 10))
        self.ax.grid(True)
        #设置网格标志
        self.user = [None] * POINTS
        self.l_user,=self.ax.plot(range(POINTS),self.user,label='Light Sensors')
        self.ax.legend(loc='upper center',
                           ncol=4,
                           prop=font_manager.FontProperties(size=10))
        self.canvas.draw()
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)
        wx.EVT_TIMER(self, TIMER_ID, self.onTimer)

    def onTimer(self, evt):
        self.canvas.restore_region(self.bg)
        for i in range(0,240):
          index = int(i/40)*40
          per = (index-i)+20.0
          per =((math.sin((per/20.0)*math.pi/2))+1.0)/2.0
          self.user[i+30] = 100-(float(arr[i/40])*per+float(arr[(i+40)/40])*(1-per))*1
        self.l_user.set_ydata(self.user)
        self.ax.draw_artist(self.l_user)
        self.canvas.blit(self.ax.bbox)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PlotFigure()
    t = wx.Timer(frame, TIMER_ID)
    t.Start(10)
    frame.Show()
    app.MainLoop()
