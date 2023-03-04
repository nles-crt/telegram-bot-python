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


#---------跟简单的方式接收信息
'''from telegram import Update
import json

def handle_webhook_request(request):
    update = Update.de_json(json.loads(request.body), bot)
    message = update.message
    chat_id = message.chat_id
    text = message.text
'''    # do something with the chat_id and text

def getinfo(request):
    data = {}
    try:
        data_json = json.loads(request.body.decode('utf-8'))
        print(data_json)
        if 'status' in data_json:
            return False
        elif 'channel_post' in data_json:
            data = {
                'chat': data_json['channel_post']['chat']['id'],
                'text': data_json['channel_post']['text']
            }
        elif 'message' in data_json:
            message = data_json['message']
            chat_type = message['chat']['type']
            if 'group' in chat_type:
                data = {
                    'name': message['from'].get('last_name', '') + message['from'].get('first_name', ''),
                    'chat': message['chat']['id'],
                    'user': message['from']['id'],
                    'text': message['text'],
                    'is_bot': message['from'].get('is_bot', False),
                    'language_code': message['from'].get('language_code', '')
                }
            elif chat_type == 'private':
                data = {
                    'name': message['from'].get('last_name', '') + message['from'].get('first_name', ''),
                    'chat': message['chat']['id'],
                    'text': message['text'],
                    'user': message['from']['id'],
                    'is_bot': message['from'].get('is_bot', False),
                    'language_code': message['from'].get('language_code', '')
                }
    except json.JSONDecodeError:
        pass
    return data

bot_token = "6290859152:AAF7KhxgW7ReuImLxy0gYL-WbCtx81SLkbo"
def postdata(senddata):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": str(senddata["user"]),
        "text": senddata["text"],
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=data, proxies=proxies)
    return response.ok


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


openai.api_key = ("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")
os.environ["HTTP_PROXY"] = proxies["http"]
os.environ["HTTPS_PROXY"] = proxies["https"]

def mesopenai(text):
    response = requests.post(
        "https://api.openai.com/v1/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        },
        json={
            "model": 'text-davinci-003',
            "prompt": text,
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
    )
    if 'error' in response.json():
        aidata = 'key失效'
    else:
        aidata = response.json()['choices'][0]['text']
    return aidata


OPENAI_EDIT_URL = "https://api.openai.com/v1/engines/text-davinci-edit-001/edits"
OPENAI_HEADERS = {
    'Content-Type': "application/json",
    'Authorization': f"Bearer {openai.api_key}"
}

def eopenai(text):
    payload = {"input":"","instruction":text,"temperature":0.5,"top_p":1}
    response = requests.post(url=OPENAI_EDIT_URL, json=payload, headers=OPENAI_HEADERS)
    if 'error' in response.json():
        aidata = 'key失效'
    else:
        aidata = response.json()['choices'][0]['text']
    return aidata


def post(request):
    try:
        bigdata = getinfo(request)
    except:
        return HttpResponse('No success')

    text = bigdata.get('text')
    user_id = bigdata.get('chat')
    if request.body:
        if user_id < 0 and text == '资源':
            mess(user_id=user_id)
        elif '/start' in text:
            senddata = {'user': user_id, 'text': '使用方式\n/test  --->text-davinci-003 \n /code  --->text-davinci-edit-001 \n 试着发送/test 给我写一段php 接口'}
            postdata(senddata)
        elif '/test ' in text:
            senddata = {'user': user_id, 'text':'稍等几秒钟'}
            postdata(senddata)
            M_TEXT = text
            text = mesopenai(text=re.search(r'/test (.*)', text).group(1))
            senddata = {'user': user_id, 'text': f"{re.search(r'/test (.*)', M_TEXT).group(1)}" + text}
            postdata(senddata)
        elif '/code ' in text:
            senddata = {'user': user_id, 'text': '稍等几秒钟'}
            postdata(senddata)
            M_TEXT = text
            text = eopenai(text=re.search(r'/code (.*)', text).group(1))
            senddata = {'user': user_id, 'text': f"{re.search(r'/code (.*)', M_TEXT).group(1)}\n" + text}
            postdata(senddata)
        elif text == '我的信息':
            result = re.sub(r'[\'\"{}]', '', str(bigdata)).replace(',', '\n')
            senddata = {'user': user_id, 'text': result}
            postdata(senddata)
        else:
            senddata = {'user': user_id, 'text': text}
            postdata(senddata)

    return HttpResponse('success')

'''import threading

# 定义 runs_thread 函数
def runs_thread(interval):
    print("Timer thread is running")

# 启动 Timer 线程
interval = 1  # 1 秒钟调用一次 runs_thread
threading.Timer(interval, runs_thread, [interval]).start()'''