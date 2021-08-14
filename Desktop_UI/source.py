
from ui.warning import Ui_warning
from PyQt5 import QtCore, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow
from ui.login import Ui_logingateway
from ui.gateway import Ui_gateway
from ui.device import Ui_device
from ui.network import Ui_network
from ui.telemetry import Ui_telemetry
from ui.testtool import Ui_toolLogin
from ui.dialog import Ui_slavesetting
from ui.mqtt import Ui_demo
from ui.server_warning import Ui_server_warning
import paho.mqtt.client as mqttclient

class Serial(QtSerialPort.QSerialPort,Ui_logingateway):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = QtSerialPort.QSerialPort(self,readyRead=self.receive)
        self.control = Ui_telemetry()
    @QtCore.pyqtSlot()
    def openport(self,portname,baudrate):
        self.serial.setPortName(portname)
        self.serial.setBaudRate(baudrate)
        return self.serial.open(QtCore.QIODevice.ReadWrite)

    @QtCore.pyqtSlot()
    def send(self,string):
        self.serial.write(string.encode())

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\n')
            # print(str(text))
            # if text == 'provision':
            #     print('provision')
            # elif text == 'on':
            #     print('telemetry on')
            # elif text == 'off':
            #     print('telemetry off')
            # elif text == 'port0':
            #     print('port 0')
            # elif text == 'port1':
            #     print('port 1')
            # elif text == 'network':
            #     print('network')
            # elif text == 'mqtt':
            #     print('mqtt')
            # elif text == 'timeout':
            #     print('timeout')
            # elif text == 'apikey':
            #     print('apikey')

class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.ui = Ui_slavesetting()
        self.ui.setupUi(self)
        self.ui.save.clicked.connect(self.check_button)
        self.ui.save.clicked.connect(self.save)

    def check_button(self):
        if self.ui.save.isChecked:
            return True
            # self.ui.save.setEnabled(False)

    def save(self):
        return self.ui.port.currentText(),self.ui.slaveAddress.text(),self.ui.function.currentText().split(),\
            self.ui.devicechannel.text(),self.ui.datatype.currentText(),\
            self.ui.devicetype.currentText(),self.ui.devicename.text(),self.ui.channeltitle.text(),\
            self.ui.valuetype.currentText(),self.ui.scale.currentText()
#--------------------------------------------------------------------------------------#
class WarningDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(WarningDialog,self).__init__(parent)
        self.warning = Ui_warning()
        self.warning.setupUi(self)
class ServerWarning(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.warning = Ui_server_warning()
        self.warning.setupUi(self)
class Tool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tool = Ui_demo()
        self.tool.setupUi(self)
        self.tool.getlumen.clicked.connect(self.get_lumen)
    def get_lumen(self):
        self.tool.lumen.text()

class MqttClient():
    def __init__(self, parent=None):
        self.client= mqttclient.Client()
        self.client.on_connect=self.on_connect()
        self.client.on_message=self.on_message
    def connect_server(self,broker,username,password,port):
        self.client.username_pw_set(username,password)
        self.client.connect(broker,port,60)
        self.client.loop_start()
    def disconnect_server(self):
        self.client.loop_stop(self)
        self.client.disconnect()
        print("Disconnected")
    def on_connect(self,client,userdata,flags,rc):
        print("Connected with code : " + str(rc))
        if rc == 0:
            client.subscribe("up/command")

    def on_message(self,client,userdata,msg):
        temp_receive = str(msg.payload.decode("utf-8"))
