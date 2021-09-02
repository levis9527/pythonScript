import requests
from bs4 import BeautifulSoup
import re
import redis

client = redis.Redis()

url = '''http://61.132.132.30:8069/Exam/Exam'''
param = {
    'ExamThreeId': 'dc58bc00-aec4-e411-9d36-5404a655f7e4',
    'questionCategory': 10
}
dict_map = {}

index = 0


def get_html():
    r = requests.get(url, params=param)
    r.encoding = r.apparent_encoding
    return r.text


def option_to_list(option_soup):
    o_list = []
    for o in option_soup:
        o_str = o.next_sibling.strip().replace('\r', '').replace('\n', '')
        o_list.append(o_str)
    return o_list


def get_question_list(html):
    soup = BeautifulSoup(html, features="html.parser")
    q_list = soup.find_all(attrs={'class': 'paper_cont'})
    for q in q_list:
        tit = q.find(attrs={'class': 'tit'}).text

        option_soup = q.find_all(attrs={'class': 'option_rdo'})
        o_list = option_to_list(option_soup)

        ans = q.find(attrs={'class': 'AnswerArea'}).text

        tit = re.match(r'\d+\.(.*)', tit).group(1).strip()
        print(tit)
        print(o_list)
        print(ans.strip())

        save_to_file(tit, o_list, ans.strip())


def save_to_file(tit, o_list, ans):
    # 判断是否在redis，如果存在跳过
    if (dict_map.get(tit) is not None):
        print('重复数据---------------------------------------------------')
        return
    with open('data.txt', 'a+') as f:
        global index
        index = index + 1
        f.write(str(index) + ". " + tit + '\n')
        f.write(str(o_list) + '\n')
        f.write(ans + '\n')
        f.write('\n')
    dict_map[tit] = 1


if __name__ == '__main__':
    for _ in range(300):
        if index > 1000:
            break
        html = get_html()
        get_question_list(html)
