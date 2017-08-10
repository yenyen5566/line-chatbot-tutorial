import requests
import re
import random
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from flask_bootstrap import Bootstrap
from flask_script import Server, Manager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
line_bot_api = LineBotApi('Channel Secret')
handler = WebhookHandler('Channel Access Token')
client_id = ''
client_secret = ''
album_id = ''
API_Get_Image ='API_Get_Image'


@app.route("/callback", methods=['POST']) 
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 200







def craw_page(res, push_rate):
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                rate = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate:
                    rate = 100 if rate.startswith('爆') else rate
                    rate = -1 * int(rate[1]) if rate.startswith('X') else rate
                else:
                    rate = 0
                # 比對推文數
                if int(rate) >= push_rate:
                    article_seq.append({
                        'title': title,
                        'url': url,
                        'rate': rate,
                    })
        except Exception as e:
            # print('crawPage function error:',r_ent.find(class_="title").text.strip())
            print('本文已被刪除', e)
    return article_seq

def get_page_number(content):
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1


def ptt_beauty():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page = get_page_number(all_page_url)
    page_term = 2  # crawler count
    push_rate = 10  # 推文
    index_list = []
    article_list = []
    for page in range(start_page, start_page - page_term, -1):
        page_url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page)
        index_list.append(page_url)

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)
        res = rs.get(index, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            index_list.append(index)
            # print u'error_URL:',index
            # time.sleep(1)
        else:
            article_list = craw_page(res, push_rate)
            # print u'OK_URL:', index
            # time.sleep(0.05)
    content = ''
    for article in article_list:
        data = '[{} push] {}\n{}\n\n'.format(article.get('rate', None), article.get('title', None),
                                             article.get('url', None))
        content += data
    return content

def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    count = 0
    for index, data in enumerate(soup.select('ul.filmNextListAll a')):
        if index == 10:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

def ptt_Rent_apart():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/Rent_apart/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/Rent_apart/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/Rent_apart/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n  https://www.ptt.cc/bbs/Rent_apart/index.html \n' + content


def ptt_Rent_ya():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/Rent_ya/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/Rent_ya/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/Rent_ya/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n  https://www.ptt.cc/bbs/Rent_ya/index.html \n' + content

def ptt_Rent_tao():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/Rent_tao/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/Rent_tao/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/Rent_tao/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.ptt.cc/bbs/Rent_tao/index.html \n' + content

def ptt_SpaceArt():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/SpaceArt/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/SpaceArt/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/SpaceArt/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.ptt.cc/bbs/SpaceArt/index.html \n' + content

def ptt_dailyarticle():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/dailyarticle/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/dailyarticle/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/dailyarticle/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.ptt.cc/bbs/dailyarticle/index.html \n' + content

def ptt_rent_exp():
    HOST = "https://www.ptt.cc"
    target_url = 'https://www.ptt.cc/bbs/rent-exp/index.html'
    rs = requests.session()
    res = rs.get(HOST + '/bbs/rent-exp/index.html' , verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    buttons = soup.select('a.btn.wide')
    total_page = int(buttons[1]['href'].split('index')[1].split('.html')[0]) + 1


    page_to_crawl = 1
    for page in range(total_page, total_page - page_to_crawl, -1):
        rs = requests.session()
        res = rs.get(HOST + "/bbs/rent-exp/index{}.html".format(page), verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        content = ""
        count = 0
        for data in soup.select('div.title a'):
            title = data.text
            link = "https://www.ptt.cc/bbs/" + data['href']
            if count < 8:
                count +=1
                content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.ptt.cc/bbs/rent-exp/index.html \n' + content

def mobile01_house_exp():
    target_url = 'https://www.mobile01.com/topiclist.php?f=400'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    count = 0
    for data in soup.select('span.subject-text a.topic_gen'):
        title = data.text
        link = 'https://www.mobile01.com/' + data['href']
        if count < 5:
            count +=1
            content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n  https://www.mobile01.com/topiclist.php?f=400 \n' + content

def mobile01_living_house():
    target_url = 'https://www.mobile01.com/topiclist.php?f=335'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    count = 0
    for data in soup.select('span.subject-text a.topic_gen'):
        title = data.text
        link = 'https://www.mobile01.com/' + data['href']
        if count < 5:
            count +=1
            content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.mobile01.com/topiclist.php?f=335 \n' + content

def rent_web():
    shop = ['591','太平洋網站','21世紀租屋網','中信租屋','樂屋網','永慶租屋網','好房網','好宅網','台灣租屋網','蟹居網','住商不動產租屋網','林媽媽租屋網']
    link = ['https://www.591.com.tw/home','http://www.pacific.com.tw/','http://www.century21.com.tw/index/','http://rent.cthouse.com.tw/Building/SearchList',
            'https://www.rakuya.com.tw/search/rent_search?gclid=CjwKEAjwtJzLBRC7z43vr63nr3wSJABjJDgJovoH1gu7iJ_B1Pbu5MfhvhRmcaheo_eBa1DVNCeE9RoCsmXw_wcB',
            'https://rent.yungching.com.tw/','https://www.housefun.com.tw/','http://www.home7-11.com.tw/lsearch.asp','http://www.twhouses.com.tw/',
            'https://rent.tmm.org.tw/','http://www.hbhousing.com.tw/rentHouse/','http://www.1478.com.tw/']
    loop = ""
    for i in range(0,11):
        loop += '{}\n{}\n'.format(shop[i], link[i])
     
    return loop

def google_news():
    target_url = 'https://www.google.com.tw/search?newwindow=1&safe=off&biw=1536&bih=760&tbm=nws&q=%E7%A7%9F%E5%B1%8B&oq=%E7%A7%9F%E5%B1%8B&gs_l=serp.3..0l10.3334.4564.0.5007.5.5.0.0.0.0.59.233.5.5.0....0...1.1j4.64.serp..0.4.195.0.Wq_mR1V-V8U'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    count = 0
    for data in soup.select('h3 a'):
        title = data.text
        link = data['href'].replace('/url?q=','')
        if count < 5:
            count +=1
            content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://www.google.com.tw/search?newwindow=1&safe=off&biw=1536&bih=760&tbm=nws&q=%E7%A7%9F%E5%B1%8B&oq=%E7%A7%9F%E5%B1%8B&gs_l=serp.3..0l10.3334.4564.0.5007.5.5.0.0.0.0.59.233.5.5.0....0...1.1j4.64.serp..0.4.195.0.Wq_mR1V-V8U \n' + content

def yahoo_news():
    target_url = 'https://tw.news.yahoo.com/search?p=%E7%A7%9F%E5%B1%8B&fr=uh3_news_vert_gs&fr2=p%3Anews%2Cm%3Asb'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    count = 0
    for data in soup.select('h3 a'):
        title = data.text
        link = data['href']
        if count < 5:
            count +=1
            content += '{}\n{}\n\n'.format(title, link)
    return '前往網站 \n https://tw.news.yahoo.com/search?p=%E7%A7%9F%E5%B1%8B&fr=uh3_news_vert_gs&fr2=p%3Anews%2Cm%3Asb \n ' + content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    if event.message.text == "google租屋相關新聞":
        content = google_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "Yahoo!租屋相關新聞":
        content = yahoo_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "PTT套房板":
        content = ptt_Rent_tao()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "PTT雅房板":
        content = ptt_Rent_ya()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "PTT公寓板":
        content = ptt_Rent_apart()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "PTT租屋板":
        content = ptt_rent_exp()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "PTT空間藝術板":
        content = ptt_SpaceArt()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "PTT生活智慧王板":
        content = ptt_dailyarticle()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "Moblie01居家房事消費經驗分享":
        content = mobile01_house_exp()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "Moblie01居家綜合":
        content = mobile01_living_house()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "近期上映電影":
        content = movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))

    if event.message.text == "PTT 表特版 近期大於 10 推的文章":
        content = ptt_beauty()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "來張 imgur 正妹圖片":
        client = ImgurClient(client_id, client_secret)
        images = client.get_album_images(album_id)
        index = random.randint(0, len(images) - 1)
        url = images[index].link.replace('http', 'https')
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0
    if event.message.text == "隨便來張正妹圖片":
        image = requests.get(API_Get_Image)
        url = image.json().get('Url')
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0

    if event.message.text == "各大租屋網站":
        content = rent_web()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "內政部-租屋資訊網":
        content = '內政部租屋網 \n https://houserent.cpami.gov.tw/'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "開始服務":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='選擇服務',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/ISSvMi5.jpg',
                actions=[
                    MessageTemplateAction(
                        label='新聞摘要',
                        text='新聞摘要'
                    ),
                    MessageTemplateAction(
                        label='PTT租屋相關板',
                        text='PTT租屋相關板'
                    ),
                    MessageTemplateAction(
                        label='生活分享',
                        text='生活分享'
                    ),
                    MessageTemplateAction(
                        label='輕鬆一下',
                        text='輕鬆一下'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    if event.message.text == "新聞摘要":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='新聞類型',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/gVVBQE9.jpg',
                actions=[
                    MessageTemplateAction(
                        label='google租屋相關新聞',
                        text='google租屋相關新聞'
                    ),
                    MessageTemplateAction(
                        label='Yahoo!租屋相關新聞',
                        text='Yahoo!租屋相關新聞'
                    )
                ] 
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    if event.message.text == "PTT租屋相關板":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='看板類型',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/ufSIEmt.jpg',
                actions=[
                    MessageTemplateAction(
                        label='PTT租屋板',
                        text='PTT租屋板'
                    ),
                    MessageTemplateAction(
                        label='PTT公寓板',
                        text='PTT公寓板'
                    ),
                    MessageTemplateAction(
                        label='PTT雅房板',
                        text='PTT雅房板'
                    ),
                    MessageTemplateAction(
                        label='PTT套房板',
                        text='PTT套房板'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    if event.message.text == "生活分享":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='看板類型',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/81FS8MV.jpg',
                actions=[
                    MessageTemplateAction(
                        label='Moblie01居家房事消費經驗分享',
                        text='Moblie01居家房事消費經驗分享'
                    ),
                    MessageTemplateAction(
                        label='Moblie01居家綜合',
                        text='Moblie01居家綜合'
                    ),
                    MessageTemplateAction(
                        label='PTT空間藝術板',
                        text='PTT空間藝術板'
                    ),
                    MessageTemplateAction(
                        label='PTT生活智慧王板',
                        text='PTT生活智慧王板'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    if event.message.text == "輕鬆一下":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='選擇服務',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/Gks0XGh.jpg',
                actions=[
                    MessageTemplateAction(
                        label='近期上映電影',
                        text='近期上映電影'
                    ),
                    MessageTemplateAction(
                        label='PTT 表特版 近期大於 10 推的文章',
                        text='PTT 表特版 近期大於 10 推的文章'
                    ),
                    MessageTemplateAction(
                        label='來張 imgur 正妹圖片',
                        text='來張 imgur 正妹圖片'
                    ),
                    MessageTemplateAction(
                        label='隨便來張正妹圖片',
                        text='隨便來張正妹圖片'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0

    if event.message.text == "開始使用" or event.message.text == "啾啾啾啾":
        buttons_template = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='選擇服務',
                text='請選擇',
                thumbnail_image_url='https://imgur.com/1rIntBo.jpg',
                actions=[
                    MessageTemplateAction(
                        label='開始服務',
                        text='開始服務'
                    ),
                    MessageTemplateAction(
                        label='BB101-G2專題網站',
                        text='10.120.37.16:8000'
                    ),
                    URITemplateAction(
                        label='聯絡我們',
                        uri='https://www.facebook.com/roadpigpig/'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0


if __name__ == '__main__':
    app.run()