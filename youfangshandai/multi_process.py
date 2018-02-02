from second_put import BuildingId
from multiprocessing import Process
from thirdly_put import HouseId
from first_put import Construction

def start_worker2():
    worker = BuildingId()
    worker.consume_start()


def start_worker3():
    worker = HouseId()
    worker.consume_start()


if __name__ == '__main__':
    start_worker1 = Construction()
    start_worker1.get_constructionId()
    for i in range(100):
        Process(target=start_worker2).start()
        print('第%s个“消费进程”开启'%i)
    # for i in range(100):
    #     Process(target=start_worker3).start()
    #     print('第%s个“消费进程”开启' % i)
