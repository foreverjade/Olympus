import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView
from Form_Orders import *
from Form_TradingStatus import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class FormOrders(QMainWindow, Ui_Form_Orders):
    def __init__(self, parent=None):
        super(FormOrders, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_Hide.clicked.connect(self.hide)
        self.model = QStandardItemModel(4, 3)
        self.model.setHorizontalHeaderLabels(['id', '姓名', '年龄'])
        self.listView.setModel(self.model)
        item11 = QStandardItem("1")
        item12 = QStandardItem("小明")
        item13 = QStandardItem("20")
        self.model.setItem(0, 0, item11)
        self.model.setItem(0, 1, item12)
        self.model.setItem(0, 2, item13)


class FormTradingStatus(QMainWindow, Ui_Form_TradingStatus):
    def __init__(self, parent=None):
        super(FormTradingStatus, self).__init__(parent)
        self.setupUi(self)
        self.model = QStandardItemModel(4, 3)
        self.model.setHorizontalHeaderLabels(['id', '姓名', '年龄'])
        self.tableView_PnL.setModel(self.model)
        self.tableView_PnL.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_PnL.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView_PnL.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.tableView_PnL.setGridStyle(Qt.)
        item11 = QStandardItem("1")
        item12 = QStandardItem("小明")
        item13 = QStandardItem("20")
        self.model.setItem(0, 0, item11)
        self.model.setItem(0, 1, item12)
        self.model.setItem(0, 2, item13)

    def test(self, item):
        print("You pressed on {0}x{1}".format(item.column(), item.row()))
        self.tableView_PnL.clearSelection()
        self.tableView_PnL.selectRow(item.row())

    def test2(self, item):
        print("clicked")
        self.tableView_PnL.clearSelection()
        self.tableView_PnL.selectRow(item.row())
        pass

    def test3(self, item):
        print("selected clicked")
        pass

if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    test = FormTradingStatus()
    # 将窗口控件显示在屏幕上
    test.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())