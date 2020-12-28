from SysFunction import *
from PyQt5.QtGui import QColor


class SysLog:
    def __init__(self, p_core):
        self.link_core = p_core
        self.date_str = datetime.now().strftime("%Y%m%d")
        self.record_log = True
        self.log_file = self.link_core.sys_file.file_sys_log_output

    def log_out(self, text):
        time_str = datetime.now().strftime('%H:%M:%S.%f')
        print(time_str + " " + text)
        if self.record_log:
            self.log_file.write(time_str + " " + text + "\n")


class StgLog:
    def __init__(self, p_stg):
        self.strategy_instance = p_stg
        self.date_str = datetime.now().strftime("%Y%m%d")
        # self.record_log = True
        # self.log_file = open("C:/Users/shrfa/PycharmProjects/pythonProject/Logs/" + self.date_str +"STG_LOG.log", 'a+')

    def log_out(self, text, index=0):  # index[0:OnlyRecord, 1:ShowInTheFrontEnd, 2:FrontEndAlert]
        if self.strategy_instance.region == 'US':
            time_str = datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%H:%M:%S.%f')
            time_str_short = datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%H:%M:%S')
        else:
            time_str = datetime.now().strftime('%H:%M:%S.%f')
            time_str_short = datetime.now().strftime('%H:%M:%S')
        print(time_str + " " + text)
        # if self.record_log:
        #     self.log_file.write(time_str + " " + text + "\n")
        if index & 1:
            self.strategy_instance.strategy_window.listWidget_Log.insertItem(0, time_str_short + ' ' + text)
        if index & 2:
            self.strategy_instance.strategy_window.listWidget_Log.item(0).setBackground(QColor('red'))


class WinLog:
    def __init__(self, p_win):
        self.strategy_window = p_win
        self.date_str = datetime.now().strftime("%Y%m%d")
        # self.record_log = True
        # self.log_file = open("C:/Users/shrfa/PycharmProjects/pythonProject/Logs/" + self.date_str +"WIN_LOG.log", 'a+')

    def log_out(self, text, index=1):  # index[0:OnlyRecord, 1:ShowInTheFrontEnd]
        if self.strategy_window.derivative_code[0:2] == 'US':
            time_str = datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%H:%M:%S.%f')
            time_str_short = datetime.now(tz=pytz.timezone('US/Eastern')).strftime('%H:%M:%S')
        else:
            time_str = datetime.now().strftime('%H:%M:%S.%f')
            time_str_short = datetime.now().strftime('%H:%M:%S')
        print(time_str + " " + text)
        # if self.record_log:
        #     self.log_file.write(time_str + " " + text + "\n")
        if index & 1:
            self.strategy_window.listWidget_Log.insertItem(0, time_str_short + ' ' + text)
        if index & 2:
            self.strategy_window.listWidget_Log.item(0).setBackground(QColor('red'))
