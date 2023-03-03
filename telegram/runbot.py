import time
import datetime
import os
import openai
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

def getinfo(request):
    if request.body:
        data = request.body.decode('utf-8')
        data_json = json.loads(data)
        print(data_json)
        if 'status' in data_json:
            return False
        if 'channel_post' in data_json:
            channel_id = data_json['channel_post']['chat']['id']
            channel_text = data_json['channel_post']['text']
            data = {'chat':channel_id,'text':channel_text}
        elif 'message' in data_json:
            type = data_json['message']['chat']['type']
            print(type)
            if 'group' in type:
                user_id = data_json['message']['from']['id'] #用户id
                chat = data_json['message']['chat']['id']
                user_text = data_json['message']['text'] #获取的内容
                is_bot = data_json['message']['from']['is_bot']
                language_code = data_json['message']['from']['language_code']
                name = data_json['message']['from']['last_name'] + data_json['message']['from']['first_name']
                data = {'name':name,'chat':chat,'user': user_id,'text':user_text,'is_bot':is_bot,'language_code':language_code}
            elif type == 'private':
                user_id = data_json['message']['from']['id']
                user_text = data_json['message']['text']
                chat = data_json['message']['chat']['id']
                is_bot = data_json['message']['from']['is_bot']
                language_code = data_json['message']['from']['language_code']
                name = data_json['message']['from']['last_name'] + data_json['message']['from']['first_name']
                data = {'name':name, 'chat':user_id, 'text':user_text, 'is_bot':is_bot, 'language_code':language_code}

    return data


def postdata(senddata):
    headers = {'Content-Type': 'application/json'}
    data = {
        'chat_id': str(senddata['user']),
        'text': senddata['text'],
        'parse_mode':'Markdown'
    }
    print(data)
    send_text = 'https://api.telegram.org/bot6290859152:AAF7KhxgW7ReuImLxy0gYL-WbCtx81SLkbo/sendMessage'
    if requests.post(url=send_text,proxies=proxies, headers=headers,json=data).status_code == 200:
        code = True
    else:
        code = False
    return code


def mess(user_id):
    if user_id is None:
        user_id = -1001501401953
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
            senddata = {'user': user_id, 'text': data}
            postdata(senddata=senddata)




def mesopenai(text):
    openai.api_key = ("**")
    os.environ["HTTP_PROXY"] = proxies["http"]
    os.environ["HTTPS_PROXY"] = proxies["https"]
    response = requests.post(
        "https://api.openai.com/v1/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        },
        json={
            "model": "text-davinci-003",
            "prompt": text,
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }, proxies=proxies)
    if 'Incorrect' in response.json():
        aidata = 'key失效'
    else:
        aidata = response.json()['choices'][0]['text']
    return aidata

def post(request):
    try:
        bigdata = getinfo(request)
    except:
        print('刷新')
        return HttpResponse('No success')
    text = bigdata['text']
    user_id = bigdata['chat']
    if request.body:
        print(user_id, text)
        if user_id < 0 and text == '资源':
            mess(user_id=user_id)
        elif '/test ' in text:
            print('分支二')
            senddata = {'user': user_id, 'text':'稍等几秒钟'}
            postdata(senddata)
            text = mesopenai(text=text.split('/test ')[1].strip())
            senddata = {'user': user_id, 'text':text}
            postdata(senddata)
        elif text == '我的信息':
            print('分支三')
            result = re.sub(r'[\'\"{}]', '', str(bigdata))
            result = re.sub(r',', '\n', result)
            senddata = {'user': user_id, 'text':str(result)}
            postdata(senddata)
        else:
            senddata = {'user': user_id, 'text': text}
            postdata(senddata)
    return HttpResponse('success')



        #href_content = selector.xpath('//ul/ul/li[@class='new']/a/@href')


'''while True:
    # 获取当前时间
    time.sleep(0.8)
    now = datetime.datetime.now()
    print(now.hour, now.minute, now.second)
    # 判断是否到了执行时间（每天中午12点）
    if now.hour == 12 and now.minute == 0 and now.second == 0:
        # 执行函数
        mess(None)
        # 等待到第二天再执行
        time.sleep(24 * 60 * 60)

'''

