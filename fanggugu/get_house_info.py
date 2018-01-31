import requests
import pymongo
import time
import json
import pika
from multiprocessing import Process
import random

ips = [
    "192.168.0.90:4234",
    "192.168.0.93:4234",
    "192.168.0.94:4234",
    "192.168.0.96:4234",
    "192.168.0.98:4234",
    "192.168.0.99:4234",
    "192.168.0.100:4234",
    "192.168.0.101:4234",
    "192.168.0.102:4234",
    "192.168.0.103:4234"
]


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, ))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


def login(ip, user_id):
    s = requests.session()
    parms = {'pwd_login_username': user_id,
             'pwd_login_password': '4ac9fa21a775e4239e4c72317cdca870',
             'remembermeVal': 0}
    proxies = {
        'http': ip
    }
    s.get(url='http://www.fungugu.com/DengLu/doLogin_noLogin', params=parms,
          proxies=proxies)
    jrbqiantai = s.cookies.get_dict()['jrbqiantai']
    return jrbqiantai


class get_building_info(object):
    coll_insert = connect_mongodb('192.168.0.235', 27017, 'fgg', 'fanggugu_building')
    channel = connect_rabbit('192.168.0.235', 'fgg_community_id')

    def __init__(self, ip, user_id):
        self.ip = ip
        self.user_id = user_id
        self.proxies = {'http': self.ip}

    def start_building_info(self, ch, method, properties, body):
        cookie_ = method.consumer_tag
        headers = {
            'Cookie': 'jrbqiantai=' + cookie_,
            'Referer': 'http://www.fungugu.com/JinRongGuZhi/toJinRongGuZhi_s?xqmc=DongHuVillas&gjdx=DongHuVillas&residentialName=&realName=&dz=&xzq=%E9%95%BF%E5%AE%81%E5%8C%BA&xqid=22013&ldid=&dyid=&hid=&loudong=&danyuan=&hu=&retrievalMethod=%E6%99%AE%E9%80%9A%E6%A3%80%E7%B4%A2',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        }
        message = json.loads(body.decode())
        ResidentialAreaID = message['ResidentialAreaID']
        city_name = message['city_name']
        building_id = message['building_id']
        print(building_id, city_name)
        url = 'http://www.fungugu.com/JinRongGuZhi/getLiandong'
        params = {
            'city': city_name,
            'id': building_id,
            'type': 'danyuan'
        }
        try:
            time.sleep(5)
            response = requests.post(url=url, headers=headers, params=params,
                                     proxies=self.proxies)
            if 'true' or 'True' in response.text:
                house_list = json.loads(response.text)['list']
                if not house_list:
                    print('没有house信息 - - None')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                for i in house_list:
                    print(i)
                    building_id = i['id']
                    building_name = i['name']
                    building_type = i['type']
                    data = {
                        'building_id': building_id,
                        'building_name': building_name,
                        'building_type': building_type,
                    }
                    self.channel.basic_publish(exchange='',
                                               routing_key='fgg_building_id',
                                               body=json.dumps(data),
                                               )
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print('页面错误')
            self.channel.basic_publish(exchange='',
                                       routing_key='fgg_building_id',
                                       body=body,
                                       )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_queue(self, cookie):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(consumer_callback=self.start_building_info, queue='fgg_building_id',
                                   consumer_tag=cookie)
        self.channel.start_consuming()


if __name__ == '__main__':
    coll = connect_mongodb('192.168.0.235', 27017, 'fgg', 'user_info').find({})
    for i in coll:
        user_id = i['user_name']
        ip = random.choice(ips)
        cookie = login(ip, user_id)
        com = get_building_info(ip=ip, user_id=user_id)
        Process(target=com.consume_queue, args=(cookie,)).start()
