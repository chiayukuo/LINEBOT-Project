import random
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


import requests

import json





import gspread
from oauth2client.service_account import ServiceAccountCredentials






app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('VvzxwO3VDPuMelekj0EYAq2q+PdhqgbNlSvDNwsqCMn5J1Uxc5MdV9wjE540fvlxCTtx6ZqT6SuVLR/CWk1AarZbXJSKcWHkjkIXTYUaWSyJcerJen46VWjLcl9hPMXdk5HQXMX5IFkNsawVUkCIGwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('51f7ea3fdc737dca85035afd50434764')

@app.route('/')
def index():
    return "<p>Hello World!</p>"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    profile = line_bot_api.get_profile('')

    if event.message.text == 'p':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='HI'+profile.user_id))

    if event.message.text == '愛你':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='我也愛你♥'))

    elif event.message.text== '說明':    

        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='輸入「配對餐廳」：\n不知道這餐該吃什麼？讓LineBot幫你決定！\n根據你的嗜好，一步步篩選出最適合自己的餐廳♥\n\n輸入「搜尋 餐廳名稱」（中間有半形空格）：\n若已經知道明確的餐廳名稱，\n透過此功能可得到店家的詳細資訊哦！\n\n輸入「回報」：\n程式使用上如有發現問題，\n或是找不到自己心儀的餐廳…\n請替我們填寫表單回報錯誤，以提供更好的使用體驗！\n\n輸入「新增 自訂名稱 喜愛的餐廳名稱」（中間有半形空格）：\n此功能提供使用者簡單記錄自己喜愛的餐廳，\n並可在日後查看！「自訂名稱」的部分可自行命名，\n之後只輸要輸入自訂名稱，就可查到自己的簡易筆記！\n\n輸入「最愛 自訂名稱」（中間有半形空格）：\n此功能可查看自己先前所記錄過的餐廳、簡易筆記！\n（使用時請務必牢記自訂名稱！）'))
    elif event.message.text[:2] == '新增':
        try:
            a = event.message.text.split()

            scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

            creds = ServiceAccountCredentials.from_json_keyfile_name("PythonUpload.json", scope)

            client = gspread.authorize(creds)

            sheet = client.open("Record").sheet1  # Open the spreadhseet

            sheet.append_row([a[1],a[2]])
            
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='添加最愛成功！'))

        except:

            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='添加最愛失敗！\n格式應為:新增 你的最愛名字 要填加的店名 \n如仍有錯誤，請輸入"回報"填寫錯誤表單。'))

        
    elif event.message.text == '回報':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='回饋/錯誤回報表單如下:\nhttps://forms.gle/qxMQbkwfy4sfRL5B8\n感謝你的填寫！\n一起挖掘更多美食！！'))



    elif event.message.text[:2] == '搜尋':

        try:

            a = event.message.text.split()
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if a[1] in i ['gsx$店名']['$t'] :
                    shop.append(i ['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)

            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='搜尋失敗！請確認名稱、格式是否有誤。\n\n-可輸入"說明"看更詳盡的操作方式！\n-輸入"回報"推薦我們更多餐廳！'))
    elif event.message.text[:2] == '最愛':
        try:
            a = event.message.text.split()
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1AmvC2slGjiT1HajBwTkrWyzP9gI8aCF6ouuVF6cfk40/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            shop = []
            for i in parse['feed']['entry']:
                if a[1] in i ['gsx$name']['$t'] :
                    C = ''.join(i['gsx$store']['$t'])
                    shop.append(C)
                    
            shop1=[]
            for i in shop:
                i = '-' + i
                shop1.append(i)
            end ='\n'.join(shop1)

            
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='本次搜尋結果如下！{}:\n'.format(a[1])+end))

        except :
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='搜尋失敗 ！請確認格式是否有誤。\n可輸入"說明"看更詳盡的操作方式！'))
    elif event.message.text == '配對餐廳':
        line_bot_api.reply_message(event.reply_token, buttons_message())



    
    elif event.message.text == "隨便來點什麼吧！":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=love()))

    elif event.message.text == "開始進行搜尋！":
        line_bot_api.reply_message(event.reply_token,buttons_messagebd())

    elif event.message.text == "寶寶想吃早餐！":
        line_bot_api.reply_message(event.reply_token,buttons_messagenrB())

    elif event.message.text == "寶寶想吃正餐！":
        line_bot_api.reply_message(event.reply_token,buttons_messagenrN())
        
    elif event.message.text == "寶寶肚子餓了！":
        line_bot_api.reply_message(event.reply_token,buttons_messagenrA())

        
    elif event.message.text == "今天早餐想吃飯！":
        line_bot_api.reply_message(event.reply_token,buttons_messageBRF())

    elif event.message.text == "今天早餐想吃麵！":
        line_bot_api.reply_message(event.reply_token,buttons_messageBNF())

    elif event.message.text == "今天早餐隨便吃！":
        line_bot_api.reply_message(event.reply_token,buttons_messageBOF())







    elif event.message.text == "今天正餐想吃飯！":
        line_bot_api.reply_message(event.reply_token,buttons_messageNRF())

    elif event.message.text == "今天正餐想吃麵！":
        line_bot_api.reply_message(event.reply_token,buttons_messageNNF())

    elif event.message.text == "今天正餐隨便吃！":
        line_bot_api.reply_message(event.reply_token,buttons_messageNOF())




        

    elif event.message.text == "嘴饞想吃飯！":
        line_bot_api.reply_message(event.reply_token,buttons_messageARF())

    elif event.message.text == "嘴饞想吃麵！":
        line_bot_api.reply_message(event.reply_token,buttons_messageANF())

    elif event.message.text == "嘴饞隨便吃！":
        line_bot_api.reply_message(event.reply_token,buttons_messageAOF())

    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='是不是格式錯誤了呢！\n\n-輸入"說明"查看詳細的操作方式\n-輸入"回報"給我們更多建議！'))




    



def love():
    
    
    b = random.randint(1,96)
    b = b+2
    
    response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
    parse = json.loads(response_dynamic.text)
    for i in parse['feed']['entry'][b-2:b-1]:
        a = i['content']['$t']
        a = a.split(',')
        a.insert(0,'♥久等了！本次篩選結果如下:')
        a.insert(1,'---------')
        a.insert(3,'---------')
        a ='\n'.join(a)
        return a






#Postback
@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        if event.postback.data == '早飯中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t']:
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)

            
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

            

        if event.postback.data == '早飯日':

            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t']:
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)

            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='a'))


            

        if event.postback.data == '早飯西':


            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t'] :
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))



        if event.postback.data == '早飯':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '早' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

            

        if event.postback.data == '早麵中':
            
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t']  :
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '早麵日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t']  :
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '早麵西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']  :
                        if '早' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))


        if event.postback.data == '早麵':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '早' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))


        if event.postback.data == '早都可中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '中' in i ['gsx$食物風格']['$t']  :
                    if '早' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
            

        if event.postback.data == '早都可日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '日' in i ['gsx$食物風格']['$t']  :
                    if '早' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
            
        if event.postback.data == '早都可西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '西' in i ['gsx$食物風格']['$t']  or '東' in i ['gsx$食物風格']['$t'] :
                    if '早' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '早都可':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '早' in i ['gsx$早餐正餐消夜']['$t']:
                    shop.append(i['gsx$店名']['$t'])
                        
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))






        if event.postback.data == '正飯中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t']  :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正飯日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t']  :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正飯西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']  :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正飯':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :

                    if '正' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))




        if event.postback.data == '正麵中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t'] :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正麵日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t']  :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))


        if event.postback.data == '正麵西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']  :
                        if '正' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正麵':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :

                    if '正' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))


            

        if event.postback.data == '正都可中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '中' in i ['gsx$食物風格']['$t'] :
                    if '正' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正都可日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '日' in i ['gsx$食物風格']['$t']  :
                    if '正' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正都可西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']  :
                    if '正' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '正都可':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '正' in i ['gsx$早餐正餐消夜']['$t']:
                    shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))


            

        if event.postback.data == '消飯中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t'] :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消飯日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t']  :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消飯西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']  :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
        if event.postback.data == '消飯':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '飯' in i ['gsx$種類']['$t'] :

                    if '消' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

            

        if event.postback.data == '消麵中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '中' in i ['gsx$食物風格']['$t'] :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消麵日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '日' in i ['gsx$食物風格']['$t'] :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消麵西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :
                    if '西' in i ['gsx$食物風格']['$t'] or '東'in i ['gsx$食物風格']['$t'] :
                        if '消' in i ['gsx$早餐正餐消夜']['$t']:
                            shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消麵':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])
                if '麵' in i ['gsx$種類']['$t'] :

                    if '消' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
            

        if event.postback.data == '消都可中':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '中' in i ['gsx$食物風格']['$t']:
                    if '消' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消都可日':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '日' in i ['gsx$食物風格']['$t'] :
                    if '消' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

            
        if event.postback.data == '消都可西':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])

                if '西' in i ['gsx$食物風格']['$t'] or '東' in i ['gsx$食物風格']['$t']:
                    if '消' in i ['gsx$早餐正餐消夜']['$t']:
                        shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

        if event.postback.data == '消都可':
            response_dynamic = requests.get('https://spreadsheets.google.com/feeds/list/1O4jtk852-5rLDQjL_8L1uP5pBBTZoyKXpRTFwhFjwUY/od6/public/values?alt=json')
            parse = json.loads(response_dynamic.text)
            total = []
            shop = []
            for i in parse['feed']['entry']:
                total.append(i['gsx$店名']['$t'])


                if '消' in i ['gsx$早餐正餐消夜']['$t']:
                    shop.append(i['gsx$店名']['$t'])
            a=random.sample(shop,1)
            a = ''.join(a)
            p=total.index(a)
            p=p+2
            
            for i in parse['feed']['entry'][p-2:p-1]:
                a = i['content']['$t']
                a = a.split(',')
                a.insert(0,'♥久等了！本次篩選結果如下:')
                a.insert(1,'---------')
                a.insert(3,'---------')
                a ='\n'.join(a)
                
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))

    except:
        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='唉呀，目前沒有符合你條件的餐廳…\n\n-建議把條件放寬再試一次\n-輸入"回報"，推薦我們更多餐廳！'))        
            















#TemplateSendMessage - ButtonsTemplate (按鈕介面訊息)
def buttons_message():
    message = TemplateSendMessage(
        alt_text='今天想吃什麼～',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="今天想吃什麼？",
            text="開始選擇你想進行的搜索模式吧！",
            actions=[

                MessageTemplateAction(
                    label="店家進階搜尋（喜好配對）",
                    text="開始進行搜尋！"
                ),

                MessageTemplateAction(
                    label="隨便！",
                    text="隨便來點什麼吧！"
                )
                    
            ]
        )
    )
    return message


#吃哪餐
def buttons_messagebd():
    message = TemplateSendMessage(
        alt_text='這是哪一餐～',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="吃早餐/正餐？",
            text="開始選擇你今天的口味吧！",
            actions=[

                MessageTemplateAction(
                    label="吃早餐！",
                    text="寶寶想吃早餐！"
                ),
                MessageTemplateAction(
                    label="吃正餐！",
                    text="寶寶想吃正餐！"
                ),

                MessageTemplateAction(
                    label="吃消夜/現在有點嘴饞！",
                    text="寶寶肚子餓了！"
                )
                    
            ]
        )
    )
    return message

#飯麵1
def buttons_messagenrB():
    message = TemplateSendMessage(
        alt_text='想吃飯還是麵？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃飯/吃麵？",
            text="告訴我你目前的胃口吧！",
            actions=[

                MessageTemplateAction(
                    label="想吃飯！",
                    text="今天早餐想吃飯！"
                ),
                MessageTemplateAction(
                    label="想吃麵！",
                    text="今天早餐想吃麵！"
                ),

                MessageTemplateAction(
                    label="都可！（建議選項）",
                    text="今天早餐隨便吃！"
                )
                    
            ]
        )
    )
    return message

#飯麵2
def buttons_messagenrN():
    message = TemplateSendMessage(
        alt_text='想吃飯還是麵？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃飯/吃麵？",
            text="告訴我你目前的胃口吧！",
            actions=[

                MessageTemplateAction(
                    label="想吃飯！",
                    text="今天正餐想吃飯！"
                ),
                MessageTemplateAction(
                    label="想吃麵！",
                    text="今天正餐想吃麵！"
                ),

                MessageTemplateAction(
                    label="都可！（建議選項）",
                    text="今天正餐隨便吃！"
                )
                    
            ]
        )
    )
    return message


#飯麵3
def buttons_messagenrA():
    message = TemplateSendMessage(
        alt_text='想吃飯還是麵？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃飯/吃麵？",
            text="告訴我你目前的胃口吧！",
            actions=[

                MessageTemplateAction(
                    label="想吃飯！",
                    text="嘴饞想吃飯！"
                ),
                MessageTemplateAction(
                    label="想吃麵！",
                    text="嘴饞想吃麵！"
                ),

                MessageTemplateAction(
                    label="都可！（建議選項）",
                    text="嘴饞隨便吃！"
                )
                    
            ]
        )
    )
    return message




#風格1
def buttons_messageBRF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
             
                    data='早飯中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
                 
                    data='早飯日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
                  
                    data='早飯西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
                
                    data='早飯'
                )
            ]
        )
    )
    return message


#風格2
def buttons_messageBNF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
                 
                    data='早麵中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
         
                    data='早麵日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
              
                    data='早麵西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
              
                    data='早麵'
                )
            ]
        )
    )
    return message




#風格3
def buttons_messageBOF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
                   
                    data='早都可中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
                 
                    data='早都可日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
             
                    data='早都可西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
           
                    data='早都可'
                )
            ]
        )
    )
    return message






#風格4
def buttons_messageNRF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
           
                    data='正飯中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
             
                    data='正飯日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
            
                    data='正飯西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
           
                    data='正飯'
                )
            ]
        )
    )
    return message


#風格5
def buttons_messageNNF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
             
                    data='正麵中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
               
                    data='正麵日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
          
                    data='正麵西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
                
                    data='正麵'
                )
            ]
        )
    )
    return message



#風格6
def buttons_messageNOF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
             
                    data='正都可中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
        
                    data='正都可日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
            
                    data='正都可西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
             
                    data='正都可'
                )
            ]
        )
    )
    return message



#風格7
def buttons_messageARF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
        
                    data='消飯中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
             
                    data='消飯日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
              
                    data='消飯西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
                 
                    data='消飯'
                )
            ]
        )
    )
    return message



#風格8
def buttons_messageANF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
                
                    data='消麵中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
              
                    data='消麵日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
                 
                    data='消麵西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
               
                    data='消麵'
                )
            ]
        )
    )
    return message



#風格9
def buttons_messageAOF():
    message = TemplateSendMessage(
        alt_text='想吃哪種風格的料理呢？',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="想吃哪種風格的料理呢？",
            text="告訴我你的喜好吧！",
            actions=[

                PostbackTemplateAction(
                    label="中式料理！",
               
                    data='消都可中'
                ),
                PostbackTemplateAction(
                    label="日韓料理！",
            
                    data='消都可日'
                ),

                PostbackTemplateAction(
                    label="西式/東南亞！",
                 
                    data='消都可西'
                ),
                PostbackTemplateAction(
                    label="都可！(建議選項)",
                 
                    data='消都可'
                )
            ]
        )
    )
    return message







#TemplateSendMessage - ImageCarouselTemplate(圖片旋轉木馬)
def image_carousel_message1():
    message = TemplateSendMessage(
        alt_text='圖片旋轉木馬',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/uKYgfVs.jpg",
                    action=URITemplateAction(
                        label="新鮮水果",
                        uri="http://img.juimg.com/tuku/yulantu/110709/222-110F91G31375.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QOcAvjt.jpg",
                    action=URITemplateAction(
                        label="新鮮蔬菜",
                        uri="https://cdn.101mediaimage.com/img/file/1410464751urhp5.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛狗狗",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QRIa5Dz.jpg",
                    action=URITemplateAction(
                        label="可愛貓咪",
                        uri="https://m-miya.net/wp-content/uploads/2014/07/0-065-1.min_.jpg"
                    )
                )
            ]
        )
    )
    return message








import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
