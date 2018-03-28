import requests
from lib.mongo import Mongo


class Login(object):
    def __init__(self):
        m = Mongo('192.168.0.235', 27017)
        self.connection = m.get_connection()

    def to_request(self, user_name):
        s = requests.session()
        parms = {'pwd_login_username': user_name,
                 'pwd_login_password': '4ac9fa21a775e4239e4c72317cdca870',
                 'remembermeVal': 0}
        while True:
            data = {"app_name": 'fgg'}
            ip = requests.post(url='http://192.168.10.85:8999/get_one_proxy', data=data).text
            print(ip)
            proxies = {'http': ip}
            try:
                s.get(url='http://www.fungugu.com/DengLu/doLogin_noLogin', params=parms,
                      proxies=proxies, timeout=5)
                jrbqiantai = s.cookies.get_dict()['jrbqiantai']
                return jrbqiantai
            except Exception as e:
                formdata = {"app_name": 'fgg', "status_code": 1, "ip": ip}
                response = requests.post(url='http://192.168.10.85:8999/send_proxy_status', data=formdata, timeout=5)
                status = response.text
                print('更新' + status)

    def put_mongo(self):
        coll_login = self.connection['fgg']['login']
        coll_user = self.connection['fgg']['user_info']
        for i in coll_user.find():
            user_name = i['user_name']
            jrbqiantai = self.to_request(user_name)
            data = {
                'user_name': user_name,
                'jrbqiantai': jrbqiantai
            }
            coll_login.update({'user_name': user_name}, {'$set': data}, True)
            print('cookie')
        return 200

    def update_mongo(self, user_name):
        coll_login = self.connection['fgg']['login']
        jrbqiantai = self.to_request(user_name)
        data = {
            'user_name': user_name,
            'jrbqiantai': jrbqiantai
        }
        coll_login.update({'user_name': user_name}, {'$set': data})
        jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
        return jrbqiantai
