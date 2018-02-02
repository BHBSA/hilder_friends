import pika
import pymongo
import json
import random
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.235'))
channel = connection.channel()
coll = pymongo.MongoClient('192.168.0.61', 27017)['buildings'].get_collection('yfsd_new')
channel.queue_declare(queue='yfsd_house')

city_dict = {
    'yfsdhrb': '哈尔滨',
    'yfsdsuz': '苏州',
    'bjset': '北京',
    'yfsdwh': '武汉',
    'yfsdsjz': '石家庄',
    'yfsdchd': '成都',
    'yfsdzz': '郑州',
    'yfsdhf': '合肥',
    'yfsdnac': '南昌',
    'yfsdfuz': '福州',
    'yfsdhaz': '杭州',
    'yfsdlaz': '兰州',
    'yfsdhuh': '呼和浩特',
    'yfsdnib': '宁波',
    'yfsdguy': '贵阳',
    'yfsdwez': '温州',
    'yfsdkum': '昆明',
    'yfsdjin': '济南',
}
count = 0


def callback(ch, method, properties, body):
    body = json.loads(body.decode())
    resultData = body.get('resultData')
    city = body.get('city')
    for i in resultData:
        i['city'] = city
    coll.insert_many(resultData)
    print('--'*random.randint(2,50))
    # 告诉生产者，消息处理完成
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consume():
    # 类似权重，按能力分发，如果有一个消息，就不在给你发
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='yfsd_house',)
    channel.start_consuming()


if __name__ == "__main__":
    start_consume()
