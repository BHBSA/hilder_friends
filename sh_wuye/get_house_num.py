import pymongo
import pika
import requests
import json
from multiprocessing import Process


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


headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}
proxies = {
    'https': '192.168.0.90:4234'
}
url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getHouListSDO.do'

wuye_house = connect_mongodb('192.168.0.235', 27017, 'wuye', 'wuye_house_info')
channel = connect_rabbit('192.168.0.235', 'key_name')


def callback(ch, method, properties, body):
    message = body.decode()
    data = json.loads(message)
    unit_no = data['unit_no']
    unit_id = data['unit_id']
    unit_addr = data['unit_addr']
    sect_id = data['sect_id']
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n1\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"unit_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select\"\r\n\r\n\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n20\r\n--0xKhTmLbOuNdArY--".format(
        unit_id)
    try:
        response = requests.post(url=url, headers=headers, data=payload, verify=False, proxies=proxies)
        data = response.text
        print(data)
        message = data['message']
        print(message)
        for i in message:
            hou_addr = i['hou_addr']
            st_name_frst = i['st_name_frst']
            hou_no = i['hou_no']
            hou_id = i['hou_id']
            data = {
                'unit_id': unit_id,
                'sect_id': sect_id,
                'unit_addr': unit_addr,
                'unit_no': unit_no,
                'hou_addr': hou_addr,
                'st_name_frst': st_name_frst,
                'hou_no': hou_no,
                'hou_id': hou_id,
            }
            print(data)
            wuye_house.insert_one(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(e)
        channel.basic_publish(exchange='',
                              routing_key='wuye_building_id',
                              body=body,
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue='wuye_building_id')
    channel.start_consuming()


if __name__ == '__main__':
    for i in range(10):
        Process(target=consume_queue).start()
