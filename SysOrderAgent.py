

class OrderAgent:
    def __init__(self, p_core, p_stg):
        self.link_core = p_core
        self.strategy_instance = p_stg

    def create(self, strategy_instance, price, qty, side):  # better handover to OA
        ret, data = self.link_core.create_order(strategy_instance, price, qty, side)
        print (data)

    def cancel(self, order_id):
        # print(trd_ctx.unlock_trade(pwd_unlock))
        # print(trd_ctx.cancel_all_order())
        pass

    def cancel_all(self, order_id):
        # print(trd_ctx.unlock_trade(pwd_unlock))
        # print(trd_ctx.cancel_all_order())
        pass

    def modify(self, order_id, price, qty, side):
        # print(trd_ctx.unlock_trade(pwd_unlock)) order_id = "8851102695472794941" print(trd_ctx.modify_order(
        # ModifyOrderOp.CANCEL, order_id, 0, 0)) modify_order(modify_order_op, order_id, qty, price, adjust_limit=0,
        # trd_env=TrdEnv.REAL, acc_id=0, acc_index=0) ModifyOrderOp NONE        未知操作 NORMAL        修改订单的价格、数量 CANCEL
        # 撤单 DISABLE        失效 ENABLE        生效 DELETE        删除
        pass
