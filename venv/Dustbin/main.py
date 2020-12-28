from PyQt5.QtCore import QAbstractTableModel, Qt, QAbstractListModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt5.QtGui import QFont
from OlympusMain import *
from Form_StrategyTrading import *
from Form_TradingStatus import *
from Form_Orders import *
from venv.Dustbin.USOptionManual import *
from futu import *


class pandasListModel(QAbstractListModel):
    def __init__(self, data):
        QAbstractListModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class FormStrategyTrading(QWidget, Ui_Form_StrategyTrading):
    def __init__(self, main, option, underlying, strategy, acc_id, parent=None):
        super(FormStrategyTrading, self).__init__(parent)
        self.setupUi(self)
        # basic variables
        self.main_window = main
        self.quote_channel = OpenQuoteContext(host=self.main_window.ip, port=self.main_window.port)
        if option[0:2] == 'US':
            self.trade_channel = OpenUSTradeContext(host=self.main_window.ip, port=self.main_window.port)
        elif option[0:2] == 'HK':
            self.trade_channel = OpenHKTradeContext(host=self.main_window.ip, port=self.main_window.port)
        else:
            pass
        self.trade_channel.set_handler(USOptionManualTradeOrder(self))
        self.trade_channel.set_handler(USOptionManualTradeDeal(self))
        self.option_code = option
        self.ul_code = option[0:3] + underlying
        self.strategy_code = strategy
        self.account_id = int(acc_id)
        self.position = 0
        self.label_Position.setText(str(self.position))
        self.profit = 0
        self.label_PnL.setText(str(self.profit))

        self.setWindowTitle(self.strategy_code + ": " + self.option_code)
        self.pushButton_Hide.clicked.connect(self.hide)
        self.pushButton_Delete.clicked.connect(self.close)
        self.expended = False
        self.pushButton_Log.clicked.connect(self.expend)
        self.pushButton_Buy.clicked.connect(self.process_buy)
        self.pushButton_Sell.clicked.connect(self.process_sell)

        self.comboBox_Sync.addItems(['NoSync', 'BidSync', 'AskSync', 'TradeSync'])
        self.comboBox_OrderType.addItems(['Normal'])

        self.out_log("Strategy Create Successfully:" + self.strategy_code)
        self.out_log("Option: " + self.option_code)
        self.out_log("Underlying: " + self.ul_code)

    def process_buy(self):
        print("Push Buy")
        self.trade_channel.unlock_trade(self.main_window.pwd_unlock)
        self.trade_channel.place_order(trd_env=TrdEnv.SIMULATE,
                                       acc_id=self.account_id,
                                       price=self.doubleSpinBox_OrderPrice.value(),
                                       qty=self.spinBox_OrderQty.value(), code=self.option_code, trd_side=TrdSide.BUY)

    def process_sell(self):
        print("Push Sell")
        self.trade_channel.unlock_trade(self.main_window.pwd_unlock)
        self.trade_channel.place_order(trd_env=TrdEnv.SIMULATE,
                                       acc_id=self.account_id,
                                       price=self.doubleSpinBox_OrderPrice.value(),
                                       qty=self.spinBox_OrderQty.value(), code=self.option_code, trd_side=TrdSide.SELL)

    def out_log(self, text):
        time_str = datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%H:%M:%S')
        self.listWidget_Log.insertItem(0, time_str + ' ' + text)

    def expend(self):
        if self.expended:
            self.expended = False
            self.setGeometry(self.geometry().x(), self.geometry().y(), 500, 460)
        else:
            self.expended = True
            self.setGeometry(self.geometry().x(), self.geometry().y(), 500, 650)

    def open(self):
        orderbook_handler = USOptionManualOrderBook(self)
        ticker_handler = USOptionManualTicker(self)
        self.quote_channel.set_handler(orderbook_handler)  # 设置实时摆盘回调
        self.quote_channel.set_handler(ticker_handler)  # 设置实时摆盘回调
        ret_sub, err_message = self.quote_channel.subscribe([self.option_code],
                                                            [SubType.ORDER_BOOK, SubType.TICKER],
                                                            is_first_push=True, extended_time=True)
        if ret_sub == RET_OK:
            self.out_log(
                'subscribe successfully！current subscription status :' + str(self.quote_channel.query_subscription()))
        else:
            self.out_log('subscription failed' + str(err_message))
        self.show()

    def closeEvent(self, event):
        ret_unsub, err_message_unsub = self.quote_channel.unsubscribe([self.option_code],
                                                                      [SubType.ORDER_BOOK, SubType.TICKER,
                                                                       SubType.RT_DATA])
        if ret_unsub == RET_OK:
            self.out_log(
                'unsubscribe all successfully！current subscription status:' + str(
                    self.quote_channel.query_subscription()))  # 取消订阅后查询订阅状态
            self.out_log("Try to delete strategy!")
            self.quote_channel.close()
            self.trade_channel.close()
            self.main_window.pool_formStrategyTrading.remove(self)
            event.accept()
        else:
            self.out_log('Failed to cancel all subscriptions！' + str(err_message_unsub))
            event.ignore()


class FormTradingStatus(QWidget, Ui_Form_TradingStatus):
    def __init__(self, main, parent=None):
        super(FormTradingStatus, self).__init__(parent)
        self.setupUi(self)
        self.main_window = main
        self.pushButton_Hide.clicked.connect(self.hide)


class FormOrders(QWidget, Ui_Form_Orders):
    def __init__(self, main, parent=None):
        super(FormOrders, self).__init__(parent)
        self.setupUi(self)
        self.main_window = main
        self.pushButton_Hide.clicked.connect(self.hide)


class OlympusMainWindow(QMainWindow, Ui_OlympusMain):
    def __init__(self, parent=None):
        super(OlympusMainWindow, self).__init__(parent)
        self.setupUi(self)

        # futu data
        self.ip = '127.0.0.1'
        self.port = 11111
        self.pwd_unlock = '900213'

        self.trd_ctx_us = OpenUSTradeContext(host=self.ip, port=self.port)
        self.trd_ctx_hk = OpenHKTradeContext(host=self.ip, port=self.port)
        self.trd_ctx_current = self.trd_ctx_us
        self.quote_ctx = OpenQuoteContext(host=self.ip, port=self.port)
        self.pool_currentOptions = []
        self.pool_formStrategyTrading = []

        self.form_trading_status = FormTradingStatus(self)
        self.form_orders = FormOrders(self)
        self.action_Trading_Status.triggered.connect(self.menu_open_window_trading_status)
        self.action_Orders.triggered.connect(self.menu_open_window_orders)

        self.comboBox_Region.addItems(["US", "HK", "CN"])
        self.combobox_region_text_changed(self)
        self.comboBox_Region.activated[str].connect(self.combobox_region_text_changed)
        self.comboBox_SubAccount.activated[str].connect(self.combobox_subaccount_text_changed)

        self.tableView_AccountStatus.horizontalHeader().setStyleSheet('QHeaderView::section{background:orange}')
        self.tableView_AccountDetails.horizontalHeader().setStyleSheet('QHeaderView::section{background:orange}')
        font = QFont('微软雅黑', 10)
        font.setBold(True)  # 设置字体加粗
        self.tableView_AccountStatus.horizontalHeader().setFont(font)  # 设置表头字体
        self.tableView_AccountDetails.horizontalHeader().setFont(font)  # 设置表头字体

        self.comboBox_Strategy.addItems(["USOptionManual"])
        self.lineEdit_SecurityCode.editingFinished.connect(self.lineedit_securitycode_text_changed)

        self.pushButton_Create.clicked.connect(self.pushbutton_create_clicked)

    def menu_open_window_trading_status(self):
        self.form_trading_status.show()

    def menu_open_window_orders(self):
        self.form_orders.show()

    def pushbutton_create_clicked(self):
        if len(self.pool_currentOptions) > 0:
            selected = self.listView_OptionChain.currentIndex()
            item = selected.row()
            print(self.pool_currentOptions[item])
            print(self.pool_formStrategyTrading)
            for i in self.pool_formStrategyTrading:
                if i.option_code == self.pool_currentOptions[item]:
                    i.open()
                    break
            else:
                self.pool_formStrategyTrading.append(
                    FormStrategyTrading(main=self, option=self.pool_currentOptions[item],
                                        underlying=self.lineEdit_SecurityCode.text(),
                                        strategy=self.comboBox_Strategy.currentText(),
                                        acc_id=self.comboBox_SubAccount.currentText()))
                self.pool_formStrategyTrading[len(self.pool_formStrategyTrading) - 1].open()
                print("Create new strategy!" + self.pool_currentOptions[item])
        else:
            QMessageBox.warning(self, 'Error', 'No Selected Option!',
                                QMessageBox.Close, QMessageBox.Close)
            return None

    def lineedit_securitycode_text_changed(self):
        data_filter = OptionDataFilter()
        region = self.comboBox_Region.currentText()
        code = self.lineEdit_SecurityCode.text()
        security_code = region + '.'
        if region == 'US':
            if str.isalpha(code):
                security_code += code
            else:
                QMessageBox.warning(self, 'Error', 'Invalid Security Code ' + region + '.' + code + ' for US Market',
                                    QMessageBox.Close, QMessageBox.Close)
                return None
        else:
            if str.isdigit(code):
                if region == 'HK':
                    if 5 >= len(code) > 0:
                        security_code += "".join(['0' for n in range(len(code) - 1)]) + code
                        # self.lineEdit_SecurityCode.setText("".join(['0' for n in range(len(code) - 1)]) + code)
                    else:
                        QMessageBox.warning(self, 'Error',
                                            'Invalid Security Code ' + region + '.' + code + 'for HK Market',
                                            QMessageBox.Close, QMessageBox.Close)
                        return None
            else:
                QMessageBox.warning(self, 'Error', 'Invalid Security Code ' + region + '.' + code + ' for HK/CN Market',
                                    QMessageBox.Close, QMessageBox.Close)
                return None
        ret, data = self.quote_ctx.get_option_chain(security_code, IndexOptionType.NORMAL, '2020-12-01',
                                                    self.dateEdit_ExpireDate.text(), OptionType.ALL, OptionCondType.ALL,
                                                    OptionDataFilter())
        if ret == RET_OK:
            if len(data) > 0:
                self.listView_OptionChain.setModel(pandasListModel(pd.DataFrame(data)))
            else:
                QMessageBox.warning(self, 'Error', 'No Option Found!',
                                    QMessageBox.Close, QMessageBox.Close)
            self.pool_currentOptions = data['code'].values.tolist()  # 转为list
        else:
            QMessageBox.warning(self, 'Error', data,
                                QMessageBox.Close, QMessageBox.Close)

    def combobox_subaccount_text_changed(self, text):
        self.trd_ctx_current = self.trd_ctx_us
        if self.comboBox_Region.currentText() == 'US':
            self.trd_ctx_current = self.trd_ctx_us
        elif self.comboBox_Region.currentText() == 'HK':
            self.trd_ctx_current = self.trd_ctx_hk
        else:
            pass
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        environment = TrdEnv.SIMULATE if int(text) < 99999999 else TrdEnv.REAL
        ret, data = self.trd_ctx_current.accinfo_query(trd_env=environment, acc_id=int(text))
        if ret == RET_OK:
            self.tableView_AccountDetails.setModel(pandasModel(pd.DataFrame(data)))
        else:
            QMessageBox.warning(self, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def combobox_region_text_changed(self, text):
        self.trd_ctx_current = self.trd_ctx_us
        if text == 'US':
            self.trd_ctx_current = self.trd_ctx_us
        elif text == 'HK':
            self.trd_ctx_current = self.trd_ctx_hk
        ret, data = self.trd_ctx_current.get_acc_list()
        if ret == RET_OK:
            self.tableView_AccountStatus.setModel(pandasModel(pd.DataFrame(data)))
            self.comboBox_SubAccount.clear()
            self.comboBox_SubAccount.addItems(list(data['acc_id'].apply(str)))
            self.trd_ctx_current.unlock_trade(self.pwd_unlock)
            ret2, data2 = self.trd_ctx_current.accinfo_query(acc_index=0)
            if ret2 == RET_OK:
                self.tableView_AccountDetails.setModel(pandasModel(pd.DataFrame(data2)))
            else:
                QMessageBox.warning(self, 'Error', data2, QMessageBox.Close, QMessageBox.Close)
        else:
            QMessageBox.warning(self, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Warning', "Confirm to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:

            self.form_trading_status.close()
            self.form_orders.close()

            self.trd_ctx_us.close()
            self.trd_ctx_hk.close()
            self.quote_ctx.close()
            print("Destruction Function!")
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    olympusWin = OlympusMainWindow()
    # 将窗口控件显示在屏幕上
    olympusWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
