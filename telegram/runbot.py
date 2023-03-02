import time
import datetime

from django.http import HttpResponse
from django.shortcuts import render
import requests
from lxml import etree
import re
import json
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
#使用本地代理访问api.telegram域名
def getinfo(request):
    if request.body:
        data = request.body.decode('utf-8')
        print('\n\n'+str(data)+'\n\n')
        data_json = json.loads(data)
        if 'channel_post' in data_json:
            channel_id = data_json['channel_post']['chat']['id']
            channel_text = data_json['channel_post']['text']
            data = {'user':channel_id, 'text':channel_text}
        elif 'message' in data_json:
            user_id = data_json['message']['from']['id']
            user_text = data_json['message']['text']
            data = {'user':user_id, 'text':user_text}
        print(data)
        return data


def postdata(senddata):
    headers = {'Content-Type': 'application/json'}
    data = {
        'chat_id': str(senddata['user']),
        'text': senddata['text'],
        'parse_mode':'Markdown'
    }
    print(data)
    send_text = 'https://api.telegram.org/bot这里设置机器人tk/sendMessage'
    if requests.post(url=send_text,proxies=proxies, headers=headers,json=data).status_code == 200:
        code = True
    else:
        code = False
    return code
def mess(user_id):
    if user_id is None:
        user_id = #设置频道 例如-1001501432435
    url = 'https://www.10fzw.com/'
    data = requests.get(url=url, proxies=proxies).text
    selector = etree.HTML(data)
    id = selector.xpath("//div[@class='center']/div[@class='title']/font/text()")
    id = re.sub("\D", "", id[0])
    row = selector.xpath("//ul/ul/li[@class='new']/a")
    if int(id) > 1:
        for i in range(len(row)):
            bt = selector.xpath("//ul/ul/li[@class='new']/a/text()")[i]
            href = selector.xpath("//ul/ul/li[@class='new']/a/@href")[i]
            newdata = requests.get(url=href, proxies=proxies).text
            selectornewdata = etree.HTML(newdata)
            article_content = selectornewdata.xpath("//h3[@class='article-title']/text()")
            link = selectornewdata.xpath('//span[@class="Fengdown"]/@onclick')[0]
            tele = selectornewdata.xpath("//b[@class='bq-wg']/a/text()")[0]
            link = re.findall(r"window.open\('(.*?)'\);", link)
            data = article_content[0] + '\n' + link[0] + '\n#' + tele + ' '
            print(data)
            senddata = {'user': user_id, 'text': data}
            postdata(senddata=senddata)

def post(request):
    try:
        text = getinfo(request)['text']
        user_id = getinfo(request).get('user')
        if request.body:
            print(user_id, text)
            if user_id < 0 and text == '资源':
                mess(user_id=user_id)
            else:
                senddata = {'user': user_id, 'text': text}
                postdata(senddata)
    except:
        print('在线刷新')
    return HttpResponse('success')



        #href_content = selector.xpath('//ul/ul/li[@class='new']/a/@href')


while True:
    # 获取当前时间
    now = datetime.datetime.now()
    print(now.hour, now.minute, now.second)
    # 判断是否到了执行时间（每天中午12点）
    if now.hour == 12 and now.minute == 0 and now.second == 0:
        # 执行函数
        mess(None)
        # 等待到第二天再执行
        time.sleep(24 * 60 * 60)



