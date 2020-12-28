#  the core part of Olympus Trading System

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from SysManager import *
from SysLog import *
from SysHandler import *
from futu import *
from SysWindow import *
# import cgitb
#
# cgitb.enable(format='text')
#
# import threading



class Core:
    version = "Olympus Alpha 0.3.1228"
    heart = "For my forever love, Ying"

    # login info
    ip = '127.0.0.1'
    port = 11111
    pwd_unlock = '900213'

    def __init__(self):
        # sub systems
        self.sys_file = SysFileManager(self)
        self.sys_log = SysLog(self)
        self.sys_stg_mgr = SysStrategyManager(self)
        self.sys_pos_mgr = SysPositionManager(self)
        self.sys_ord_mgr = SysOrderManager(self)
        self.sys_log.log_out("Subsystems Launched Successfully!")

        # futu component
        self.quote_ctx = OpenQuoteContext(host=Core.ip, port=Core.port)
        self.quote_handler = OrderBookHandler(self, self.sys_file.file_quote_handler_output)
        self.ticker_handler = TickerHandler(self, self.sys_file.file_ticker_handler_output)
        self.quote_ctx.set_handler(self.quote_handler)
        self.quote_ctx.set_handler(self.ticker_handler)

        self.trd_ctx_us = OpenUSTradeContext(host=Core.ip, port=Core.port)
        self.trd_ctx_hk = OpenHKTradeContext(host=Core.ip, port=Core.port)
        self.trd_ctx_cn = OpenCNTradeContext(host=Core.ip, port=Core.port)
        self.trd_ctx_current = self.trd_ctx_us
        self.order_handler = TradeOrderHandler(self, self.sys_file.file_order_handler_output)
        self.deal_handler = TradeDealHandler(self, self.sys_file.file_deal_handler_output)
        self.trd_ctx_us.set_handler(self.order_handler)
        self.trd_ctx_us.set_handler(self.deal_handler)
        self.trd_ctx_hk.set_handler(self.order_handler)
        self.trd_ctx_hk.set_handler(self.deal_handler)
        self.trd_ctx_cn.set_handler(self.order_handler)
        self.trd_ctx_cn.set_handler(self.deal_handler)
        self.sys_log.log_out("Connection Built Successfully!")

        self.data_account_status = pd.DataFrame({})
        self.data_account_details = pd.DataFrame({})
        self.option_chain_filter = OptionDataFilter()
        self.data_option_chain = pd.DataFrame({})
        self.data_position_list = pd.DataFrame({})
        self.data_order_list = pd.DataFrame({})
        self.data_deal_list = pd.DataFrame({})
        self.data_historical_order_list = pd.DataFrame({})

        # Pyqt5
        self.app = QApplication(sys.argv)
        self.msg_box = QMessageBox()
        self.olympusWin = OlympusMainWindow(self)
        self.olympusWin.show()
        self.sys_log.log_out("Window Launched Successfully!")
        sys.exit(self.app.exec_())

    def get_acc_list(self, text):
        if text == 'US':
            self.trd_ctx_current = self.trd_ctx_us
        elif text == 'HK':
            self.trd_ctx_current = self.trd_ctx_hk
        else:
            self.trd_ctx_current = self.trd_ctx_cn
        ret, data = self.trd_ctx_current.get_acc_list()
        if ret == RET_OK:
            self.data_account_status = data
            self.accinfo_query(data['acc_id'][0])
        else:
            self.sys_log.log_out('[Error]' + data)
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def accinfo_query(self, text2):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret2, data2 = self.trd_ctx_current.accinfo_query(
            trd_env=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
            acc_id=int(text2))
        if ret2 == RET_OK:
            self.data_account_details = data2

            self.position_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
                                     acc_id=int(text2))
            self.order_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
                                  acc_id=int(text2))
            self.historical_order_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
                                             acc_id=int(text2))
            self.deal_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
                                 acc_id=int(text2))
        else:
            self.sys_log.log_out('[Error]' + data2)
            self.msg_box.warning(self.msg_box, 'Error', data2, QMessageBox.Close, QMessageBox.Close)

    def get_option_chain(self, security_code, expire_date):
        ret, data = self.quote_ctx.get_option_chain(security_code, IndexOptionType.NORMAL, '2020-12-01',
                                                    expire_date, OptionType.ALL, OptionCondType.ALL,
                                                    self.option_chain_filter)
        if ret == RET_OK:
            if len(data) > 0:
                self.data_option_chain = data
            else:
                self.msg_box.warning(self.msg_box, 'Error', 'No Option Found!', QMessageBox.Close, QMessageBox.Close)
                self.data_option_chain = pd.DataFrame({})
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
            self.data_option_chain = pd.DataFrame({})

    def get_market_snapshot(self, security_code):
        ret, data = self.quote_ctx.get_market_snapshot([security_code])
        if ret == RET_OK:
            pass
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
        return ret, data

    def position_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.position_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
        if ret == RET_OK:
            if code == '':
                self.data_position_list = data
            else:
                return data
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def order_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.order_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
        if ret == RET_OK:
            if code == '':
                self.data_order_list = data
                self.sys_ord_mgr.total_update()
            else:
                return data
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def historical_order_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.history_order_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
        if ret == RET_OK:
            if code == '':
                self.data_historical_order_list = data
            else:
                return data
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def deal_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.deal_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
        if ret == RET_OK:
            if code == '':
                self.data_deal_list = data
            else:
                return data
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

    def create_strategy(self, strategy, derivative, underlying, acc_id, acc_type):
        ret, strategy_instance = self.sys_stg_mgr.add_stg(strategy, derivative, underlying, acc_id, acc_type)
        if ret:
            if self.feed_subscribe(underlying) and self.feed_subscribe(derivative):
                # self.sys_stg_mgr.group_callback_orderbook(self.quote_ctx.get_order_book(underlying, 1)[1])
                # self.sys_stg_mgr.group_callback_orderbook(self.quote_ctx.get_order_book(derivative, 1)[1])
                strategy_instance.strategy_window.show()
            else:
                self.msg_box.warning(self.msg_box, 'Warning', "Subscription may not be successful!",
                                     QMessageBox.Close, QMessageBox.Close)
            return True
        else:
            return False

    def feed_subscribe(self, security_code):
        ret_sub, err_message = self.quote_ctx.subscribe([security_code],
                                                        [SubType.ORDER_BOOK, SubType.TICKER],
                                                        is_first_push=True, extended_time=True)
        if ret_sub == RET_OK:
            self.sys_log.log_out(
                'subscribe successfully:' + str(self.quote_ctx.query_subscription()))
            return True
        else:
            self.sys_log.log_out(str(err_message))
            return False

    def delete_strategy(self, derivative, underlying):
        if self.feed_unsubscribe(underlying):   # youwenti!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.feed_unsubscribe(derivative):
                self.sys_log.log_out("Try to delete strategy!")
                if self.sys_stg_mgr.del_stg(derivative, underlying):
                    return True
                else:
                    self.feed_subscribe(derivative)
                    self.feed_subscribe(underlying)
            else:
                self.feed_subscribe(underlying)
        return False

    def feed_unsubscribe(self, security_code):
        ret_unsub, err_message_unsub = self.quote_ctx.unsubscribe([security_code],
                                                                  [SubType.ORDER_BOOK, SubType.TICKER])
        if ret_unsub == RET_OK:
            self.sys_log.log_out(
                'unsubscribe all successfully！current subscription status:' + str(
                    self.quote_ctx.query_subscription()))  # 取消订阅后查询订阅状态
            return True
        else:
            self.sys_log.log_out('Failed to cancel all subscriptions！' + str(err_message_unsub))
            return False

    def callback_orderbook(self, data):
        self.sys_stg_mgr.group_callback_orderbook(data)

    def callback_ticker(self, data):
        self.sys_stg_mgr.group_callback_ticker(data)

    def callback_order(self, data):
        self.sys_ord_mgr.feed_update(data)
        self.sys_stg_mgr.group_callback_order(data)

    def callback_deal(self, data):
        self.sys_pos_mgr.feed_update(data)
        self.sys_stg_mgr.group_callback_deal(data)

    def create_order(self, strategy_instance, price, qty, side):  # better handover to OA
        if strategy_instance.region == 'US':
            self.trd_ctx_current = self.trd_ctx_us
        elif strategy_instance.region == 'HK':
            self.trd_ctx_current = self.trd_ctx_hk
        else:
            self.trd_ctx_current = self.trd_ctx_cn
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.place_order(trd_env=strategy_instance.trading_type,
                                                     acc_id=strategy_instance.trading_account,
                                                     price=price,
                                                     qty=qty,
                                                     code=strategy_instance.derivative_code,
                                                     trd_side=side)
        if ret == RET_OK:
            self.sys_log.log_out("Order: " + str(data['order_id'][0]) + " has been sent! [" +
                                 strategy_instance.derivative_code + "," +
                                 str(strategy_instance.trading_account) + "," +
                                 str(price) + "," +
                                 str(qty) + "]"
                                 )
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)

        return ret, data

    def modify_order(self, order_id, acc_id, modifyorderop, qty=0, price=0):
        self.trd_ctx_current.unlock_trade(self.pwd_unlock)
        ret, data = self.trd_ctx_current.modify_order(modifyorderop,
                                                      order_id, qty, price,
                                                      trd_env=TrdEnv.REAL if int(
                                                          acc_id) > 99999999 else TrdEnv.SIMULATE,
                                                      acc_id=acc_id)
        if ret == RET_OK:
            if modifyorderop == ModifyOrderOp.CANCEL:
                self.sys_log.log_out("Order: " + str(data['order_id'][0]) + " has been canceled!")
            # print(data.to_dict())
        else:
            self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
        return ret, data

    def __del__(self):
        self.quote_ctx.close()
        self.trd_ctx_us.close()
        self.trd_ctx_hk.close()
        self.trd_ctx_cn.close()

        sys.exit(self.app.exec_())
