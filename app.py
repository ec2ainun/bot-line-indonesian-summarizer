import re
import urllib
from bs4 import BeautifulSoup
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()
import numpy as np
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from listBerita import listBerita
from rangkum import Berita
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = "CHANNEL_SECRET"
channel_access_token = "CHANNEL_ACCESS_TOKEN"


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


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

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type + '\nHi, i\'m zumi. your personal Indonesian summarizer assistant \nwhat can i do? \n - untukmu yang malas baca berita, aku bisa meringkas sampai 1/2 dari keseluruhan kalimat berita yang ada \n - untukmu yang hemat kuota, kamu cuma perlu ngasih perintah aku dan tidak perlu mendownload informasi yang tidak penting seperti file-file web ataupun IKLAN wkwk \n - aku menyediakan 4 berita yang kamu suka, jika menurutmu tidak sesuai yang kamu inginkan, aku akan mengambilkan 4 berita terbaru lain untukmu \n\n\nPerintah \'bantu\' untuk mengetahui list command yang ada '))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    if "kompas.com/read" in event.postback.data:
        linkBerita = Berita(event.postback.data)
        rangkuman = linkBerita.rangkumanBerita()
        teks = ' '.join(rangkuman)
        if(len(teks)>1):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=teks))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="maaf, karena beberapa hal, aku nggak bisa meringkas berita tersebut"))
        

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    text = event.message.text
    acak = np.arange(14)
    np.random.shuffle(acak)
    if text == 'K':
        buttons_template = ButtonsTemplate(
             text='Daftar Kategori Berita', actions=[
                MessageTemplateAction(label='Tekno', text='tekno'),
                MessageTemplateAction(label='Bisnis', text='bisnis'),
                MessageTemplateAction(label='Otomotif', text='otomotif'),
                MessageTemplateAction(label='Bantuan', text='bantu') 
            ])
        template_message = TemplateSendMessage(
            alt_text='Daftar Kategori', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'bye zumi' or text == 'Bye zumi':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text='Meninggalkan group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text='Meninggalkan group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Aku nggak bisa meninggalkanmu :P"))
    elif text == 'tekno':
        databerita = listBerita("http://tekno.kompas.com/business")
        daftarberita = databerita.daftarBerita()    
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text=daftarberita[acak[0]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[0]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[0]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[1]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[1]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[1]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[2]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[2]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[2]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[3]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[3]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[3]]['link'])
            ])
        ])
        template_message = TemplateSendMessage(
            alt_text='Daftar Berita Tekno', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'bisnis':
        databerita = listBerita("http://bisniskeuangan.kompas.com/bisnis")
        daftarberita = databerita.daftarBerita()
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text=daftarberita[acak[0]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[0]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[0]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[1]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[1]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[1]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[2]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[2]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[2]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[3]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[3]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[3]]['link'])
            ])
        ])
        template_message = TemplateSendMessage(
            alt_text='Daftar Berita Bisnis', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'otomotif':
        databerita = listBerita("http://otomotif.kompas.com/news")
        daftarberita = databerita.daftarBerita()
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text=daftarberita[acak[0]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[0]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[0]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[1]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[1]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[1]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[2]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[2]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[2]]['link'])
            ]),
            CarouselColumn(text=daftarberita[acak[3]]['judul'],  actions=[
                PostbackTemplateAction(label="Ringkas", data=daftarberita[acak[3]]['link'], text='ringkas'),
                URITemplateAction(label='Baca berita asli', uri=daftarberita[acak[3]]['link'])
            ])
        ])
        template_message = TemplateSendMessage(
            alt_text='Daftar Berita Otomotif', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif "kompas.com/read" in text :
        linkBerita = Berita(text)
        rangkuman = linkBerita.rangkumanBerita()
        teks = ' '.join(rangkuman)
        if(len(teks)>2):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=teks))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="maaf, link yang anda kirim tidak valid "))
    elif text == 'Bantu' or text == 'bantu':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='\'K\' >> untuk list Kategori \n\'Bantu\' >> list command yang ada \n\'Bye zumi\' >> mengusirku dari group \n\'Ping\' >> ngecek aku masih hidup ato nggak :P'))
    elif text == 'ringkas':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Meringkas...'))

    elif text == 'Ping' or text == 'ping':
        buttons_template = ButtonsTemplate(
             text='Ping aku', actions=[
                PostbackTemplateAction(label='ping', data='ping')    
            ])
        template_message = TemplateSendMessage(
            alt_text='ping', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    else:
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Hi "+profile.display_name+"\n"+event.message.text+" :P"))
    '''
    profile = line_bot_api.get_profile(event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hi mastah "+profile.display_name+"\n"+event.message.text+" :P")
    )'''
    

if __name__ == "__main__":
    app.run()
