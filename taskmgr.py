from os import system
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
import sys, psutil, pyautogui, csv

class MyClass():
    def __init__(self):
        self.cgName = list()
        self.cgCPU = list()
        self.cgMem = list()

x = MyClass()

class ThreadClass(QThread, Qt):
    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow
    
    def run(self):
        self.mainwindow.loop()
        
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.createMenuBar()
        self.createButtons()

    def setupUi(self):  
        self.setWindowTitle("Диспетчер задач")
        self.move(300,300)
        self.resize(500, 500)
        self.tw = QtWidgets.QTreeWidget()
        self.tw.setHeaderLabels(["Имя", "ЦП", "Память"])
        self.setCentralWidget(self.tw)
        self.setFixedSize(500, 500)
        self.ThreadClass_instance = ThreadClass(mainwindow=self)
        self.launchThreadClass()

    def createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("Файл")
        newAction = QAction("Запустить новую задачу", self)
        closeAction = QAction("Выход", self)
        fileMenu.addAction(newAction)
        fileMenu.addAction(closeAction)
        closeAction.triggered.connect(self.close)
        newAction.triggered.connect(self.newActioncon)

    def createButtons(self):
        self.button = QPushButton("Завершить процесс", self)
        self.button.move(350, 50)
        self.button.setFixedSize(110,30)
        self.button1 = QPushButton("Обновить список", self)
        self.button1.move(350, 90)
        self.button1.setFixedSize(110,30)
        self.button2 = QPushButton("Сохранить", self)
        self.button2.move(350, 130)
        self.button2.setFixedSize(110,30)

        self.button.clicked.connect(self.killProc)
        self.button1.clicked.connect(self.reload)
        self.button2.clicked.connect(self.saveCSV)

    def newActioncon(self):
        pyautogui.hotkey("win", "r")

    def launchThreadClass(self):
        self.ThreadClass_instance.start()
    
    def saveCSV(self):
        data = [{"name":x.cgName}, {"CPU":x.cgCPU}, {"MEM":x.cgMem}]
        with open("list.csv", "w") as file:
            file_writer = csv.DictWriter(file, fieldnames=["name", "CPU", "MEM"], delimiter=";", dialect="excel")
            file_writer.writeheader()
            file_writer.writerows(data)

    def reload(self):
        self.tw.clear()
        x.cgName.clear()
        x.cgCPU.clear()
        x.cgMem.clear()
        self.ThreadClass_instance.terminate()
        self.ThreadClass_instance.start()

    def killProc(self):
        self.killLoop(name=self.tw.currentItem().text(0))
        self.tw.currentItem().removeChild(self.tw.currentItem())

    def loop(self):
        for item in psutil.process_iter():
            cg = QtWidgets.QTreeWidgetItem(self.tw, [item.name(), 
                                                    "{} %".format(item.cpu_percent(interval=0)), 
                                                    "{} MB".format(round(item.memory_info().rss / 1024 / 1024, 3))])
            x.cgName.append(item.name())
            x.cgCPU.append(item.cpu_percent())
            x.cgMem.append(item.memory_info().rss)

    def killLoop(self, name):
        for item in psutil.process_iter(["name"]):
            if item.info["name"] == name:
                item.kill()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())