"""
    消费xiaozijia_num队列，请求，入小区库
    大约需要1个小时
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import requests

log = LogHandler('小资家_fast')

# mongo
m = Mongo('192.168.0.235', 27017)
coll_comm = m.connect['friends']['xiaozijia_comm_fast']

# rabbit
r = Rabbit('192.168.0.190', 5673)
channel = r.get_channel()
channel.queue_declare(queue='xiaozijia_num')


def get_comm_info(ch, method, properties, body):
    """
    消费xiaozijia_num队列，请求，入小区库，并放入楼栋页
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    comm_url = 'http://www.xiaozijia.cn/ConstructionInfo/' + str(body.decode())
    try:
        response = requests.get(comm_url)
        html_json = response.json()
        coll_comm.insert_one(html_json)
        print(html_json)
    except Exception as e:
        log.error('请求错误，url="{}"'.format(comm_url, e))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=get_comm_info, queue='xiaozijia_num')
    channel.start_consuming()


if __name__ == '__main__':
    from multiprocessing import Process
    for i in range(10):
        Process(target=consume_queue).start()
    # consume_queue()
