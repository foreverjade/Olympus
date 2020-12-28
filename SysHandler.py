import time
from futu import *
import tkinter as tk
import pandas as pd
import pytz
from datetime import datetime
from PyQt5.QtGui import QColor


class OrderBookHandler(OrderBookHandlerBase):
    def __init__(self, main, file):  # member variables
        OrderBookHandlerBase.__init__(self)
        # variables for control
        self.b_dataRecord = False
        # variables for front end display
        self.link_core = main
        # variables for Data Storage
        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("USOptionManual: error, msg: %s" % data)
            return RET_ERROR, data
        if data['Bid'] == []: data["Bid"] = [()]
        if data['Ask'] == []: data["Ask"] = [()]
        # print("OrderBook ", data)
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_orderbook(data)
        return RET_OK, data


class TickerHandler(TickerHandlerBase):
    def __init__(self, main, file):  # member variables
        TickerHandlerBase.__init__(self)
        # variables for control
        self.b_dataRecord = False

        # variables for front end display
        self.link_core = main

        # variables for Data Storage
        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        # print("Ticker ", data.to_dict('list'))
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_ticker(data)

        return RET_OK, data


class TradeOrderHandler(TradeOrderHandlerBase):
    """ order update push"""

    def __init__(self, main, file):  # member variables
        TradeOrderHandlerBase.__init__(self)
        # variables for front end display
        self.link_core = main
        self.b_dataRecord = False

        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_pb):
        ret, data = super(TradeOrderHandler, self).on_recv_rsp(rsp_pb)
        if ret != RET_OK:
            print("OrderTest: error, msg: %s" % data)
            return RET_ERROR, data
        # print("Order ", data.to_dict('list'))
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_order(data)
        return RET_OK, data


class TradeDealHandler(TradeDealHandlerBase):
    """ order update push"""

    def __init__(self, main, file):  # member variables
        TradeDealHandlerBase.__init__(self)
        # variables for front end display
        self.link_core = main
        self.b_dataRecord = False

        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_pb):
        ret, data = super(TradeDealHandler, self).on_recv_rsp(rsp_pb)
        if ret != RET_OK:
            print("DealTest: error, msg: %s" % data)
            return RET_ERROR, data
        # print("Deal ", data.to_dict('list'))
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_deal(data)
        return RET_OK, data
