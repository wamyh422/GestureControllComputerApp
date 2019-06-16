import wx

import serial
import pyautogui
import serial.tools.list_ports
import webbrowser
import os
import time
from threading import Thread 
from pubsub import pub

COM_path=''
Start_flag = False
Running_flag = False
AutoKey_config = ''
Controll_Msg=''
#--COM_path,six action config needed in serial part-------
#---------------Get Serial COM Function--------------------
def  getSerialCOM(text):
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) <=0:
            content = "The Serial port can't find!"
            text.SetLabel(content)
            return False
    else:
        port_list_0 = list(port_list[0])
        port_serial = port_list_0[0]
        content = 'Arduino Using : '+str(port_serial)
        global COM_path 
        COM_path = str(port_serial)
        text.SetLabel(content)
        return True
#Open Application Function----------------------------------------------------
def OpenApp(num):
    global Start_flag
    global AutoKey_config
    if num==0:
        webbrowser.open('https://www.youtube.com/', new=0, autoraise=True) 
        Start_flag = True
        AutoKey_config="YouTuBe"
    elif num==1:
        os.system('start VLC media player')
        Start_flag = True
        AutoKey_config="VLC"
    else:
        Start_flag = False
#Start/End Serial Function---------------------------------------------------------
def StartSerial():
    global Running_flag
    if Running_flag ==False:
        Running_flag =True
    elif Running_flag ==True:
        Running_flag =False
#-----------------Thread defined--------------------------------------------------
class TestThread(Thread): 
    def __init__(self): 
#"""Init Worker Thread Class."""
        Thread.__init__(self) 
        self.start()  
    def run(self): 
        if AutoKey_config=="YouTuBe":
            YoutubeSerial()
        elif AutoKey_config=="VLC":
            VLCSerial()
#---------------------------------------------------------------------- 
#=========Youtube Thread======================
def YoutubeSerial():
    if Running_flag==True:
        global Controll_Msg
        ArduinoSerial = serial.Serial(COM_path,9600)
        time.sleep(2)
        while Running_flag:
            comingData = str(ArduinoSerial.readline())
            Controll_Msg =str(ArduinoSerial.readline().decode())
            pub.sendMessage("panel_listener", message=Controll_Msg)
            if 'Play/Pause' in comingData:
                pyautogui.press('space')
            if 'Rewind' in comingData:
                pyautogui.press('left')
            if 'Forward' in comingData:
                pyautogui.press('right')
            if 'Vup' in comingData:
                pyautogui.press('up')
            if 'Vdown' in comingData:
                pyautogui.press('down')
#=========================================
#=========VLC Thread=========================
def VLCSerial():
    if Running_flag==True:
        ArduinoSerial = serial.Serial(COM_path,9600)
        time.sleep(2)
        while Running_flag:
            comingData = str(ArduinoSerial.readline())
            Controll_Msg =str(ArduinoSerial.readline().decode())
            pub.sendMessage("panel_listener", message=Controll_Msg)
            if 'Play/Pause' in comingData:
                pyautogui.typewrite(['space'],0.2)
            if 'Rewind' in comingData:
                pyautogui.hotkey('ctrl', 'left')
            if 'Forward' in comingData:
                pyautogui.hotkey('ctrl', 'right')
            if 'Vdown' in comingData:
                pyautogui.hotkey('ctrl', 'down')
            if 'Vup' in comingData:
                pyautogui.hotkey('ctrl', 'up')
#=========================================
#----------------GUI class def---------------------------------
class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='Controll Panel',size=(900,550))
        panel = wx.Panel(self)        
        my_sizer = wx.BoxSizer(wx.VERTICAL)     
        pub.subscribe(self.my_listener, "panel_listener")
        #COM textView----------------------------------------
        self.textView_COM = wx.StaticText(panel)
        self.textView_COM.SetLabel ('Renew to get COMport')
        my_sizer.Add(self.textView_COM,0,wx.ALL | wx.CENTER, 10)
        #--------------------------------------------------------
        #Renew COM btn--------------------------------------
        Renew_btn = wx.Button(panel, label='Renew port')
        Renew_btn.Bind(wx.EVT_BUTTON, self.on_press)
        my_sizer.Add(Renew_btn, 0, wx.ALL | wx.CENTER, 5)   
        #--------------------------------------------------------
        #Mode chooser----------------------------------------
        lblList = ['YouTuBe','VLC player']
        self.Mode_Radio = wx.RadioBox(panel, label='Choose MOD'
                                      ,choices=lblList)
        self.Mode_Radio.Disable()
        my_sizer.Add(self.Mode_Radio,0,wx.ALL | wx.CENTER,5)
        #--------------------------------------------------------
        #confirm MODE btn-----------------------------------
        self.Mode_btn = wx.Button(panel, label='confirm')
        self.Mode_btn.Disable()
        self.Mode_btn.Bind(wx.EVT_BUTTON, self.on_mod)
        my_sizer.Add(self.Mode_btn,0,wx.ALL | wx.CENTER,5)
        #--------------------------------------------------------
        self.statusText  = wx.StaticText(panel,size=(125,250))
        my_sizer.Add(self.statusText ,0,wx.ALL | wx.CENTER,5)
        self.Start_btn = wx.Button(panel,label='Start')
        self.Start_btn.Disable()
        self.Start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        my_sizer.Add(self.Start_btn,0,wx.ALL | wx.CENTER,5)





        panel.SetSizer(my_sizer)
        self.Show()
#COM finder---------------------------------
    def on_press(self, event):
        if getSerialCOM(self.textView_COM)==True:
            self.Mode_btn.Enable()
            self.Mode_Radio.Enable()
#mode button event-------------------------
    def on_mod(self,event):
        OpenApp(self.Mode_Radio.Selection)
        #Check config set-----------------------
        if Start_flag ==True:
            self.Start_btn.Enable()
#start Serial event----------------------------
    def on_start(self,event):
        StartSerial()
        TestThread()
        if Running_flag ==True:
            self.Start_btn.SetLabel('Pause')
        else:
            self.Start_btn.SetLabel('Start')
    def my_listener(self, message):
        """
        Listener function
        """
        self.statusText.SetLabelText(message)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
