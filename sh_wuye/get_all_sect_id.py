import pymongo
import pika


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


wuye_coll = connect_mongodb('192.168.0.235', 27017, 'wuye', 'wuye_sect_id')
channel = connect_rabbit('192.168.0.235', 'wuye_sect_id')


def produce():
    for i in wuye_coll.find():
        sect_id = i['_id']
        print(sect_id)
        channel.basic_publish(exchange='',
                              routing_key='wuye_sect_id',
                              body=str(sect_id),
                              )
