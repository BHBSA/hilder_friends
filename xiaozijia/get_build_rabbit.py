"""
    消费xiaozijia_build队列，请求，入楼栋库xiaozijia_build_fast
    大约需要10个小时
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import requests
import json

log = LogHandler('小资家_build_fast')

# mongo
m = Mongo('192.168.0.235', 27017)
coll_build = m.connect['friends']['xiaozijia_build_fast']

# rabbit
r = Rabbit('192.168.0.190', 5673)
connection = r.get_connection()
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_build')
channel.queue_declare(queue='xiaozijia_house')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    'Cookie': "18584=webim-visitor-F9R2GW6JMJGC7WV9KTPH; UM_distinctid=163aa58efc71ca-00bff4dd25a5f5-39614101-1aeaa0-163aa58efc8bde; ASP.NET_SessionId=lk4js1iwugdvp4m4jtahxqrq; __RequestVerificationToken=qoZfPtozkkBzTTM1_j6mFw6Pr3sCf7Jhg9vae96v8p2n7GSlue5uJlW-00aZl0zzI_Jchdi6mMg6yuXcwcEKJKENMutQ5Hv9OwhG8FoA00Q1; CNZZDATA1261485443=1637837715-1527570977-%7C1527743000; city_Info=%7B%22CityCode%22%3A%22310100%22%2C%22CityId%22%3A3101%2C%22CityName%22%3A%22%u4E0A%u6D77%u5E02%22%2C%22CityPY%22%3A%22SH%22%2C%22IsEvaluation%22%3Atrue%2C%22IsModel%22%3Afalse%2C%22IsTax%22%3Afalse%2C%22ServiceName%22%3A%22%22%2C%22ServiceTel%22%3A%22%22%2C%22OCityId%22%3A0%2C%22Hot%22%3A1%2C%22Sort%22%3A998%7D; Hm_lvt_a9c54182b3ffd707e45190a9a35a305f=1527571343,1527737477,1527743944; .AspNet.ApplicationCookie=HYtxuZjLt1b8Etlq5ax4XwY465FA1wQuxAS8ari-5Dnfj5M31WdxRht1WddkH2fEQe0keM1e6N4BT_WuhlDsIKqOlk-J1BaPjj8qgshrRu74U2FeDyxq8PaSEfDaWIojTdddl1bJsJTRLfv4x8mA9jZjfu7YqBZGOWoNkk1gmAhKWAcZ7a67QkZ6NZcLNW-5A2LNjGksux32y3eFY5tMj9tIeufb-E0dLwTuC7Dxf8RRwK7hxGWWdYrVRzhAYPUWlCR690H4AZPE6JFCbYUyuM9ejTucJj4Lr5mUmvWTz89JMKH075oSuNibo8fN6cL32YnORemxdwHS2iy6GphdQKJOHE8eJ3XbTnxzv9tkCuqveqG6X7GQueCV0W9SzDGXWKBgEtmZQwW8434bZLiPd2a5JZQchyCCnxaYEcOGsIw; u_Info=%7B%22UserId%22%3A%22db3fa4b8-0048-418f-b893-40c7b3509246%22%2C%22ImgUrl%22%3A%22%22%2C%22NikeName%22%3A%2218621579838%22%2C%22BeanBalance%22%3A0%2C%22GiftBeanBalance%22%3A0%7D; Hm_lpvt_a9c54182b3ffd707e45190a9a35a305f=1527747012",
}


def get_build_info(ch, method, properties, body):
    """
    消费xiaozijia_build队列，请求，入小区库，并放入房号页
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    body_json = json.loads(body.decode())
    ConstructionPhaseId = body_json['ConstructionPhaseId']
    ConstructionName = body_json['ConstructionName']
    ConstructionId = body_json['ConstructionId']
    build_url = 'http://www.xiaozijia.cn/HousesForJson/' + ConstructionPhaseId + '/2'
    try:
        # proxies = {'http': '118.114.77.47:8080', 'https': '118.114.77.47:8080'}
        proxies = {}
        response = requests.get(build_url, headers=headers, proxies=proxies, timeout=30)
        connection.process_data_events()
        html_json = response.json()
        if not html_json:
            print('小区没有楼栋，url={}'.format(build_url))
        for i in html_json:
            i['ConstructionName'] = ConstructionName
            i['ConstructionId'] = ConstructionId
            channel.basic_publish(exchange='',
                                  routing_key='xiaozijia_house',
                                  body=json.dumps(i))
            coll_build.insert_one(i)
            print(i)

    except Exception as e:
        log.error('请求错误，url="{}",ConstructionPhaseId="{}",ConstructionName="{}",ConstructionId="{}",e="{}"'
                  .format(build_url, ConstructionPhaseId, ConstructionName, ConstructionId, e))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=get_build_info, queue='xiaozijia_build')
    channel.start_consuming()


if __name__ == '__main__':
    # from multiprocessing import Process
    #
    # for i in range(10):
    #     Process(target=consume_queue).start()
    consume_queue()
