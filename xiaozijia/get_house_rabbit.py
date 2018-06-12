"""
    消费xiaozijia_house队列，请求，入楼栋库xiaozijia_house_fast
"""

from lib.log import LogHandler
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import requests
import json
from retry import retry

log = LogHandler('小资家_house_fast')

# mongo
m = Mongo('114.80.150.196', 27017)
coll_house = m.connect['friends']['xiaozijia_house_fast_new']

# rabbit
r = Rabbit('114.80.150.196', 5673)
connection = r.get_connection()
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_house')
channel.queue_declare(queue='xiaozijia_house_detail')

headers = {
    'Cookie': "UM_distinctid=163d7da6abc2bf-0b0d00ec058822-39614101-1aeaa0-163d7da6abe5ab; 18584=webim-visitor-86EX8RX699BV2RGPQT69; Hm_lvt_a9c54182b3ffd707e45190a9a35a305f=1528334805,1528766435,1528769152; CNZZDATA1261485443=1749712422-1528333743-null%7C1528768191; ASP.NET_SessionId=zfoefbsltsqoocvtdvy3ws3d; .AspNet.ApplicationCookie=L1rSB-CvGENsv5s6m1-RJuV3xeh1foFCr6dic2hQhFwXytGjYtcWqYiwzpBIZar4liUtYphGLgOEIuJOD6sdXnn6Wi-Ks_pljruLf7yki-kI5tg_4gZG6-5CfRgYCuCuSdDrhkGALNDD4FU18f6L9kcnLBzD-90XvFFLj38V7fqWOtMX61gvy_Ykw1gPcAej6zw241ipts_8ls8S2GO0MmaAjMRcPcdkmXHwyexmAAkjEpqWJPOGyhCYXeFBeL1LwsOcVJOfw36t1RclNN3smOEcSQd_61XzYs1mOJRcswScqBkPO-a84gUzH6Z0aDt5ZAxPczyzBajQkb6IiTw28-teb5s180jevhy_WVLy3ZBxBMqnRbk9atNJelRfPB8R-4Apd15oxeBWBlQZp6oPi0AUSFWdnX_zoXz7MyNZ-mg; u_Info=%7B%22UserId%22%3A%22a9c61144-848e-48d6-be16-f65d555f0cac%22%2C%22ImgUrl%22%3A%22%22%2C%22NikeName%22%3A%2215893020331%22%2C%22BeanBalance%22%3A0%2C%22GiftBeanBalance%22%3A0%7D; city_Info=%7B%22CityId%22%3A4403%2C%22CityName%22%3A%22%u6DF1%u5733%u5E02%22%2C%22CityCode%22%3A%22440300%22%7D; Hm_lpvt_a9c54182b3ffd707e45190a9a35a305f=1528770303",
}

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
    "192.168.0.103:4234",
    '118.114.77.47:8080'
]


@retry(tries=3)
def get_house_info(ch, method, properties, body):
    """
    消费xiaozijia_build队列，请求，入小区库，并放入房号页
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    ip = method.consumer_tag
    body_json = json.loads(body.decode())
    IdSub = body_json['IdSub']
    ConstructionName = body_json['ConstructionName']
    BuildName = body_json['Name']
    ConstructionId = body_json['ConstructionId']
    house_url = 'http://www.xiaozijia.cn/HousesForJson/' + IdSub + '/1'
    try:
        # proxies = {'http': ip, 'https': ip}
        # proxies = {'http': '118.114.77.47:8080', 'https': '118.114.77.47:8080'}
        proxies = {}
        try:
            response = requests.get(house_url, headers=headers, proxies=proxies, timeout=30)
        except Exception as e:
            raise
        connection.process_data_events()
        html_json = response.json()
        for i in html_json:
            i['ConstructionName'] = ConstructionName
            i['ConstructionId'] = ConstructionId
            i['BuildName'] = BuildName
            i['IdSub'] = IdSub
            channel.basic_publish(exchange='',
                                  routing_key='xiaozijia_house_detail',
                                  body=json.dumps(i))
            coll_house.insert_one(i)
            print(ip)
            print(i)

    except Exception as e:
        print(ip)
        # log.error('请求错误，url="{}",BuildName="{}",ConstructionName="{}",ConstructionId="{}",IdSub="{}",e="{}"'
        #           .format(house_url, BuildName, ConstructionName, ConstructionId, IdSub, e))
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_house',
                              body=body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue(ip):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=get_house_info, queue='xiaozijia_house', consumer_tag=ip)
    channel.start_consuming()


if __name__ == '__main__':
    from multiprocessing import Process

    for i in ips:
        Process(target=consume_queue, args=(i,)).start()
    # consume_queue('1')