import pandas as pd
import json
from logconfig import *
from self_func import cal_comp, WaterTempBase_summer, WaterTempBase_winter, DeltaT
pd.set_option('display.max_columns', None)


class Process():

    def __init__(self, mq_mess):

        self.mq_mess_dict = mq_mess
        self.entityName = self.mq_mess_dict['entityName']
        self.asid = self.mq_mess_dict['asId']
        self.coolHeatMode = self.mq_mess_dict['coolHeatMode']
        self.baseWaterTemp = self.mq_mess_dict['baseWaterTemp']
        # ----------关键变量信息-------------
        logging.error('key values'.center(50, '='))
        self.dfConfig = pd.DataFrame(self.mq_mess_dict["dfConfig"])
        # self.dfConfig['locations'] = self.dfConfig['locations'].map(lambda x: json.loads(x)[2])

        # 温湿度的配置信息
        print('dfConfig:\n%s' % self.dfConfig)

        # 超标点最近3个时刻的温湿度df
        self.dfTp = self.dfTp_preprocess()
        print('dfTp:\n%s' % self.dfTp)

        # 其他点位的送风温度df
        self.df_supplyTemp = pd.DataFrame(self.mq_mess_dict['supplyTemp'])
        print('supplyTemp:\n%s' % self.df_supplyTemp)

        # 冷站最近3个时刻综合负载率和综合出水温度的df
        self.df_ratio = self.dfWtp_preprocess()
        print('df_ratio:\n%s' % self.df_ratio)

    def dfTp_preprocess(self):
        '''
        对原始数据进行预处理，整理超标温度最近3个时刻数据的df格式
        :return:
        '''
        dict_dfTp = self.mq_mess_dict["dfTp"].copy()
        list_dfTp = []

        for i in dict_dfTp.keys():

            df = pd.DataFrame(dict_dfTp[i])
            df.sort_values(by='time', ascending=False, inplace=True)
            list_dfTp.append(df)

        df_concat = pd.concat(list_dfTp, keys=[int(i) for i in dict_dfTp.keys()], axis=1)

        return df_concat

    def dfWtp_preprocess(self):
        '''
        对原始数据预处理，形成冷站最近3个时刻各冷机数据df，再进一步处理成冷站的负载率以及综合出水温度的df
        数据预处理，得到该冷站各个冷机的meterid的集合set_meter_id;
        得到处理后的冷站加权负载和综合水温df_ratio
        :return:
        '''
        dict_dfWtp = self.mq_mess_dict["dfWtp"].copy()
        list_dfWtp = []

        for i in dict_dfWtp.keys():
            list_dfWtp.append(pd.DataFrame(dict_dfWtp[i]))

        self.dfWtp = pd.concat(list_dfWtp, keys=[int(i) for i in dict_dfWtp.keys()], axis=1)

        set_meter_id = set([int(i) for i in dict_dfWtp.keys()])
        df_ratio = self.dfWtp.apply(cal_comp, axis=1, args=(set_meter_id,))

        return df_ratio

    # ------------进行逻辑分析------------
    def classifyer_summer(self):
        '''
        超标温度点问题分类——分锅函数
        :return:
        '''
        # 当前冷站出水温度
        wtp = self.df_ratio['ratio_2'].mean()
        wtp = round(wtp, 2)
        # 最小送风温度
        min_su_tp = self.df_supplyTemp['tp'].min()

        # # #如果部分空调机组全新风或近似全新风，送风温度可能比水温还低，全局最小送风温度将不能反映冷冻水处理空气的最佳效果
        if min_su_tp < wtp + 1:
            min_su_tp = wtp + 1
        # # #如果只开一个空调末端，其送风温度将成为最小的温度，无法真实反映末端正常的可达到的最低送风温度。
        min_su_tp = min(min_su_tp, wtp + 5)

        # 采集时间
        list_time = []
        # 超标类型
        list_type = []
        # 送风温度
        list_su_tp_mean = []
        # 全局最小送风温度
        list_min_su_tp = []
        # 回风温度
        list_re_tp = []
        # 当前水温
        list_wtp = []
        # 文本
        list_text = []

        for id in self.dfConfig.su_meterId:

            # 当前送风温度(最近3个点的平均送风温度)
            su_tp_mean = self.dfTp[(id, 'tp')].mean()
            su_tp_mean = round(su_tp_mean, 2)
            # 当前回风温度(最近时刻的回温度)
            reid = self.dfConfig[self.dfConfig['su_meterId'] == id]['re_meterId'].iloc[0]
            re_tp = self.dfTp[(reid, 'tp')].iloc[0]
            # 当前时间
            time = self.dfTp[(id, 'time')].max()
            # 第1类超标问题
            if (su_tp_mean - wtp > min_su_tp - wtp + DeltaT) and (re_tp - su_tp_mean <= 7):
                type = 1
                reason = '当前送风温度远大于出水温度；该点位流量不足，送风温度设定偏高或当前时刻末端可能发生故障。'
            # 第2类超标问题
            elif wtp < WaterTempBase_summer + 1.0:
                type = 2
                reason = '出水温度已经在7±1℃范围，监测点依然超标；当前时刻冷负荷较大，末端能力不足。'
            # 第4类问题
            elif str(wtp) == 'nan':
                type = 4
                reason = '可能没开机或其他原因(离线)。'
            # 第3类超标问题
            else:
                type = 3
                reason = '冷站出水温度较高；当前设定温度较高。'

            list_time.append(time)
            list_type.append(type)
            list_su_tp_mean.append(su_tp_mean)
            list_min_su_tp.append(min_su_tp)
            list_re_tp.append(re_tp)
            list_wtp.append(wtp)
            list_text.append(reason)

        df = pd.DataFrame({'locations': self.dfConfig['locations'], 'meterId': self.dfConfig['re_meterId'],
                           'time': list_time, 'type': list_type, 'su_tp_mean': list_su_tp_mean,
                           'global_min_su_tp': list_min_su_tp, 're_tp': list_re_tp, 'wtp': list_wtp, 'reason': list_text})

        logging.error('超标诊断结果'.center(50, '='))
        logging.error('\n%s' % df)

        # 返回数据-整合
        dict_send = self.mq_mess_dict.copy()
        del dict_send['dfConfig']
        del dict_send['dfTp']
        del dict_send['dfWtp']
        del dict_send['supplyTemp']

        dict_send["results"] = df.to_dict(orient='list')

        dict_send = json.dumps(dict_send, ensure_ascii=False)
        logging.error('Data sent to mq'.center(50, '='))
        logging.error(dict_send)

        return dict_send

    def classifyer_winter(self):
        '''
        超标温度点问题分类——分锅函数
        :return:
        '''
        # 当前冷站出水温度
        wtp = self.df_ratio['ratio_2'].mean()
        wtp = round(wtp, 2)
        # 最大送风温度
        max_su_tp = self.df_supplyTemp['tp'].max()
        # # # 类似地
        max_su_tp = max(max_su_tp, wtp - 5)

        # 采集时间
        list_time = []
        # 超标类型
        list_type = []
        # 送风温度
        list_su_tp_mean = []
        # 回风温度
        list_re_tp = []
        # 当前水温
        list_wtp = []
        # 文本
        list_text = []

        for id in self.dfConfig.su_meterId:

            # 当前送风温度(最近3个点的平均送风温度)
            su_tp_mean = self.dfTp[(id, 'tp')].mean()
            # 当前回风温度(最近时刻的回温度)
            reid = self.dfConfig[self.dfConfig['su_meterId'] == id]['re_meterId'].iloc[0]
            re_tp = self.dfTp[(reid, 'tp')].iloc[0]
            # 当前时间
            time = self.dfTp[(id, 'time')].max()
            # 第1类超标问题
            if su_tp_mean < max_su_tp - DeltaT:
                type = 1
                reason = '当前送风温度远小于出水温度；该点位流量不足，送风温度设定偏低或当前时刻末端可能发生故障。'
            elif wtp > WaterTempBase_winter - 1:
                type = 2
                reason = '出水温度已经达到冬季标准水温，监测点依然超标；当前时刻冷负荷较大，末端能力不足。'
            else:
                type = 3
                reason = '冷站出水温度较低。'

            list_time.append(time)
            list_type.append(type)
            list_su_tp_mean.append(su_tp_mean)
            list_re_tp.append(re_tp)
            list_wtp.append(wtp)
            list_text.append(reason)

        df = pd.DataFrame({'locations': self.dfConfig['locations'], 'meterId': self.dfConfig['re_meterId'],
                           'time': list_time, 'type': list_type, 'su_tp_mean': list_su_tp_mean, 're_tp': list_re_tp,
                           'wtp': list_wtp, 'reason': list_text})

        logging.error('超标诊断结果'.center(50, '='))
        logging.error('\n%s' % df)

        # 返回数据-整合
        dict_send = self.mq_mess_dict.copy()
        del dict_send['dfConfig']
        del dict_send['dfTp']
        del dict_send['dfWtp']
        del dict_send['supplyTemp']

        dict_send["results"] = df.to_dict(orient='list')

        dict_send = json.dumps(dict_send, ensure_ascii=False)
        logging.error('Data sent to mq'.center(50, '='))
        logging.error(dict_send)

        return dict_send

    def classifyer(self):
        '''
        根据夏季冬季的模式不同，区分
        :return:
        '''
        if self.coolHeatMode == 0:
            dict_send = self.classifyer_summer()
        elif self.coolHeatMode == 1:
            dict_send = self.classifyer_winter()
        else:
            raise ValueError('!!!制冷制热模式输出错误!!!')

        return dict_send
