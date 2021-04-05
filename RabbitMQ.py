from config.Config_sem import configs
import pika
import json
import logging

class RabbitMQ(object):

    def __init__(self, exchange, queue_name, routing_key):
        """
        初始化参数:
        用户名，密码，ip，端口，交换机，交换机类型，队列名称，路由key
        """
        self._host = configs["rabbitmq_config"]["host"]  # broker IP
        self._port = int(configs["rabbitmq_config"]["port"])  # broker port
        # self._vhost = vhost  # vhost
        self._exchange = exchange  # 交换机名称
        self._exchange_type = configs["rabbitmq_config"]["exchange_type"]  # 交换机方式
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._credentials = pika.PlainCredentials(configs["rabbitmq_config"]["username"],
                                                  configs["rabbitmq_config"]["password"])

    def connect(self):
        # 连接RabbitMQ的参数对象
        parameter = pika.ConnectionParameters(self._host, self._port,
                                              credentials=self._credentials)

        self.connection = pika.BlockingConnection(parameter)  # 建立连接

        self.channel = self.connection.channel()

    def declare_exchange(self):
        """
        声明交换机
        :return: None
        """
        self.channel.exchange_declare(exchange=self._exchange,
                                      exchange_type=self._exchange_type,
                                      durable=True)

    def declare_queue(self):
        """
        声明队列
        :return: None
        """
        self.declare_queue_result = self.channel.queue_declare(queue=self._queue_name,
                                                               durable=True)

    def bind_queue(self):
        """
        将交换机下的队列名与路由key绑定起来
        :return: None
        """
        self.channel.queue_bind(exchange=self._exchange,
                                queue=self._queue_name,
                                routing_key=self._routing_key)

    def publish(self, body):
        """
        发布消息
        :return: None
        """
        self.channel.basic_publish(exchange=self._exchange,
                                   routing_key=self._routing_key,
                                   body=body)

    def consume(self):
        """
        消费信息，先判断队列中是否有消息，如果无，过，如有，则消费掉队列中的所有消息
        :return: None
        """

        message_count = self.declare_queue_result.method.message_count

        if message_count == 0:
            raise ValueError('No messages in Rabbitmq !'.center(50, '*'))
        else:
            for method, properties, body in self.channel.consume(self._queue_name):
                self.channel.basic_ack(method.delivery_tag, multiple=False)
                if method.delivery_tag == message_count:
                    message_get = body.decode()
                    break
        return message_get

    def consume1(self):
        """
        消费消息
        :return: None
        """
        self.channel.basic_consume(self._queue_name, on_message_callback=self.callback, auto_ack=True)

        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        pass

    def connection_close(self):
        self.connection.close()

    def get_data_fromMQ(self):
        '''
        :return: 返回rabbitmq的最新消息，str格式
        '''
        self.connect()
        self.declare_exchange()
        self.declare_queue()
        self.bind_queue()
        mq_mess = self.consume1()
        self.connection_close()
        mq_mess_dict = json.loads(mq_mess)
        print(mq_mess_dict['entityName'].center(80, '+'))
        print('messages from MQ:'.center(50, '='))
        print(mq_mess)

        return mq_mess_dict

    def send_data_to_RabbitMQ(self, mess_send):

        self.connect()  # 建立连接
        self.declare_exchange()  # 声明交换机
        self.declare_queue()  # 声明队列
        self.bind_queue()  # 绑定队列
        self.publish(mess_send)
        self.connection_close()  # 关闭连接
        logging.error('Message Transfer Successful !'.center(50, '='))


# if __name__=='__main__':
#
#     from CommunicationConfig import *
#
#     queue_name = QUEUE_NAME_GET
#     routing_key = ROUTING_KEY_GET
#     mq = RabbitMQ(queue_name, routing_key)
#     mq.connect()
#     mq.declare_exchange()
#     mq.declare_queue()
#     mq.bind_queue()
#     mess = mq.consume()
#     print(mess)
#     # i = 0
#     # while i < 10:
#     #     i = i + 1
#     #     mq.publish('我是第%s条消息'% i)
#     mq.connection_close()
