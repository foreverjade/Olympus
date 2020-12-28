from datetime import datetime
from PyQt5.QtWidgets import QWidget
import pytz
import numpy as np
from scipy.stats import norm
import time


def sys_time_now_hms():
    return datetime.now().strftime("%H:%M:%S")


def auto_strptime(text):
    if str.find(text, '.', 18) > 0:
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f')
    else:
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')


def cal_implied_volatility(time_to_expire, underlying_price, strike_price, market_price, option_type,
                           risk_free=0.01, dividend_yield=0):
    # 设定参数
    r = risk_free  # risk-free interest rate
    t = float(time_to_expire) / 365  # time to expire (30 days)
    q = dividend_yield  # dividend yield
    S0 = underlying_price  # underlying price
    X = strike_price  # strike price
    mktprice = market_price  # market price

    # 用二分法求implied volatility，暂只针对call option
    sigma = 0.3  # initial volatility
    C = P = 0
    upper = 1
    lower = 0
    if option_type == "CALL":
        if S0 - X >= mktprice:
            return 0
        while abs(C - mktprice) > 1e-6:
            d1 = (np.log(S0 / X) + (r - q + sigma ** 2 / 2) * t) / (sigma * np.sqrt(t))
            d2 = d1 - sigma * np.sqrt(t)
            C = S0 * np.exp(-q * t) * norm.cdf(d1) - X * np.exp(-r * t) * norm.cdf(d2)
            if C - mktprice > 0:
                upper = sigma
                sigma = (sigma + lower) / 2
            else:
                lower = sigma
                sigma = (sigma + upper) / 2
    else:
        if X - S0 >= mktprice:
            return 0
        while abs(P - mktprice) > 1e-6:
            d1 = (np.log(S0 / X) + (r - q + sigma ** 2 / 2) * t) / (sigma * np.sqrt(t))
            d2 = d1 - sigma * np.sqrt(t)
            P = X * np.exp(-r * t) * norm.cdf(-d2) - S0 * np.exp(-q * t) * norm.cdf(-d1)
            if P - mktprice > 0:
                upper = sigma
                sigma = (sigma + lower) / 2
            else:
                lower = sigma
                sigma = (sigma + upper) / 2

    return sigma * 100  # implied volatility
