from lib.rabbitmq import Rabbit
import re


class AnalyLog:
    """
        解析log日志。放入队列
    :param path(str): 文件路径，相对路径，带文件名以及后缀，e: '小资家_build_fast.log' ( ◆ must ◆ )
    :param queue(str): 放入的队列
    :param args(str): 字段参数，以 args="(.*?)" 的规则解析字段，可以多填  ( ◆ must ◆ )
    :param r_host(str): 放入rabbit的地址
    :param r_port(int): 放入rabbit的端口号

    """

    def __init__(self, path, queue, *args, r_host='192.168.0.190', r_port=5673):
        self.path = path
        self.args = args
        self.r_host = r_host
        self.r_port = r_port
        self.queue = queue
        self.data = {}

    def connect_rabbit(self):
        r = Rabbit(self.r_host, self.r_port)
        connection = r.connection
        channel = connection.channel()
        channel.queue_declare(queue=self.queue)
        return channel

    def analy_start(self):
        # channel = self.connect_rabbit()
        with open(self.path, 'r',encoding='gbk') as f:
            paper = f.read()
            line_list = re.findall('^(.*?)$', paper, re.S | re.M)
            for line in line_list:
                print(self.args)
                for args in self.args:
                    value_ = re.search('%s="(.*?)"' % args, line, re.S | re.M).group(1)
                    self.data[args] = value_
                print(self.data)


if __name__ == '__main__':
    a = AnalyLog('小资家_build_fast.log', 'log_test', 'ConstructionPhaseId', 'ConstructionName', 'ConstructionId')
    a.analy_start()
