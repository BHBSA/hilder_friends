**数据库存储地址以及字段**
--

<h4>优房闪贷，房估估，上海物业


+ <h5>优房闪贷：
192.168.0.235 库：friends 表：yfsd
+ 字段：
    + houseId  == 房号id
    + houseName  ==  房号名字
    + buildingId == 楼栋id
    + buildingName  == 房号id
    + constructionId   == 小区id
    + constructionName  ==  小区名字
    + address  ==  地址
    + cityId  ==  城市id
    + allAddress  ==  房号地址
    + estimateArea  ==  null
    + pinyin  ==  null
    + saleName  ==  null
    + loopLine  ==  null
    + endDate  ==  null
    + areaName  ==  null
    + conArrea  ==  null
    + city  ==  城市
    
---
<h5>上海物业：
192.168.0.235 库：wuye 表：
+ wuye_house_info
+ 字段
    + hou_no  ==  房号
    + hou_id  ==  房间id
    + unit_addr  ==  楼栋地址
    + unit_id  ==  楼栋id
    + unit_no  ==  楼栋名字
    + st_name_frst  ==  小区地址
    + hou_addr  ==  房号地址
    + sect_id  ==  小区id
+ wuye_sect_detail
+ 字段
    + message
        + 0
            + st_addr_frst  ==  小区地址
            + st_condo_hous_area  ==  建筑面积
            + st_name_frst  ==  小区名字
            + sect_finish_date  ==  竣工时间
            + sect_finish_date  ==  竣工时间
            + ho_id  ==  房号id
            + sect_id  ==  小区id
        + 1
        + 2
        + 3
    + flag  ==  标识符
    
---
<h5>房估估：
192.168.0.235，库：fgg 表：
+ fanggugu_house
+ 字段
    + house_id  ==  房间id                
    + house_name  ==  房间名字
    + ResidentialAreaID  ==  小区id
    + city_name  ==  城市
    + house_type  ==  房间类型
    + building_id  ==  楼栋id
+ fanggugu_price
+ 字段
    + RatioByLastMonthForPrice  == 距上月上调价格百分比
    + RatioByLastYearForPrice  == 距上年上调价格百分比
    + DistrictName  == 区域
    + x  == 坐标
    + y  == 坐标
    + ResidentialAreaID  == 小区id
    + city_name  == 城市
    + UnitPrice  == 均价
    + baseinfo
        + json
            + residentialareaMap
                + address == 小区地址
                + residentialareaName == 小区名字
+ fanggugu_building
+ 字段
    + ResidentialAreaID  == 小区id
    + city  == 城市
    + building_id  == 楼栋id
    + building_name  == 楼栋名字
    + building_type  == 楼栋类型





