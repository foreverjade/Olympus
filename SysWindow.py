from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QMenu
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from SysLog import WinLog
from SysFunction import *
from Form_Orders import *
from Form_TradingStatus import *
from Form_StrategyTrading import *
from OlympusMain import *
from SysModel import *
from futu import *


class OlympusMainWindow(QMainWindow, Ui_OlympusMain):
    def __init__(self, p_core, parent=None):
        super(OlympusMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.link_core = p_core
        self.current_security_code = ""

        self.setFixedSize(self.width(), self.height())
        self.form_trading_status = FormTradingStatus(self)
        self.form_orders = FormOrders(self)
        self.action_OutputOrderBookData.triggered.connect(self.action_data_triggered)
        self.action_OutputTickerData.triggered.connect(self.action_data_triggered)
        self.action_RecordDealData.triggered.connect(self.action_data_triggered)
        self.action_RecordOrderData.triggered.connect(self.action_data_triggered)
        self.action_data_triggered()
        self.action_Trading_Status.triggered.connect(self.form_trading_status.show)
        self.action_Orders.triggered.connect(self.form_orders.show)
        self.action_VersionInfo.triggered.connect(self.action_versioninfo_triggered)

        self.comboBox_Region.addItems(["US", "HK", "CN"])
        self.combobox_region_text_changed()
        self.comboBox_Region.activated[str].connect(self.combobox_region_text_changed)
        self.comboBox_SubAccount.activated[str].connect(self.combobox_subaccount_text_changed)
        self.tableView_AccountStatus.horizontalHeader().setStyleSheet('QHeaderView::section{background:orange}')
        self.tableView_AccountDetails.horizontalHeader().setStyleSheet('QHeaderView::section{background:orange}')
        self.tableView_AccountStatus.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_AccountDetails.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_OptionChain.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.tableView_AccountStatus.horizontalHeader().setFont(QFont('微软雅黑', 10).setBold(True))  # 设置表头字体
        # self.tableView_AccountDetails.horizontalHeader().setFont(QFont('微软雅黑', 10).setBold(True))  # 设置表头字体

        self.comboBox_Strategy.addItems(["RuleUSOptionManual"])
        self.lineEdit_SecurityCode.editingFinished.connect(self.lineedit_securitycode_text_changed)

        self.pushButton_Create.clicked.connect(self.pushbutton_create_clicked)

    #
    # def subwindow_open_trading_status(self):
    #     self.form_trading_status.show()
    #
    # def subwindow_open_orders(self):
    #     self.form_orders.show()

    def action_data_triggered(self):
        self.link_core.quote_handler.b_dataRecord = self.action_OutputOrderBookData.isChecked()
        self.link_core.ticker_handler.b_dataRecord = self.action_OutputTickerData.isChecked()
        self.link_core.order_handler.b_dataRecord = self.action_RecordOrderData.isChecked()
        self.link_core.deal_handler.b_dataRecord = self.action_RecordDealData.isChecked()

    def action_versioninfo_triggered(self):
        QMessageBox.about(self, 'Version', self.link_core.version + "\n" + self.link_core.heart)

    def pushbutton_create_clicked(self):
        if len(self.link_core.data_option_chain) > 0 and self.tableView_OptionChain.currentIndex().row() >= 0:
            self.link_core.create_strategy(
                self.comboBox_Strategy.currentText(),
                self.link_core.data_option_chain['code'][self.tableView_OptionChain.currentIndex().row()],
                self.current_security_code,
                int(self.comboBox_SubAccount.currentText()),
                acc_type=TrdEnv.REAL if int(self.comboBox_SubAccount.currentText()) > 99999999 else TrdEnv.SIMULATE)

    def lineedit_securitycode_text_changed(self):
        region = self.comboBox_Region.currentText()
        code = self.lineEdit_SecurityCode.text()
        security_code = region + '.'
        if region == 'US':
            if str.isalpha(code):
                security_code += code
            else:
                QMessageBox.warning(self, 'Error', 'Invalid Security Code ' + region + '.' + code + ' for US Market',
                                    QMessageBox.Close, QMessageBox.Close)
        else:
            if str.isdigit(code):
                if region == 'HK':
                    if 5 > len(code) > 0:
                        security_code += "".join(['0' for n in range(5 - len(code))]) + code
                    else:
                        QMessageBox.warning(self, 'Error',
                                            'Invalid Security Code ' + region + '.' + code + 'for HK Market',
                                            QMessageBox.Close, QMessageBox.Close)
            else:
                QMessageBox.warning(self, 'Error', 'Invalid Security Code ' + region + '.' + code + ' for HK/CN Market',
                                    QMessageBox.Close, QMessageBox.Close)

        self.current_security_code = security_code
        self.link_core.get_option_chain(security_code, self.dateEdit_ExpireDate.text())
        self.update_data()

    def combobox_subaccount_text_changed(self):
        self.link_core.accinfo_query(self.comboBox_SubAccount.currentText())
        self.update_data()

    def combobox_region_text_changed(self):
        self.link_core.get_acc_list(self.comboBox_Region.currentText())
        self.update_data(0)

    def update_data(self, index=1):
        self.tableView_AccountStatus.setModel(PandasTableModel(pd.DataFrame(self.link_core.data_account_status)))
        self.tableView_AccountDetails.setModel(PandasTableModel(pd.DataFrame(self.link_core.data_account_details)))
        if index == 0 and 'acc_id' in self.link_core.data_account_status.columns:
            self.comboBox_SubAccount.clear()
            self.comboBox_SubAccount.addItems(list(self.link_core.data_account_status['acc_id'].apply(str)))
        if len(self.link_core.data_option_chain) > 0:
            self.tableView_OptionChain.setModel(PandasTableModel(pd.DataFrame(self.link_core.data_option_chain)))
        else:
            self.tableView_OptionChain.setModel(PandasTableModel(pd.DataFrame({})))
        if len(self.link_core.data_position_list) > 0:
            self.form_trading_status.tableView_Position.setModel(
                PandasTableModel(pd.DataFrame(self.link_core.data_position_list)))
        else:
            self.form_trading_status.tableView_Position.setModel(PandasTableModel(pd.DataFrame({})))
        if len(self.link_core.data_order_list) > 0:
            self.form_orders.tableView_CurrentOrders.setModel(
                PandasTableModel(pd.DataFrame(self.link_core.data_order_list)))
        else:
            self.form_orders.tableView_CurrentOrders.setModel(PandasTableModel(pd.DataFrame({})))
        if len(self.link_core.data_historical_order_list) > 0:
            self.form_orders.tableView_HistoricalOrders.setModel(
                PandasTableModel(pd.DataFrame(self.link_core.data_historical_order_list)))
        else:
            self.form_orders.tableView_HistoricalOrders.setModel(PandasTableModel(pd.DataFrame({})))
        if len(self.link_core.data_deal_list) > 0:
            self.form_trading_status.tableView_TradingHistory.setModel(
                PandasTableModel(pd.DataFrame(self.link_core.data_deal_list)))
        else:
            self.form_trading_status.tableView_TradingHistory.setModel(PandasTableModel(pd.DataFrame({})))

    def err_msg_box(self, test):
        QMessageBox.warning(self, 'Error', test, QMessageBox.Close, QMessageBox.Close)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Warning', "Confirm to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.form_trading_status.close()
            self.form_orders.close()
            print("Destruction Function!")
            self.link_core.__del__()
            event.accept()
        else:
            event.ignore()


class FormStrategyTrading(QWidget, Ui_Form_StrategyTrading):
    _signal = QtCore.pyqtSignal(str)

    signal_derivative_quote_update = QtCore.pyqtSignal(float, float, int, int)
    signal_derivative_trade_update = QtCore.pyqtSignal(float, int, str, datetime)
    signal_underlying_quote_update = QtCore.pyqtSignal(float, float, int, int)
    signal_underlying_trade_update = QtCore.pyqtSignal(float, int, str, datetime)
    signal_order_update = QtCore.pyqtSignal(pd.DataFrame, int)

    def __init__(self, main, derivative, parent=None):
        super(FormStrategyTrading, self).__init__(parent)
        self.setupUi(self)
        self.main_window = main
        self.link_core = self.main_window.link_core
        self.derivative_code = derivative
        self.strategy_instance = None
        self.win_log = WinLog(self)
        self.timer = QTimer()
        self.expended = False
        self.order_queue = {}

        self.ul_bid = 0.0
        self.ul_ask = 0.0
        self.op_bid = 0.0
        self.op_ask = 0.0
        self.day_to_expire = 0.0
        self.delta = 0.0
        self.strike = 0.0
        self.type = ""
        self.order_price = 0.0
        self.order_qty = 0.0
        self.order_ratio = 0
        self.position = 0
        self.profit = 0
        self.setWindowTitle("Strategy: " + self.derivative_code)
        self.label_PnL.setText(str(self.profit))
        self.label_Position.setText(str(self.position))
        self.comboBox_OrderType.addItems(['NORMAL'])
        self.comboBox_Sync.addItems(['NoSync', 'BidSync', 'AskSync', 'TradeSync'])
        self.comboBox_Mode.addItems(['Ratio', 'QTY'])
        self.timer.setInterval(1000)

        # self.setFixedSize(self.width(), self.height())
        self.timer.timeout.connect(self.on_timer_out)
        self.comboBox_Sync.activated[str].connect(self.combobox_sync_text_changed)
        self.spinBox_OrderQty.valueChanged.connect(self.input_update)
        self.doubleSpinBox_OrderPrice.valueChanged.connect(self.input_update)
        self.pushButton_Log.clicked.connect(self.expend)
        self.pushButton_Buy.clicked.connect(self.process_buy)
        self.pushButton_Sell.clicked.connect(self.process_sell)
        self.pushButton_Hide.clicked.connect(self.hide)
        self.pushButton_Delete.clicked.connect(self.close)
        self.listWidget_CurrentOrder.customContextMenuRequested.connect(self.menu_right_order)

        self.signal_derivative_quote_update.connect(self.derivative_quote_update)
        self.signal_derivative_trade_update.connect(self.derivative_trade_update)
        self.signal_underlying_quote_update.connect(self.underlying_quote_update)
        self.signal_underlying_trade_update.connect(self.underlying_trade_update)
        self.signal_order_update.connect(self.on_order_update)

    def menu_right_order(self, pos):
        menu = QMenu()
        opt1 = menu.addAction("Cancel")
        action = menu.exec_(self.listWidget_CurrentOrder.mapToGlobal(pos))
        if action == opt1:
            order_id = list(self.order_queue.keys())[self.listWidget_CurrentOrder.currentIndex().row()]
            self.link_core.modify_order(order_id=order_id,
                                        acc_id=self.strategy_instance.trading_account,
                                        modifyorderop=ModifyOrderOp.CANCEL)
            self.win_log.log_out("Cancel Order:" + str(order_id))
            return
        else:
            return

    def status_check(self):
        self.win_log.log_out("Strategy Created: " + self.strategy_instance.stg_version, 1)
        self.win_log.log_out("Product: " + self.strategy_instance.derivative_code, 1)
        self.win_log.log_out("Underlying: " + self.strategy_instance.underlying_code, 1)
        self.win_log.log_out("Account: " + str(self.strategy_instance.trading_account), 1)

        position_list = self.link_core.position_list_query(code=self.derivative_code,
                                                           acc_id=self.strategy_instance.trading_account,
                                                           acc_type=self.strategy_instance.trading_type)
        if len(position_list) > 0:
            self.position = position_list['qty'][0] \
                if position_list['position_side'][0] == PositionSide.LONG else 0 - position_list['qty'][0]
            self.label_Position.setText(str(self.position))
            self.win_log.log_out("Position Updated: " + str(position_list['position_side'][0]) + ' ' +
                                 str(position_list['qty'][0]) + '@' +
                                 str(position_list['cost_price'][0])
                                 , 1)
            self.profit = position_list['pl_val'][0]
            self.label_PnL.setText(str(self.profit))
            self.win_log.log_out("Profit Updated: " + str(position_list['pl_val'][0]), 1)

        if self.derivative_code in self.link_core.sys_ord_mgr.dict_dev2orders:
            order_group = self.link_core.sys_ord_mgr.dict_orders
            for ord in self.link_core.sys_ord_mgr.dict_dev2orders[self.derivative_code]:
                trd_side = order_group[ord][1]
                order_status = order_group[ord][3]
                qty = order_group[ord][4]
                price = order_group[ord][5]
                date_str = auto_strptime(order_group[ord][6]).strftime('%X')
                str_list = date_str + ' ' + str(qty) + '@' + str(price) + " " + trd_side + " " + order_status
                self.order_queue[ord] = [str_list, 'green' if order_status == 'FILLED_ALL' else 'yellow']
            for line in self.order_queue.values():
                n = self.listWidget_CurrentOrder.count()
                self.listWidget_CurrentOrder.insertItem(0, line[0])
                self.listWidget_CurrentOrder.item(0).setBackground(QColor(line[1]))
                if self.listWidget_CurrentOrder.count() >= 10:
                    self.listWidget_CurrentOrder.takeItem(0)
            self.win_log.log_out("Orders Updated: " +
                                 str(len(self.link_core.sys_ord_mgr.dict_dev2orders[self.derivative_code])) +
                                 " orders in total",
                                 1)

        ret, product_info = self.link_core.get_market_snapshot(security_code=self.derivative_code)
        if ret == RET_OK:
            self.day_to_expire = (datetime.strptime(product_info['strike_time'][0],
                                                    "%Y-%m-%d") - datetime.now()).days + 1
            self.delta = product_info['option_delta'][0]
            self.strike = product_info['option_strike_price'][0]
            self.type = product_info['option_type'][0]
            self.win_log.log_out("Expiration: " + str(self.day_to_expire) + " days", 1)
            self.win_log.log_out("Delta: " + str(self.delta), 1)
            self.win_log.log_out("Strike: " + str(self.strike), 1)
        else:
            self.win_log.log_out("Failed to get product info!", 3)
        self.timer.start()

    def derivative_quote_update(self, op_bid, op_ask, op_bidqty, op_askqty):
        self.op_bid = op_bid
        self.op_ask = op_ask
        self.label_OptionBid_1.setText(str(op_bid))
        self.label_OptionAsk_1.setText(str(op_ask))
        self.label_OptionBidQty_1.setText(str(op_bidqty))
        self.label_OptionAskQty_1.setText(str(op_askqty))
        # if self.strategy_window.comboBox_Sync.currentText() == 'TradeSync':
        #     self.strategy_window.doubleSpinBox_OrderPrice.setValue(self.f_opLastTradePrice)
        if self.comboBox_Sync.currentText() == 'BidSync':
            self.doubleSpinBox_OrderPrice.setValue(op_bid)
        elif self.comboBox_Sync.currentText() == 'AskSync':
            self.doubleSpinBox_OrderPrice.setValue(op_ask)

    def derivative_trade_update(self, op_lasttrade_price, op_lasttrade_qty, op_lasttrade_direction, op_lasttrade_time):
        date_str = op_lasttrade_time.strftime('%H:%M:%S')
        self.listWidget_OptionTicker.insertItem(0, date_str + ' ' + str(op_lasttrade_qty) + '@' +
                                                str(op_lasttrade_price) + " " + op_lasttrade_direction)
        if op_lasttrade_direction == 'SELL':
            self.listWidget_OptionTicker.item(0).setBackground(QColor('red'))
        elif op_lasttrade_direction == 'BUY':
            self.listWidget_OptionTicker.item(0).setBackground(QColor('green'))
        else:
            pass
        if self.listWidget_OptionTicker.count() >= 10:
            self.listWidget_OptionTicker.takeItem(self.listWidget_OptionTicker.count())
        if self.comboBox_Sync.currentText() == 'TradeSync':
            self.doubleSpinBox_OrderPrice.setValue(op_lasttrade_price)

    def underlying_quote_update(self, ul_bid, ul_ask, ul_bidqty, ul_askqty):
        self.ul_bid = ul_bid
        self.ul_ask = ul_ask
        self.label_ULBid_1.setText(str(ul_bid))
        self.label_ULAsk_1.setText(str(ul_ask))
        self.label_ULBidQty_1.setText(str(ul_bidqty))
        self.label_ULAskQty_1.setText(str(ul_askqty))
        if ul_bidqty + ul_askqty > 0:
            process_ratio = float(ul_bidqty) / (ul_bidqty + ul_askqty)
            self.label_RatioTotal.setText(str(round(process_ratio * 100)) + " %")
            self.label_Ratio.setGeometry(self.label_Ratio.geometry().x(),
                                         self.label_Ratio.geometry().y(),
                                         round(self.label_RatioTotal.geometry().width() * process_ratio),
                                         self.label_Ratio.geometry().height())
        # else:
        #     self.label_RatioTotal.setText("0 %")
        #     self.label_Ratio.setGeometry(self.label_Ratio.geometry().x(),
        #                                  self.label_Ratio.geometry().y(),
        #                                  1,
        #                                  self.label_Ratio.geometry().height())

    def underlying_trade_update(self, ul_lasttrade_price, ul_lasttrade_qty, ul_lasttrade_direction, ul_lasttrade_time):
        date_str = ul_lasttrade_time.strftime('%H:%M:%S')
        self.listWidget_ULTicker.insertItem(0, date_str + ' ' + str(ul_lasttrade_qty) + '@' +
                                            str(ul_lasttrade_price) + " " + ul_lasttrade_direction)
        if ul_lasttrade_direction == 'SELL':
            self.listWidget_ULTicker.item(0).setBackground(QColor('red'))
        elif ul_lasttrade_direction == 'BUY':
            self.listWidget_ULTicker.item(0).setBackground(QColor('green'))
        else:
            pass
        if self.listWidget_ULTicker.count() >= 10:
            self.listWidget_ULTicker.takeItem(self.listWidget_ULTicker.count())
        pass

    def process_buy(self):
        if self.checkBox_PriceBound.isChecked():
            self.order_price = min(self.order_price, self.op_bid + self.doubleSpinBox_PriceBound.value())
            self.win_log.log_out("Order Price Adjusted to " + str(self.order_price), 1)
        self.link_core.create_order(self.strategy_instance, self.order_price, self.order_qty, TrdSide.BUY)

    def process_sell(self):
        if self.checkBox_PriceBound.isChecked():
            self.order_price = max(self.order_price, self.op_ask - self.doubleSpinBox_PriceBound.value())
            self.win_log.log_out("Order Price Adjusted to " + str(self.order_price), 1)
        self.link_core.create_order(self.strategy_instance, self.order_price, self.order_qty, TrdSide.SELL)

    def combobox_sync_text_changed(self):
        if self.comboBox_Sync.currentText() == 'BidSync':
            self.doubleSpinBox_OrderPrice.setValue(float(self.label_OptionBid_1.text()))
        elif self.comboBox_Sync.currentText() == 'AskSync':
            self.doubleSpinBox_OrderPrice.setValue(float(self.label_OptionAsk_1.text()))

    def input_update(self):
        self.order_price = round(self.doubleSpinBox_OrderPrice.value(), 3)
        self.order_qty = self.spinBox_OrderQty.value()
        # self.win_log.log_out("Value Update", 1)

    def expend(self):
        if self.expended:
            self.expended = False
            self.setGeometry(self.geometry().x(), self.geometry().y(), 760, 460)
        else:
            self.expended = True
            self.setGeometry(self.geometry().x(), self.geometry().y(), 760, 650)

    def on_timer_out(self):
        if self.strategy_instance.region == 'US':
            self.lcdNumber_Time.display(datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%X'))
        else:
            self.lcdNumber_Time.display(datetime.now().strftime('%X'))
        self.label_IV_Bid.setText(str(round(cal_implied_volatility(self.day_to_expire,
                                                                   self.ul_ask,
                                                                   self.strike,
                                                                   self.op_bid,
                                                                   self.type), 2)))
        self.label_IV_Ask.setText(str(round(cal_implied_volatility(self.day_to_expire,
                                                                   self.ul_bid,
                                                                   self.strike,
                                                                   self.op_ask,
                                                                   self.type), 2)))

    def on_order_update(self, data, action=0):  # action:[0:add/update]
        if action == 0:
            trd_side = data['trd_side'][0]
            order_status = data['order_status'][0]
            qty = data['qty'][0]
            price = round(data['price'][0], 3)
            date_str = auto_strptime(data['create_time'][0]).strftime('%X')
            str_list = date_str + ' ' + str(qty) + '@' + str(price) + " " + trd_side + " " + order_status
            if data['order_id'][0] in self.order_queue:
                self.order_queue[data['order_id'][0]] = \
                    [str_list, 'green' if order_status == OrderStatus.FILLED_ALL else 'yellow']
            else:
                dict_temp = {data['order_id'][0]: [str_list,
                                                   'green' if order_status == OrderStatus.FILLED_ALL else 'yellow']}
                dict_temp.update(self.order_queue)
                self.order_queue = dict_temp
        else:
            if data['order_id'][0] in self.order_queue.keys():
                self.order_queue.pop(data['order_id'][0])
        self.listWidget_CurrentOrder.clear()
        for line in self.order_queue.values():
            n = self.listWidget_CurrentOrder.count()
            self.listWidget_CurrentOrder.insertItem(0, line[0])
            self.listWidget_CurrentOrder.item(0).setBackground(QColor(line[1]))
            if self.listWidget_CurrentOrder.count() >= 10:
                self.listWidget_CurrentOrder.takeItem(0)

    def closeEvent(self, event):
        if self.link_core.delete_strategy(self.strategy_instance.derivative_code,
                                          self.strategy_instance.underlying_code):
            event.accept()
        else:
            self.win_log.log_out("At least subscribe for 1 min！", 3)
            event.ignore()


class FormTradingStatus(QWidget, Ui_Form_TradingStatus):
    def __init__(self, main, parent=None):
        super(FormTradingStatus, self).__init__(parent)
        self.setupUi(self)
        self.main_window = main
        self.setFixedSize(self.width(), self.height())
        self.pushButton_Hide.clicked.connect(self.hide)
        self.pushButton_Refresh.clicked.connect(self.refresh)
        self.tableView_Position.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_PnL.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_TradingHistory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def refresh(self):
        self.main_window.combobox_subaccount_text_changed()


class FormOrders(QWidget, Ui_Form_Orders):
    def __init__(self, main, parent=None):
        super(FormOrders, self).__init__(parent)
        self.setupUi(self)
        self.main_window = main
        self.setFixedSize(self.width(), self.height())
        self.pushButton_Hide.clicked.connect(self.hide)
        self.pushButton_CancelOrder.clicked.connect(self.cancel_order)
        self.pushButton_Refresh.clicked.connect(self.refresh)
        self.tableView_HistoricalOrders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_CurrentOrders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def cancel_order(self):
        i = self.tableView_CurrentOrders.currentIndex().row()
        if i >= 0:
            order_id = self.main_window.link_core.data_order_list.at[i, 'order_id']
            acc_id = int(self.main_window.comboBox_SubAccount.currentText())
            self.main_window.link_core.modify_order(order_id, acc_id, ModifyOrderOp.CANCEL)

    def refresh(self):
        self.main_window.combobox_subaccount_text_changed()
