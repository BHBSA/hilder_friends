import pymongo


def connect_mongodb(host, port, database, collection):
    client = pymongo.MongoClient(host, port)
    db = client[database]
    coll = db.get_collection(collection)
    return coll


set_ = set([])
comm_coll = connect_mongodb('192.168.0.136', 27017, 'fangjia', 'seaweed')
key_coll = connect_mongodb('192.168.0.235', 27017, 'wuye', 'key_name')
list_ = comm_coll.find({'city': '上海'})
count = 0
for i in list_:
    name = i['name']
    for i in name:
        print(i)
        data = {
            '_id': i
        }
        try:
            key_coll.insert(data)
        except Exception as e:
            print('key重复')
    count += 1
    print(count)
