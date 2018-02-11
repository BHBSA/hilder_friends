from multiprocessing import Process, Pool
import urllib3
import json
import pika
import certifi
import time
import random
import os
import psutil

pool_list = []


class HouseId(object):
    # 建立实例，声明管道，声明队列
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.235', ))
    channel = connection.channel()
    channel.queue_declare(queue='yfsd_building')
    # 设置代理IP
    proxy = urllib3.ProxyManager('http://192.168.0.94:4234/', cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    }

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        # 获取队列中的数据
        if 'city' in body:
            city_url = body['city_url']
            buildingId = body['buildingId']
            print(city_url)
            print(buildingId)
            city = body['city']
            # 发起第三次请求，得到房间的Id
            try:
                response = self.proxy.request(
                    'POST',
                    city_url + '/wxp/yfsd/loadHouseData',
                    fields={'buildingId': str(buildingId)},
                    headers=self.headers,
                )

                result = json.loads(response.data.decode('utf-8'))

                if 'resultData' in result:
                    data = {
                        'resultData': result['resultData'],
                        'city': city,
                    }
                    self.channel.queue_declare(queue='yfsd_house')
                    self.channel.basic_publish(exchange='',
                                               routing_key='yfsd_house',
                                               body=json.dumps(data)
                                               )
                    print("==" * random.randint(1, 20))
                else:
                    print("NO RESULT:", result)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(e,buildingId)



    def consume_start(self):
        pool_list.append(os.getpid())
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                                   queue='yfsd_building')
        self.channel.start_consuming()


if __name__ == '__main__':
    worker = HouseId()
    for i in range(10):
        Process(target=worker.consume_start).start()
