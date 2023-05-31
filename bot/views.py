from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import requests


from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def getLottery():

    try:
        url = "https://www.taiwanlottery.com.tw/lotto/lotto649/history.aspx"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        trs = soup.find("table", class_="table_org td_hm").find_all("tr")
        columns = [td.text.strip() for td in trs[0].find_all("td")]
        datas = [td.text.strip() for td in trs[1].find_all("td")]
        numbers = [td.text.strip() for td in trs[4].find_all("td")]

        info = ""
        for i in range(len(columns)):
            info += f"{columns[i]}:{datas[i]}\n"
        info += ",".join(numbers[1:-1]) + f"  特別號：{numbers[-1]}"

        return info

    except Exception as e:
        return "中獎號碼查找失敗,請稍候再試！"


def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parse.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event, MessageEvent):
                text = event.message.text
                message = None
                print(text)

                if text == "1":
                    message = "早安！"
                elif text == "2":
                    message = "晚安！"
                elif "早安" in text:
                    message = "你好啊,早安！"
                elif "樂透" in text:
                    message = getLottery
                elif "台北捷運" in text:
                    image_url = "https://web.metro.taipei/pages/assets/images/routemap2023n.png"
                elif "高雄捷運" in text:
                    image_url = "https://khh.travel/content/images/static/kmrt-map-l.jpg"
                else:
                    message = "很抱歉, 我不知道你在說什麼, 請再重複一次 ！"

                if message is None:
                    message_obj = ImageSendMessage(image_url, image_url)
                else:
                    message_obj = TextSendMessage(text=message)

                line_bot_api.reply_message(event.reply_token, message_obj)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def index(request):
    return HttpResponse("<h1>Line Bot !</h1>")


def lottery(request):
    text = getLottery().replace("\n", "<br>")
    return HttpResponse(f"<h1>{text}</h1>")
