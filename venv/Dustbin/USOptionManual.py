import time
from futu import *
import tkinter as tk
import pandas as pd
import pytz
from datetime import datetime
from PyQt5.QtGui import QColor


class USOptionManualOrderBook(OrderBookHandlerBase):
    def __init__(self, strategywin):  # member variables
        OrderBookHandlerBase.__init__(self)
        # variables for calculation
        self.f_opBidPrice1 = 0.0
        self.f_opAskPrice1 = 0.0
        self.f_opBidQty1 = 0.0
        self.f_opAskQty1 = 0.0

        # variables for control
        self.b_dataRecord = False

        # variables for front end display
        self.strategy_window = strategywin

        # variables for Data Storage
        self.df_data = pd.DataFrame({})

    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(USOptionManualOrderBook, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("USOptionManual: error, msg: %s" % data)
            return RET_ERROR, data
        print("USOptionManual ", data)
        if self.b_dataRecord:
            self.df_data = self.df_data.append(pd.DataFrame(data))
        if len(data['Bid']) > 0:
            self.f_opBidPrice1 = data['Bid'][0][0]
            self.f_opBidQty1 = data['Bid'][0][1]
            self.strategy_window.label_OptionBid_1.setText(str(self.f_opBidPrice1))
            self.strategy_window.label_OptionBidQty_1.setText(str(self.f_opBidQty1))
        if len(data['Ask']) > 0:
            self.f_opAskPrice1 = data['Ask'][0][0]
            self.f_opAskQty1 = data['Ask'][0][1]
            self.strategy_window.label_OptionAsk_1.setText(str(self.f_opAskPrice1))
            self.strategy_window.label_OptionAskQty_1.setText(str(self.f_opAskQty1))
        if self.strategy_window.comboBox_Sync.currentText() == 'BidSync':
            self.strategy_window.doubleSpinBox_OrderPrice.setValue(self.f_opBidPrice1)
        elif self.strategy_window.comboBox_Sync.currentText() == 'AskSync':
            self.strategy_window.doubleSpinBox_OrderPrice.setValue(self.f_opAskPrice1)
        return RET_OK, data


class USOptionManualTicker(TickerHandlerBase):
    def __init__(self, strategywin):  # member variables
        TickerHandlerBase.__init__(self)
        # variables for calculation
        self.f_opLastTradePrice = 0.0
        self.f_opLastTradeQty = 0.0
        self.f_opLastTradeDirection = ""
        self.f_opLastTradeTime = ""

        # variables for control
        self.b_dataRecord = False

        # variables for front end display
        self.strategy_window = strategywin

        # variables for Data Storage
        self.df_data = pd.DataFrame({})

    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(USOptionManualTicker, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data)  # TickerTest自己的处理逻辑
        if self.b_dataRecord:
            self.df_data = self.df_data.append(pd.DataFrame(data))
        print(data)
        date_str = datetime.strptime(data['time'][0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')

        self.f_opLastTradePrice = data['price'][0]
        self.f_opLastTradeQty = data['volume'][0]
        self.f_opLastTradeDirection = data['ticker_direction'][0]
        self.f_opLastTradeTime = data['time'][0]

        self.strategy_window.listWidget_OptionTicker.insertItem(0, date_str + ' ' + str(
            self.f_opLastTradeQty) + '@' + str(
            self.f_opLastTradePrice) + " " + self.f_opLastTradeDirection)
        if self.f_opLastTradeDirection == 'SELL':
            self.strategy_window.listWidget_OptionTicker.item(0).setBackground(QColor('red'))
        else:
            self.strategy_window.listWidget_OptionTicker.item(0).setBackground(QColor('green'))
        if self.strategy_window.comboBox_Sync.currentText() == 'TradeSync':
            self.strategy_window.doubleSpinBox_OrderPrice.setValue(self.f_opLastTradePrice)
        return RET_OK, data


class USOptionManualTradeOrder(TradeOrderHandlerBase):
    """ order update push"""

    def __init__(self, strategywin):  # member variables
        TradeOrderHandlerBase.__init__(self)
        # variables for front end display
        self.strategy_window = strategywin
        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

    def on_recv_rsp(self, rsp_pb):
        ret, content = super(USOptionManualTradeOrder, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            self.order_id = content['order_id'][0]
            self.code = content['code'][0]
            self.order_qty = content['qty'][0]
            self.order_price = content['price'][0]
            self.order_trd_side = content['trd_side'][0]
            self.order_order_status = content['order_status'][0]
            self.order_create_time = content['create_time'][0]
            self.strategy_window.out_log("Order:" + str(self.order_qty) + "@" + str(self.order_price) + " " + str(
                self.order_trd_side) + "," + str(self.order_order_status) + "," + self.order_create_time)

            if self.order_order_status == 'FILLED_ALL':
                if len(self.order_create_time) > 19:
                    date_str = datetime.strptime(self.order_create_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M:%S')
                else:
                    date_str = datetime.strptime(self.order_create_time, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                self.strategy_window.listWidget_TradingHistory.insertItem(0, date_str + ' ' + str(
                    self.order_qty) + '@' + str(
                    self.order_price) + " " + self.order_trd_side)
                if self.order_trd_side == 'SELL':
                    self.strategy_window.position -= self.order_qty
                    self.strategy_window.profit += self.order_qty * self.order_price * 100
                    self.strategy_window.label_Position.setText(str(self.strategy_window.position))
                    self.strategy_window.label_PnL.setText(str(round(self.strategy_window.profit)))
                    self.strategy_window.listWidget_TradingHistory.item(0).setBackground(QColor('red'))
                else:
                    self.strategy_window.position += self.order_qty
                    self.strategy_window.profit -= self.order_qty * self.order_price * 100
                    self.strategy_window.label_Position.setText(str(self.strategy_window.position))
                    self.strategy_window.label_PnL.setText(str(round(self.strategy_window.profit)))
                    self.strategy_window.listWidget_TradingHistory.item(0).setBackground(QColor('green'))
        else:
            self.strategy_window.out_log(content)
        return ret, content


class USOptionManualTradeDeal(TradeDealHandlerBase):
    """ order update push"""

    def __init__(self, strategywin):  # member variables
        TradeDealHandlerBase.__init__(self)
        # variables for front end display
        self.strategy_window = strategywin
        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

    def on_recv_rsp(self, rsp_pb):
        ret, content = super(USOptionManualTradeDeal, self).on_recv_rsp(rsp_pb)
        if ret == RET_OK:
            self.order_id = content['order_id'][0]
            self.code = content['code'][0]
            self.order_qty = content['qty'][0]
            self.order_price = content['price'][0]
            self.order_trd_side = content['trd_side'][0]
            self.order_order_status = content['order_status'][0]
            self.order_create_time = content['create_time'][0]
            self.strategy_window.out_log("Deal:" + str(self.order_qty) + "@" + str(self.order_price) + " " + str(
                self.order_trd_side) + "," + str(self.order_order_status) + "," + self.order_create_time)
        else:
            self.strategy_window.out_log(content)
        return ret, content
