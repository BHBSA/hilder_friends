"""
    消费xiaozijia_house队列，请求，入楼栋库xiaozijia_house_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import requests
import json
from xiaozijia.user_headers import get_headers
import yaml

log = LogHandler('小资家_house_fast')

setting = yaml.load(open('config.yaml'))

# mongo
m = Mongo(setting['xiaozijia']['mongo']['host'], setting['xiaozijia']['mongo']['port'])
coll_house = m.connect[setting['xiaozijia']['mongo']['db']][setting['xiaozijia']['mongo']['house_coll']]

# rabbit
r = Rabbit(setting['xiaozijia']['rabbit']['host'], setting['xiaozijia']['rabbit']['port'])
channel = r.get_channel()
house_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_house']
detail_queue = setting['xiaozijia']['rabbit']['queue']['xiaozijia_house_detail']
channel.queue_declare(queue=house_queue)
channel.queue_declare(queue=detail_queue)

headers = get_headers()


def get_house_info(ch, method, properties, body):
    """
    消费xiaozijia_build队列，请求，入小区库，并放入房号页
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    body_json = json.loads(body.decode())
    IdSub = body_json['IdSub']
    ConstructionName = body_json['ConstructionName']
    BuildName = body_json['Name']
    ConstructionId = body_json['ConstructionId']
    house_url = 'http://www.xiaozijia.cn/HousesForJson/' + IdSub + '/1'
    try:
        response = requests.get(house_url, headers=headers, timeout=20)
        html_json = response.json()
        for i in html_json:
            i['ConstructionName'] = ConstructionName
            i['ConstructionId'] = ConstructionId
            i['BuildName'] = BuildName
            i['IdSub'] = IdSub
            channel.basic_publish(exchange='',
                                  routing_key=detail_queue,
                                  body=json.dumps(i))
            coll_house.insert_one(i)
            log.info(i)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        global headers
        headers = get_headers()
        log.error('请求错误，url="{}",BuildName="{}",ConstructionName="{}",ConstructionId="{}",IdSub="{}",e="{}"'
                  .format(house_url, BuildName, ConstructionName, ConstructionId, IdSub, e))
        channel.basic_publish(exchange='',
                              routing_key=house_queue,
                              body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=get_house_info, queue=house_queue)
    channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
