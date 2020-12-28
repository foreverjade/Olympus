from SysWindow import *
from SysOrderAgent import *
from SysLog import *
from abc import ABCMeta, abstractmethod


class RuleBase:
    __metaclass__ = ABCMeta

    stg_name = "RuleBase"
    stg_version = "RuleBase_20201125"

    FEED_UL_QUOTE = 1
    FEED_UL_TRADE = 2
    FEED_DERI_QUOTE = 3
    FEED_DERI_TRADE = 4
    FEED_ORDER = 5
    FEED_DEAL = 6

    def __init__(self, derivative, underlying, p_core, window, acc_id, acc_type):
        self.derivative_code = derivative
        self.underlying_code = underlying
        self.region = derivative[0:2]
        self.link_core = p_core
        self.strategy_window = window
        self.trading_account = acc_id
        self.trading_type = acc_type
        self.stg_log = StgLog(self)
        self.order_agent = OrderAgent(self.link_core, self)
        self.update_thread_lock = threading.Lock()

        self.op_bid = 0.0
        self.op_ask = 0.0
        self.op_bidqty = 0
        self.op_askqty = 0
        self.op_bid_lastquote_updatetime = datetime.now()
        self.op_ask_lastquote_updatetime = datetime.now()

        self.ul_bid = 0.0
        self.ul_ask = 0.0
        self.ul_bidqty = 0
        self.ul_askqty = 0
        self.ul_bid_lastquote_updatetime = datetime.now()
        self.ul_ask_lastquote_updatetime = datetime.now()

        self.op_lasttrade_price = 0.0
        self.op_lasttrade_qty = 0
        self.op_lasttrade_direction = ""
        self.op_lasttrade_time = datetime.now()

        self.ul_lasttrade_price = 0.0
        self.ul_lasttrade_qty = 0
        self.ul_lasttrade_direction = ""
        self.ul_lasttrade_time = datetime.now()

        self.orderlist = {}

    def on_feed(self, data, index):
        self.update_thread_lock.acquire()
        if index == RuleBase.FEED_UL_QUOTE:
            self.ul_bid = 0.0 if len(data['Bid'][0]) == 0 else data['Bid'][0][0]
            self.ul_ask = 0.0 if len(data['Ask'][0]) == 0 else data['Ask'][0][0]
            self.ul_bidqty = 0 if len(data['Bid'][0]) == 0 else data['Bid'][0][1]
            self.ul_askqty = 0 if len(data['Ask'][0]) == 0 else data['Ask'][0][1]
            if len(data['svr_recv_time_bid']) > 0:
                self.ul_bid_lastquote_updatetime = auto_strptime(data['svr_recv_time_bid'])
            if len(data['svr_recv_time_ask']) > 0:
                self.ul_ask_lastquote_updatetime = auto_strptime(data['svr_recv_time_ask'])
            self.strategy_window.signal_underlying_quote_update.emit(self.ul_bid, self.ul_ask, self.ul_bidqty,
                                                                     self.ul_askqty)
            self.on_underlying_quote_update()
        elif index == RuleBase.FEED_UL_TRADE:
            self.ul_lasttrade_price = data['price']
            self.ul_lasttrade_qty = data['volume']
            self.ul_lasttrade_direction = data['ticker_direction']
            if len(data['time']) > 0:
                self.ul_lasttrade_time = auto_strptime(data['time'])
            self.strategy_window.signal_underlying_trade_update.emit(self.ul_lasttrade_price,
                                                                     self.ul_lasttrade_qty,
                                                                     self.ul_lasttrade_direction,
                                                                     self.ul_lasttrade_time)
            self.on_underlying_trade_update()
        elif index == RuleBase.FEED_DERI_QUOTE:
            self.op_bid = 0.0 if len(data['Bid'][0]) == 0 else data['Bid'][0][0]
            self.op_ask = 0.0 if len(data['Ask'][0]) == 0 else data['Ask'][0][0]
            self.op_bidqty = 0 if len(data['Bid'][0]) == 0 else data['Bid'][0][1]
            self.op_askqty = 0 if len(data['Ask'][0]) == 0 else data['Ask'][0][1]
            if len(data['svr_recv_time_bid']) > 0:
                self.op_bid_lastquote_updatetime = auto_strptime(data['svr_recv_time_bid'])
            if len(data['svr_recv_time_ask']) > 0:
                self.op_ask_lastquote_updatetime = auto_strptime(data['svr_recv_time_ask'])
            self.strategy_window.signal_derivative_quote_update.emit(self.op_bid, self.op_ask, self.op_bidqty,
                                                                     self.op_askqty)
            self.on_derivative_quote_update()
        elif index == RuleBase.FEED_DERI_TRADE:
            self.op_lasttrade_price = data['price']
            self.op_lasttrade_qty = data['volume']
            self.op_lasttrade_direction = data['ticker_direction']
            if len(data['time']) > 0:
                self.op_lasttrade_time = auto_strptime(data['time'])
            self.strategy_window.signal_derivative_trade_update.emit(self.op_lasttrade_price,
                                                                     self.op_lasttrade_qty,
                                                                     self.op_lasttrade_direction,
                                                                     self.op_lasttrade_time)
            self.on_derivative_trade_update()
        elif index == RuleBase.FEED_ORDER:
            if data['order_status'][0] == OrderStatus.CANCELLED_ALL or \
                    data['order_status'][0] == OrderStatus.CANCELLED_PART:
                self.on_order_canceled_update()
            elif data['order_status'][0] == OrderStatus.SUBMITTED:
                self.on_order_submitted_update()
            elif data['order_status'][0] == OrderStatus.FILLED_ALL or \
                    data['order_status'][0] == OrderStatus.FILLED_PART:
                self.on_order_filled_update()
            elif data['order_status'][0] == OrderStatus.FAILED or \
                    data['order_status'][0] == OrderStatus.SUBMIT_FAILED:
                self.on_order_error_update()
        elif index == RuleBase.FEED_DEAL:
            pass
        self.update_thread_lock.release()
        pass

    @abstractmethod
    def on_underlying_quote_update(self):
        pass

    @abstractmethod
    def on_underlying_trade_update(self):
        pass

    @abstractmethod
    def on_derivative_quote_update(self):
        pass

    @abstractmethod
    def on_derivative_trade_update(self):
        pass

    def on_order_submitted_update(self):
        pass

    def on_order_filled_update(self):
        pass

    def on_order_canceled_update(self):
        pass

    def on_order_error_update(self):
        pass

    def on_deal_update(self):
        pass

    def delete(self):
        pass
