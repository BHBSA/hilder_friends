import requests


def get_headers():
    login_url = 'http://www.xiaozijia.cn/User/AjaxLogin'
    data = {
        'UserAccount': '15893020331',
        'AccountType': '0',
        'Password': 'goojia123456',
        'RememberMe': 'false',
        'returnUrl': '',
    }

    s = requests.session()
    response = s.post(login_url, data=data)
    html = response.text
    cookie_list = s.cookies.items()
    cookie_ = ''
    for i in cookie_list:
        key = i[0]
        value = i[1]
        string = key + '=' + value + ';'
        cookie_ += string

    headers = {
        'Cookie': cookie_
    }
    return headers
