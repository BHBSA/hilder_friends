import requests
import pymongo
import pika

headers = {
    'User-Agent': 'IOS-wuye/360;iOS;11.1.2;iPhone',
    'Content-Type': 'multipart/form-data; charset=gb18030; boundary=0xKhTmLbOuNdArY'
}
# 搜索提示 接口
url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getSectByAddrSDO.do'




# 门牌号 接口
# url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getUnitListSDO.do'
# payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"sect_id\"\r\n\r\n120302190341347\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n1\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n20\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select\"\r\n\r\n\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_name\"\r\n\r\n15021630956\r\n--0xKhTmLbOuNdArY--"
# url = 'https://www.962121.net/wyweb/962121appyzbx/v7/sect/getHouListSDO.do'
# payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n1\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"unit_id\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select\"\r\n\r\n\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n20\r\n--0xKhTmLbOuNdArY\r\n--0xKhTmLbOuNdArY--".format(unit_id)
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


wuye_coll = connect_mongodb('192.168.0.235', 27017, 'wuye', 'wuye_sect_id')
channel = connect_rabbit('192.168.0.235', 'key_name')
count = 0
key_coll = connect_mongodb('192.168.0.235', 27017, 'wuye', 'key_name')


def callback(ch, method, properties, body):
    name = body.decode()
    print(name)
    payload = "--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"sect_flag\"\r\n\r\n0\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"currentPage\"\r\n\r\n0\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"pageSize\"\r\n\r\n10000\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"au_name\"\r\n\r\n15021630956\r\n--0xKhTmLbOuNdArY\r\nContent-Disposition: form-data; name=\"select_addr\"\r\n\r\n{0}\r\n--0xKhTmLbOuNdArY--".format(
        name).encode('gb18030')
    res = requests.post(url=url, headers=headers, data=payload, verify=False)
    for i in res.json()['message']:
        sect_id = i['sect_id']
        data = {
            '_id': sect_id
        }
        try:
            wuye_coll.insert(data)
            # print(data)
        except Exception as e:
            print('key重复')
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue='key_name')
    channel.start_consuming()


if __name__ == '__main__':
    consume_queue()
