from youfangshandai import first_put, second_put, third_put, put_into_mongo
from threading import Thread
from multiprocessing import Process
if __name__ == '__main__':
    # 获取小区的id
    con = first_put.Construction()
    Thread(target=con.get_constructionId).start()
    # 获取楼栋id
    build = second_put.BuildingId()
    Thread(target=build.consume_start).start()
    # 获取房屋id
    house = third_put.HouseId()
    for i in range(10):
        Thread(target=house.consume_start).start()
    # 入库
    Process(target=put_into_mongo.start_consume).start()
