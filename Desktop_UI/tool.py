import sqlite3
from time import sleep
from PyQt5 import QtCore, QtWidgets, QtSerialPort
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication,QMainWindow
from ui.login import Ui_logingateway
from ui.gateway import Ui_gateway
from ui.device import Ui_device
from ui.network import Ui_network
from ui.telemetry import Ui_telemetry
from ui.testtool import Ui_toolLogin
from ui.dialog import Ui_slavesetting
from ui.warning import Ui_warning
from source import Dialog,MqttClient, Serial, WarningDialog
from database.backend import Database
class Gateway(QMainWindow):
    def __init__(self,parent=None):
        super(Gateway, self).__init__(parent)
        self.login = Ui_logingateway()
        self.login.setupUi(self)
        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.login.comport.addItem(info.portName())
        self.login.refresh.clicked.connect(self.refresh)
        self.login.open.clicked.connect(self.open)

    def refresh(self):
        self.login.setupUi(self)
        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.login.comport.addItem(info.portName())
        self.login.refresh.clicked.connect(self.refresh)
        self.login.open.clicked.connect(self.open)

    def open(self):
        self.serial = Serial()
        comport = self.login.comport.currentText()
        baud = int(self.login.baudrate.currentText())
        if self.serial.openport(comport, baud) == True:
            self.gateway = Ui_gateway()
            self.gateway_setting()
        elif self.serial.openport(comport, baud) != True:
            self.warning = WarningDialog()
            self.warning.open()

    def gateway_setting(self):
        self.gateway.setupUi(self)
        self.gateway.gatewaysetting.clicked.connect(self.gateway_setting)
        self.gateway.devicesetting.clicked.connect(self.device_setting)
        self.gateway.networksetting.clicked.connect(self.network_setting)
        self.gateway.telemetrycontrol.clicked.connect(self.telemetry_control)
        self.gateway.testtool.clicked.connect(self.test_tool)
        self.gateway.updateport.clicked.connect(self.update_rs485)
        self.gateway.updatemqtt.clicked.connect(self.update_mqtt)
        self.gateway.updatetimeout.clicked.connect(self.update_timeout)
        self.gateway.updateapikey.clicked.connect(self.update_apikey)
        self.gateway.resetgateway.clicked.connect(self.reset_gateway)

    def update_rs485(self):
        global portname,baud, databit, stopbit, parity
        baud = int(self.gateway.baudrate.currentText())/1200
        if self.gateway.port.currentText() == 'PORT 0':
            portname = 'port0'
        elif self.gateway.port.currentText() == 'PORT 1':
            portname = 'port1'
        if int(self.gateway.databit.currentText()) == 8:
            databit = '0'
        elif int(self.gateway.databit.currentText()) == 7:
            databit = '1'
        if int(self.gateway.stopbit.currentText()) == 1:
            stopbit = '0'
        elif int(self.gateway.stopbit.currentText()) == 2:
            stopbit = '1'
        if self.gateway.parity.currentText() == "NONE":
            parity = '0'
        port = portname+' '+str(int(baud))+' '+databit+' '+stopbit+' '+parity+'\r'
        print(port)
        self.serial.send(port)
    def update_mqtt(self):
        str = 'mqtt'+' '+self.gateway.broker.text()+' '+ self.gateway.id.text()+' '+ self.gateway.username.text()+' '+ self.gateway.password.text()+' '+ self.gateway.mqttport.text()+'\r'
        self.serial.send(str)
    def update_timeout(self):
        global timeout
        temp = self.gateway.timeout.currentText().split()
        if temp[1] == 'minute':
            timeout = 'timeout'+' '+ str(int(temp[0])*60) +'\r'
        elif temp[1] == 'second':
            timeout = 'timeout'+' '+temp[0]+'\r'
        self.serial.send(timeout)
    def update_apikey(self):
        str = 'apikey'+' '+ self.gateway.apikey.text()+'\r'
        print(str)
        self.serial.send(str)
    def reset_gateway(self):
        str = 'save\r'
        self.serial.send(str)
    def device_setting(self):
        self.device = Ui_device()
        self.device.setupUi(self)
        self.device.gatewaysetting.clicked.connect(self.gateway_setting)
        self.device.devicesetting.clicked.connect(self.device_setting)
        self.device.networksetting.clicked.connect(self.network_setting)
        self.device.telemetrycontrol.clicked.connect(self.telemetry_control)
        self.device.testtool.clicked.connect(self.test_tool)
        self.device.add.clicked.connect(self.addDevice)
        self.device.deletechannel.clicked.connect(self.deleteChannel)
        self.device.view.clicked.connect(self.loadData)
        # self.database.showDatabase()
        self.database = Database("device.db")
        self.loadData()
    def addDevice(self):
        dialog = Dialog()
        dialog.exec_()
        if dialog.check_button() == True:
            port,slave,func,channel,datatype,devicetype,devicename,channeltitle,valuetype,scale = dialog.save()
            self.database.insert(port,slave,func[0],channel,datatype,devicetype,devicename,channeltitle,valuetype,scale)
            self.loadData()

    def updateDevice(self,port,slave,func,channel,datatype,devicetype,devicename,title,valuetype,scale):
        device = 'device'+' '+ port+' '+ slave+' '+ func+' '+ channel\
                  +' '+ devicetype+' '+ devicename+' '+ title+' '+ valuetype\
                  +' '+ datatype+' '+ scale+'\r'
        print(device)
        # self.serial.send(device)
    def deleteChannel(self):
        row = self.device.table.currentIndex().row()
        print(row)
        self.device.table.removeRow(row)
        self.database.delete(row)
    def loadData(self):
        connection = sqlite3.connect('device.db')
        cur = connection.cursor()
        result   = cur.execute('SELECT * FROM device')
        self.device.table.setRowCount(0)
        for row_number, row_data in enumerate (result):
            self.device.table.insertRow(row_number)
            for colum_number, data in enumerate(row_data):
                self.device.table.setItem(row_number,colum_number,QtWidgets.QTableWidgetItem(str(data)))

    def network_setting(self):
        self.network = Ui_network()
        self.network.setupUi(self)
        self.network.gatewaysetting.clicked.connect(self.gateway_setting)
        self.network.devicesetting.clicked.connect(self.device_setting)
        self.network.networksetting.clicked.connect(self.network_setting)
        self.network.telemetrycontrol.clicked.connect(self.telemetry_control)
        self.network.testtool.clicked.connect(self.test_tool)
        self.network.update.clicked.connect(self.update_network)
    def update_network(self):
        str = 'network'+' '+self.network.ip.text()+' '+ self.network.netmask.text()+' '+ self.network.gateway.text()+'\r'
        self.serial.send(str)

    def telemetry_control(self):
        self.control = Ui_telemetry()
        self.control.setupUi(self)
        self.control.gatewaysetting.clicked.connect(self.gateway_setting)
        self.control.devicesetting.clicked.connect(self.device_setting)
        self.control.networksetting.clicked.connect(self.network_setting)
        self.control.telemetrycontrol.clicked.connect(self.telemetry_control)
        self.control.testtool.clicked.connect(self.test_tool)
        self.control.provision.clicked.connect(self.send_provision)
        self.control.telemetryon.clicked.connect(self.set_telemetry)
        self.control.telemetryoff.clicked.connect(self.off_telemetry)
    def send_provision(self):
        str = 'provision\r'
        self.serial.send(str)
        self.control.provision.setStyleSheet("background-color:rgb(255, 223, 183)")
        self.control.telemetryon.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.control.telemetryoff.setStyleSheet("background-color:rgb(255, 255, 255)")
    def set_telemetry(self):
        str = 'telemetry 1\r'
        self.serial.send(str)
        self.control.provision.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.control.telemetryon.setStyleSheet("background-color:rgb(255, 223, 183)")
        self.control.telemetryoff.setStyleSheet("background-color:rgb(255, 255, 255)")
    def off_telemetry(self):
        str = 'telemetry 0\r'
        self.serial.send(str)
        self.control.provision.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.control.telemetryon.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.control.telemetryoff.setStyleSheet("background-color:rgb(255, 223, 183)")

    def test_tool(self):
        self.test = Ui_toolLogin()
        self.test.setupUi(self)
        self.test.gatewaysetting.clicked.connect(self.gateway_setting)
        self.test.devicesetting.clicked.connect(self.device_setting)
        self.test.networksetting.clicked.connect(self.network_setting)
        self.test.telemetrycontrol.clicked.connect(self.telemetry_control)
        self.test.testtool.clicked.connect(self.test_tool)
        self.test.connect.clicked.connect(self.toolLogin)
    def toolLogin(self):
        self.broker = self.test.broker.text()
        self.username = self.test.username.text()
        self.password = self.test.password.text()
        self.port = int(self.test.port.text())
        self.client = MqttClient()
        self.client.connect_server(self.broker,self.username,self.password,self.port)



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Gateway()
    w.show()
    sys.exit(app.exec_())