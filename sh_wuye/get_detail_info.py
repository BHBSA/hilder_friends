import requests
import pymongo
import pika
from multiprocessing import Process

headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


def connect_rabbit(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, 5673))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


# 详情页 接口
url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getSectSDO.do'
wuye_coll = connect_mongodb('192.168.0.235', 27017, 'wuye', 'wuye_sect_id')
wuye_detail = connect_mongodb('192.168.0.235', 27017, 'wuye', 'wuye_sect_detail')
channel = connect_rabbit('192.168.0.235', 'wuye_sect_id')
proxies = {
    'https': '192.168.0.90:4234'
}


def callback(ch, method, properties, body):
    community_id = body.decode()
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"sect_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_id\"\r\n\r\n1801171076359845\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_name\"\r\n\r\n15021630956\r\n--0xKhTmLbOuNdArY--".format(
        community_id)
    try:
        response = requests.post(url=url, headers=headers, data=payload, verify=False, proxies=proxies)
        data = response.json()
        wuye_detail.insert_one(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(e)
        channel.basic_publish(exchange='',
                              routing_key='wuye_sect_id',
                              body=body,
                              )
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue='wuye_sect_id')
    channel.start_consuming()


if __name__ == '__main__':
    for i in range(10):
        Process(target=consume_queue).start()
