
import pandas as pd
# -------配置参数-----------
WaterTempBase_summer = 7  # 夏季供水温度最大能力基准水温
WaterTempBase_winter = 45  # 冬季供水温度最大能力基准水温
DeltaT = 4  # 温差，例如夏季某个点位的送风温度比全局最小送风高4℃，该点位又超标了，那么末端是有问题的。

def cal_comp(x, tup):

    sum_capacity_fzl = 0  # 冷站出力，用冷机容量加权负载率
    sum_capacity = 0
    sum_tp_fzl = 0
    signal = 0

    for i in tup:

        sum_capacity += float(x[(i, 'capacity')])

        if x[(i, 'fzl')] is None and x[(i, 'power_ratio')] is None:

            sum_capacity_fzl += 0
            sum_tp_fzl += 0
            signal = 1

        elif x[(i, 'fzl')] is None:

            sum_capacity_fzl += x[(i, 'power_ratio')] * float(x[(i, 'capacity')])
            sum_tp_fzl += x[(i, 'eff_tp_eva')] * x[(i, 'power_ratio')] * float(x[(i, 'capacity')])

        else:

            sum_capacity_fzl += x[(i, 'fzl')] * float(x[(i, 'capacity')])
            sum_tp_fzl += x[(i, 'eff_tp_eva')] * x[(i, 'fzl')] * float(x[(i, 'capacity')])

    ratio_1 = round(sum_capacity_fzl / sum_capacity, 2)  # 相当于实际制冷量占冷站总额定容量比值

    if sum_capacity_fzl == 0:  # 冷机关机的情况
        ratio_2 = None
    else:
        ratio_2 = round(sum_tp_fzl / sum_capacity_fzl, 2)   # 实际制冷量的加权出水水温

    if signal == 0:
        return pd.Series([ratio_1, ratio_2], index=['ratio_1', 'ratio_2'])
    else:
        return pd.Series([None, None], index=['ratio_1', 'ratio_2'])

