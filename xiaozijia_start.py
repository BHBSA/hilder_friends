from xiaozijia.put_rabbit_num import put_rabbit
from xiaozijia.get_comm_rabbit import consume_queue as comm_sumer
from xiaozijia.get_build_rabbit import consume_queue as build_sumer
from xiaozijia.get_house_rabbit import consume_queue as house_sumer
from xiaozijia.get_house_detail_rabbit import consume_queue as detail_sumer
from multiprocessing import Process

if __name__ == '__main__':
    # 放入1-35数字
    Process(target=put_rabbit).start()
    for i in range(10):
        Process(target=comm_sumer).start()
    for i in range(10):
        Process(target=build_sumer).start()
    for i in range(30):
        Process(target=house_sumer).start()
    for i in range(30):
        Process(target=detail_sumer).start()
