# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import pymssql
import datetime
import base64
import hashlib

from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow
from PyQt5.QtWidgets import QPushButton, QAction, qApp, QMessageBox
from PyQt5.QtWidgets import QBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication, QTimer
from serial import Serial
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

class TemperHumiWidget(QWidget):
    IsComPortSet = False

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.key = b'F990B19FBDDA463DAFD0E4F4DE34EB52'

        Label_Temperature = QLabel('Temperature : ')
        self.Label_Temperature_value = QLabel('Unknown')
        Label_Humidity = QLabel('Humidity : ')
        self.Label_Humidity_value = QLabel('Unknown')
        self.Label_message = QLabel('')

        grid = QGridLayout()
        grid.addWidget(QLabel('DB Server IP'), 0, 0)
        grid.addWidget(QLabel('DB Server Port'), 1, 0)
        grid.addWidget(QLabel('Database Name'), 2, 0)
        grid.addWidget(QLabel('Database Acct'), 3, 0)
        grid.addWidget(QLabel('Database Pwd'), 4, 0)
        grid.addWidget(QLabel('Check Interval(Sec)'), 5, 0)
        grid.addWidget(QLabel('Serial PortInfo'), 6, 0)
        self.Label_message = QLabel()
        grid.addWidget(self.Label_message, 7, 0, 1, 2)

        self.DBIPLE = QLineEdit()
        grid.addWidget(self.DBIPLE, 0, 1)
        self.DBPortLE = QLineEdit()
        grid.addWidget(self.DBPortLE, 1, 1)
        self.DBNameLE = QLineEdit()
        grid.addWidget(self.DBNameLE, 2, 1)
        self.DBAcctLE = QLineEdit()
        grid.addWidget(self.DBAcctLE, 3, 1)
        self.DBPwdLE = QLineEdit()
        self.DBPwdLE.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.DBPwdLE, 4, 1)
        self.ChkIntervalLE = QLineEdit()
        grid.addWidget(self.ChkIntervalLE, 5, 1)
        self.ChkIntervalLE.setText('30')
        self.portLE = QLineEdit()
        grid.addWidget(self.portLE, 6, 1)

        btn_read = QPushButton('Read', self)
        # btn.geometry(150,200,50,50)
        btn_read.resize(100, 50)
        btn_read.clicked.connect(self.btn_read_clicked)

        btn_save = QPushButton('Save', self)
        # btn.geometry(150,200,50,50)
        btn_save.resize(100, 50)
        btn_save.clicked.connect(self.btn_save_clicked)

        btn_cancle = QPushButton('Cancle', self)
        # btn.geometry(150,200,50,50)
        btn_cancle.resize(100, 50)
        btn_cancle.clicked.connect(QCoreApplication.instance().quit)

        #self.resize(500, 200)
        #self.center()
        #self.setWindowTitle('QWidget')

        layout_Result = QHBoxLayout()
        layout_Result.addStretch(1)
        layout_Result.addWidget(Label_Temperature)
        layout_Result.addWidget(self.Label_Temperature_value)
        layout_Result.addStretch(1)
        layout_Result.addWidget(Label_Humidity)
        layout_Result.addWidget(self.Label_Humidity_value)
        layout_Result.addStretch(1)
        layout_Setting = QHBoxLayout()
        layout_Setting.addLayout(grid)
        layout_control = QHBoxLayout()
        layout_control.addStretch(1)
        layout_control.addWidget(btn_read)
        layout_control.addStretch(1)
        layout_control.addWidget(btn_save)
        layout_control.addStretch(1)
        layout_control.addWidget(btn_cancle)
        layout_control.addStretch(1)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addLayout(layout_Result)
        layout.addStretch(1)
        layout.addLayout(layout_Setting)
        layout.addStretch(1)
        layout.addLayout(layout_control)
        layout.addStretch(1)
        self.setLayout(layout)

        self.load_config()
        Intervalinfo = int(self.ChkIntervalLE.text()) * 1000

        self.qtTimer = QTimer()
        self.qtTimer.setInterval(Intervalinfo)
        self.qtTimer.timeout.connect(self.read_serial)
        self.qtTimer.start()

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def read_serial(self):
        if self.IsComPortSet == True:
            portinfo = self.portLE.text()
            if portinfo.lower().find('com') != -1 :
                try:
                    serial_obj = Serial(portinfo, 9600)
                    count = 0
                    while count < 5:
                        if serial_obj.readable():
                            serial_value = serial_obj.readline()
                            # if serial_value.decode()
                            TempValue = serial_value.decode()
                            if TempValue[0:2] == "OK":
                                ReadValue = TempValue.split(',\t')
                                # self.label_Temperature_value.setText(serial_value.decode('ascii'))
                                self.Label_Temperature_value.setText(ReadValue[2].replace('\r\n', ''))
                                self.Label_Humidity_value.setText(ReadValue[1])
                                #conn = pymssql.connect(server='LOCALHOST', port='1433', user='THMonUser', password='THMonU$er!', database='THMon')
                                temp1 = self.DBIPLE.text()
                                temp2 = self.DBPortLE.text()
                                temp3 = self.DBAcctLE.text()
                                temp4 = self.DBPwdLE.text()
                                temp5 = self.DBNameLE.text()
                                if self.DBIPLE.text() != "" and self.DBAcctLE.text() != "" \
                                        and self.DBPwdLE.text() != "" and self.DBNameLE.text() != "":
                                    try:
                                        conn = pymssql.connect(server=self.DBIPLE.text(), port=self.DBPortLE.text(),
                                                               user=self.DBAcctLE.text(), password=self.DBPwdLE.text(),
                                                               database=self.DBNameLE.text())
                                        cursor = conn.cursor()
                                        cursor.execute("INSERT INTO " + self.DBNameLE.text() + ".dbo.THMonLog (ChkTime, Temperature, Humidity) VALUES(" + "'"
                                                       + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "', "
                                                       + ReadValue[2].replace('\r\n', '')
                                                       + ", " + ReadValue[1] + ")")
                                        conn.commit()
                                        conn.close()
                                    except pymssql.InterfaceError:
                                        self.Label_message.setText('** Warning : DataBase Interface Error occurred.**')
                                        continue
                                    except pymssql.DatabaseError:
                                        self.Label_message.setText('** Warning : DataBase Internal Error occurred.**')
                                        continue
                                    except pymssql.OperationalError:
                                        self.Label_message.setText('** Warning : DataBase Operational Error occurred.**')
                                        continue

                        count += 1
                except Exception as E:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("Serial 통신오류")
                    msgBox.setInformativeText("Serial 통신에 실패하였습니다. 정보가 올바른지 확인하세요.")
                    msgBox.setDefaultButton(QMessageBox.Ok)
                    msgBox.exec_()
                    serial_obj.close()

                    return

    def btn_read_clicked(self):
        portinfo = self.portLE.text()
        if portinfo.lower().find('com') == -1:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("입력오류 알림")
            msgBox.setInformativeText("Serial Port 정보가 올바르지 않습니다.")
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()
        else:
            self.IsComPortSet = True
            self.read_serial()

    def btn_save_clicked(self):
        f_config = open("./config.txt", 'wb')
        f_config.write((self.DBIPLE.text() + "\n").encode())
        f_config.write((self.DBPortLE.text() + "\n").encode())
        f_config.write((self.DBNameLE.text() + "\n").encode())
        f_config.write((self.DBAcctLE.text() + "\n").encode())

        #AES256 암호화를 위한 32byte 암호화키 난수 생성
        InnerCipherE = AES.new(self.key, AES.MODE_GCM)
        test=self.DBPwdLE.text()
        InnerCipherEText, InnerCipherETag = InnerCipherE.encrypt_and_digest(self.DBPwdLE.text().encode())
        [f_config.write(x) for x in (InnerCipherE.nonce, InnerCipherETag, InnerCipherEText)]
        f_config.write(("\n").encode())
        f_config.write((self.ChkIntervalLE.text() + "\n").encode())

        f_config.close()

    def load_config(self):
        try:
            f_config = open("./config.txt", 'rb')
            SavedConfig = f_config.readlines()
            SavedDBIP = SavedConfig[0].replace(b'\n',b'').decode()
            SavedDBPort = SavedConfig[1].replace(b'\n',b'').decode()
            SavedDBName = SavedConfig[2].replace(b'\n',b'').decode()
            SavedDBAcct = SavedConfig[3].replace(b'\n',b'').decode()

            nonce = SavedConfig[4][0:16]
            InnerCipherTag = SavedConfig[4][16:32]
            ciphertext = SavedConfig[4][32:].replace(b'\n',b'')
            InnerCipherD = AES.new(self.key, AES.MODE_GCM, nonce)
            try:
                SavedDBPW =  InnerCipherD.decrypt_and_verify(ciphertext, InnerCipherTag).decode()
                SavedChkInterval = SavedConfig[5].replace(b'\n',b'').decode()
            except Exception as E:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setInformativeText("config 파일이 손상되었습니다. 삭제 후 다시 실행 해주세요.")
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec_()

            self.DBIPLE.setText(SavedDBIP)
            self.DBPortLE.setText(SavedDBPort)
            self.DBNameLE.setText(SavedDBName)
            self.DBAcctLE.setText(SavedDBAcct)
            self.DBPwdLE.setText(SavedDBPW)
            if SavedChkInterval != '' :
                self.ChkIntervalLE.setText(SavedChkInterval)

            f_config.close()
        except FileNotFoundError as e:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setInformativeText("config 파일이 존재하지 않습니다.")
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()

class TemperHumi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        #print_serialRead(self)

    def initUI(self):
        exitAction = QAction(QIcon(''), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(qApp.quit)

        InfoAction = QAction(QIcon(''), 'Info', self)
        InfoAction.setShortcut('Ctrl+I')
        InfoAction.setStatusTip('Show Program Information')
        InfoAction.triggered.connect(self.Show_Info)

        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&FILE')
        filemenu.addAction(exitAction)
        helpmenu = menubar.addMenu('&HELP')
        helpmenu.addAction(InfoAction)

        self.setWindowTitle('Temperature & Humidity')
        self.setWindowIcon(QIcon('./img/icon.png'))
        #self.move(300,300)
        #self.resize(600,400)
        self.statusBar().showMessage('Ready')
        #self.setGeometry(300,300,600,400)
        #self.resize(600, 400)

        self.wg = TemperHumiWidget()
        self.setCentralWidget(self.wg)
        self.resize(400, 400)

        self.show()

    def Show_Info(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("프로그램 정보")
        msgBox.setInformativeText("가. Arduino Uno + DHT22(AM2302)로\n제작된 온/습도계에서 동작하도록\n만들어진 프로그램 입니다.\n \
                                  \n나. 장치관리자를 참고하여 정확한\nCOM포트 번호(ex:COM3)\n입력이 필요합니다.\n \
                                  \n다. DB에 아래 테이블이 필요합니다.\nTable Name:THMonLog\nColumn:\
                                  \n　　ChkTime　　　DATETIME\
                                  \n　　Temperature　NUMERIC(5,2)\n　　Humidity　　NUMERIC(5,2)\
                                  \n　　(ChkTime Clustered Index 권장)\n \
                                  \n라. Interval 변경 시 프로그램을\n껐다켜야 적용됩니다.\n")
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print("Hi, {0}".format(name))  # Press Ctrl+F8 to toggle the breakpoint.



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    app = QApplication(sys.argv)
    #ex1 = TemperHumiWidget()
    ex = TemperHumi()

    sys.exit(app.exec_())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
