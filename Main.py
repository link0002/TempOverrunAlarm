from config.Config_sem import configs
from RabbitMQ import RabbitMQ
from Process import Process
import json
from logconfig import *


class mq(RabbitMQ):

    def __init__(self, exchange, queue_name, routing_key):
        super(mq, self).__init__(exchange, queue_name, routing_key)

    def callback(self, ch, method, properties, body):
        data_from_rabbitmq = body.decode()
        Main_callback(data_from_rabbitmq)


def Main():

    # ------------实例化RabbitMQ连接并获取数据------------
    exchane = configs["rabbitmq_config"]["exchange_get"]
    queue_name = configs["rabbitmq_config"]["queue_name_get"]  # 获取数据的队列的名称
    routing_key = configs["rabbitmq_config"]["routing_key_get"]  # 获取数据的队列的路由建名称
    mq_get = mq(exchane, queue_name, routing_key)
    mq_get.connect()
    mq_get.declare_exchange()
    mq_get.declare_queue()
    mq_get.bind_queue()
    mq_get.consume1()
    mq_get.connection_close()


def Main_callback(mq_mess):
    '''
    被回调函数调用
    :param mq_mess:
    :return:
    '''
    # 1-mq消息获取和显示
    mq_mess_dict = json.loads(mq_mess)
    logging.error(mq_mess_dict['entityName'].center(80, '*'))
    logging.error('messages from MQ:'.center(50, '='))
    logging.error(mq_mess)

    # 2-数据预处理和逻辑分析
    p = Process(mq_mess_dict)
    mess_send = p.classifyer()

    # 3-发送到MQ队列
    exchange_send = configs["rabbitmq_config"]["exchange_send"]
    queue_name_send = configs["rabbitmq_config"]["queue_name_send"]  # 发送数据的队列的名称
    routing_key_send = configs["rabbitmq_config"]["routing_key_send"]  # 发送数据的队列的路由建名称
    mq_send = RabbitMQ(exchange_send, queue_name_send, routing_key_send)
    mq_send.send_data_to_RabbitMQ(mess_send)


if __name__ == '__main__':

    Main()
