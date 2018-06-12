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
    with open('小资家_detail_fast.log', 'r') as f:
        paper = f.read()
        Id = re.search('HouseInfo/(.*?)"', paper, re.S | re.M)
        BuildName = re.search('BuildName="(.*?)"', paper, re.S | re.M)
        ConstructionName = re.search('ConstructionName="(.*?)"', paper, re.S | re.M)
        data = {
            'ConstructionName': ConstructionName,
            'BuildName': BuildName,
            'Id': Id,
        }
        channel.basic_publish(exchange='',
                              routing_key='xiaozijia_house_detail',
                              body=json.dumps(data))
        print(data)


if __name__ == '__main__':
    log_rabbit()