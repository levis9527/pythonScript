import requests
# from bs4 import BeautifulSoup
import re
import json
import pymongo
import time
import sys

client = pymongo.MongoClient('127.0.0.1')

db = client.test
sleep_seconds = 0

# 根据uid获取jsonp数据


def get_jsonp(uid):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48",
        "cookie": "bsource=search_bing; _uuid=61D3DC71-C692-98AF-6202-C95EF894110B85399infoc; buvid3=71435C96-E742-4A81-A9D9-14B5D0D17B0E13421infoc; bfe_id=6f285c892d9d3c8f8f020adad8bed553; CURRENT_FNVAL=81; blackside_state=1; sid=l3osdfqq; rpdid=|(k|u)mJRumn0J'uYkJmk~)m~",
        "referer": "https://www.bilibili.com/video/BV1zb4y1d7Br?spm_id_from=333.851.b_7265706f7274466972737432.7"
    }
    url = "https://api.bilibili.com/x/web-interface/card?jsonp=jsonp&mid=%s&photo=1&callback=jsonCallback_bili_370452811258599861" % uid
    r = requests.get(url, headers=headers)
    return r.text

# jsonp转换成json对象


def jsonp2json(jsonp):
    json_str = re.match(".*?({.*}).*", jsonp, re.S).group(1)
    return json.loads(json_str)

# 打印json数据，自定义打印


def print_json(json_data):
    code = json_data.get("code")
    if code == -412:
        raise Exception("请求被拦截")
    if code != 0:
        print("code 错误 %s, 跳过执行" % code)
        return

    data = json_data.get("data")
    card = data.get("card")

    mid = card.get("mid")
    name = card.get("name")
    sign = card.get("sign")
    fans = card.get("fans")

    print("%s\t\t%s\t\t%s\t\t%s" % (mid, name, sign, fans))

# 保存json数据到mongoDB


def save_json_mongo(json_data):
    code = json_data.get("code")
    if code == -412:
        raise Exception("请求被拦截")
    if code != 0:
        print("code 错误 %s, 跳过执行" % code)
        return

    data = json_data.get("data")
    db.bilibili.insert_one(data)

# 获取最大mid（uid）


def get_max_mid():
    pip = [
        {
            '$group': {
                '_id': 'max',
                'max_value': {
                    '$max': {
                        '$toInt': '$card.mid'
                    }
                }
            }
        }
    ]
    return db.bilibili.aggregate(pip).next()['max_value']

# 循环执行业务逻辑（循环100次）


def loop_excute(size):
    max_mid = get_max_mid()  # 最大mid

    start = max_mid + 1  # 开始id
    # print("%s\t\t%s\t\t%s\t\t%s" % ("mid", "name", "sign", "fans"))
    for i in range(size):
        uid = i + start
        jsonp = get_jsonp(uid)
        json_data = jsonp2json(jsonp)
        print_json(json_data)
        # 保存数据到mongoDB
        save_json_mongo(json_data)

# 测试数据（测试是否通过）


def test_data():
    max_mid = get_max_mid()  # 最大mid

    jsonp = get_jsonp(max_mid)
    json_data = jsonp2json(jsonp)
    print(json_data)
    print_json(json_data)

# 添加休眠时间（每次休眠时间添加30秒，最多添加到600秒）


def add_sleep_seconds():
    global sleep_seconds
    if sleep_seconds < 600:
        sleep_seconds = sleep_seconds + 30

# 重设休眠时间，如果完整跑完没有拦截请求，那么休眠时间重置为30秒


def reset_sleep_seconds():
    global sleep_seconds
    sleep_seconds = 0


if __name__ == '__main__':
    test = True
    argv = sys.argv
    if (len(argv) == 2 and argv[1] == 'run'):
        print("=======================>运行脚本")
        while True:
            try:
                loop_excute(30)
                reset_sleep_seconds()
            except Exception as e:
                print(e)
                add_sleep_seconds()
            print("=======================>start sleep %s s %s" %
                  (sleep_seconds, time.strftime('%Y-%m-%d %H:%M:%S')))
            time.sleep(sleep_seconds)
            print("=======================>end sleep %s s %s" %
                  (sleep_seconds, time.strftime('%Y-%m-%d %H:%M:%S')))
    else:
        print("=======================>测试链接")
        try:
            test_data()
        except Exception as e:
            print(e)


# 返回json数据
# {'code': 0, 'message': '0', 'ttl': 1, 'data': {'card': {'mid': '4587', 'name': 'zczczc', 'approve': False, 'sex': '男', 'rank': '10000', 'face': 'http://i0.hdslb.com/bfs/face/3a7d1c9ff8bf74da1f22eb138ca66f649ca2198c.jpg', 'DisplayRank': '0', 'regtime': 0, 'spacesta': 0, 'birthday': '', 'place': '', 'description': '', 'article': 0, 'attentions': [], 'fans': 3, 'friend': 33, 'attention': 33, 'sign': '', 'level_info': {'current_level': 4, 'current_min': 0, 'current_exp': 0, 'next_exp': 0}, 'pendant': {'pid': 0, 'name': '', 'image': '', 'expire': 0, 'image_enhance': '', 'image_enhance_frame': ''}, 'nameplate': {'nid': 0, 'name': '', 'image': '', 'image_small': '', 'level': '', 'condition': ''}, 'Official': {'role': 0, 'title': '', 'desc': '', 'type': -1}, 'official_verify': {'type': -1, 'desc': ''}, 'vip': {'type': 0, 'status': 0, 'due_date': 0, 'vip_pay_type': 0, 'theme_type': 0, 'label': {'path': '', 'text': '', 'label_theme': '', 'text_color': '', 'bg_style': 0, 'bg_color': '', 'border_color': ''}, 'avatar_subscript': 0, 'nickname_color': '', 'role': 0, 'avatar_subscript_url': '', 'vipType': 0, 'vipStatus': 0}}, 'space': {'s_img': 'http://i1.hdslb.com/bfs/space/768cc4fd97618cf589d23c2711a1d1a729f42235.png', 'l_img': 'http://i1.hdslb.com/bfs/space/cb1c3ef50e22b6096fde67febe863494caefebad.png'}, 'following': False, 'archive_count': 0, 'article_count': 0, 'follower': 3}}
