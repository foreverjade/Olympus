from RuleBase import *


class RuleUSOptionManual(RuleBase):

    stg_name = "RuleUSOptionManual"
    stg_version = "RuleUSOptionManual_20201125"

    def __init__(self, derivative, underlying, p_core, window, acc_id, acc_type):  # member variables
        super().__init__(derivative, underlying, p_core, window, acc_id, acc_type)

    def on_underlying_quote_update(self):
        pass

    def on_underlying_trade_update(self):
        pass

    def on_derivative_quote_update(self):
        pass

    def on_derivative_trade_update(self):
        pass