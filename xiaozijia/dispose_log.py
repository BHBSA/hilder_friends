from lib.rabbitmq import Rabbit
import re
from lib.mongo import Mongo
import json

# mongo
m = Mongo('192.168.0.235', 27017)
coll_build = m.connect['friends']['xiaozijia_house_fast']

# rabbit
r = Rabbit('192.168.0.190', 5673)
connection = r.get_connection()
channel = connection.channel()
channel.queue_declare(queue='xiaozijia_house_detail')


def log_rabbit():
    with open('小资家_build_fast.log', 'rb') as f:
        paper = f.read().decode('utf-8')
        num_list = re.findall('HouseInfo/(.*?)"', paper, re.S | re.M)
        for i in num_list:
            try:
                Id = i
                house_data = coll_build.find_one({'Id': int(Id)})
                ConstructionName = house_data['ConstructionName']
                Name = house_data['Name']
                data = {
                    'ConstructionName': ConstructionName,
                    'BuildName': Name,
                    'Id': Id,
                }
                channel.basic_publish(exchange='',
                                      routing_key='xiaozijia_house_detail',
                                      body=json.dumps(data))
                print(data)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    log_rabbit()
