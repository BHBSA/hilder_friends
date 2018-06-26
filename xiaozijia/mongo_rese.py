# from lib.mongo import Mongo
#
# m = Mongo('114.80.150.196', 27017)
# coll_comm = m.connect['friends']['xiaozijia_comm_fast_test']
# coll_house = m.connect['friends']['xiaozijia_house_fast']
#
# count = 0
# for i in coll_comm.find(no_cursor_timeout=True):
#     ConstructionId = i['ConstructionId']
#     count +=1
#     print(count)
#     if not coll_house.find_one({'ConstructionId': ConstructionId}):
#         coll_comm.remove({'ConstructionId': ConstructionId})
#         print(ConstructionId)



# -------------------------------------
# 小区格式化楼栋
from lib.mongo import Mongo

m = Mongo('114.80.150.196', 27017)
coll_comm = m.connect['friends']['xiaozijia_comm_fast_test']
coll_build = m.connect['friends']['xiaozijia_build_fast_copy']

count = 0
for i in coll_build.find(no_cursor_timeout=True):
    ConstructionId = i['ConstructionId']
    IdSub = i['IdSub']
    count += 1
    print(count)
    if not coll_comm.find_one({'ConstructionId': ConstructionId}):
        coll_build.remove({'IdSub': IdSub})
        print(IdSub)
# -------------------------------------


# rabbit方式
# from lib.mongo import Mongo
# from lib.rabbitmq import Rabbit
# import json
#
# m = Mongo('114.80.150.196', 27017)
# coll_comm = m.connect['friends']['xiaozijia_comm_fast_test']
# coll_build = m.connect['friends']['xiaozijia_build_fast_copy']
#
# r = Rabbit('127.0.0.1', 5673)
# channel = r.get_channel()
# channel.queue_declare(queue='xiaozijia_build')
# count = 0
#
#
# def callable(ch, method, properties, body):
#     body_json = json.loads(body.decode())
#     ConstructionId = body_json['ConstructionId']
#     IdSub = body_json['IdSub']
#     global count
#     count += 1
#     print(count)
#     if not coll_comm.find_one({'ConstructionId': ConstructionId}):
#         coll_build.remove({'IdSub': IdSub})
#         print(IdSub)
#     ch.basic_ack(delivery_tag=method.delivery_tag)
#
#
# def consume_queue():
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(consumer_callback=callable, queue='xiaozijia_build')
#     channel.start_consuming()
#
#
# if __name__ == '__main__':
#     consume_queue()
