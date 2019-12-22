from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    #credentials = ServiceAccountCredentials.from_json_keyfile_name('money-line-python-638e48c935e8.json', scope)
    #認証情報を環境変数から
    # 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している
    credential = {
                    "type": "service_account",
                    "project_id": os.environ['SHEET_PROJECT_ID'],
                    "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
                    "private_key": os.environ['SHEET_PRIVATE_KEY'],
                    "client_email": os.environ['SHEET_CLIENT_EMAIL'],
                    "client_id": os.environ['SHEET_CLIENT_ID'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
             }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
    
    gc = gspread.authorize(credentials)
    text = event.message.text
    #全角スペースを半角スペースに対応
    text = text.replace("　", " ")

    #項目、内容、金額に分ける
    genre = text.split(" ")[0]
    what = text.split(" ")[1]
    money = text.split(" ")[2]
    #日付について
    try:
        date = text.split(" ")[3]
        #dateから取得
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
    except:
        #現在の日付を取得
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month
        day = dt_now.day
        
    #ワークシートを開く
    year_month = str(year) + "/" + str(month)
    wks = gc.open('money_LINE_python').worksheet(year_month)

    #日付を検索
    day_name = str(day) + "日"

    cell = wks.find(day_name)
    row = cell.row
    col = cell.col

    #ジャンルごとに値を更新
    if genre=="交通費":
        #詳細
        cell_value_what = wks.cell(row+2, col).value
        #金額
        cell_value_money = wks.cell(row+2, col+1).value

        wks.update_cell(row+2, col, cell_value_what+"\n"+what)
        wks.update_cell(row+2, col+1, cell_value_money+"\n"+money) 
        
        #金額の合計
        cell_money = wks.cell(row+2, col+1).value
        wks.update_cell(row+2, col+2, sum([int(i) for i in cell_money.splitlines()]))
        
    elif genre=="食事":
        #詳細
        cell_value_what = wks.cell(row+3, col).value
        #金額
        cell_value_money = wks.cell(row+3, col+1).value

        wks.update_cell(row+3, col, cell_value_what+"\n"+what)
        wks.update_cell(row+3, col+1, cell_value_money+"\n"+money) 
        
        #金額の合計
        cell_money = wks.cell(row+3, col+1).value
        wks.update_cell(row+3, col+2, sum([int(i) for i in cell_money.splitlines()]))
        
    elif genre=="おかし":
        #詳細
        cell_value_what = wks.cell(row+4, col).value
        #金額
        cell_value_money = wks.cell(row+4, col+1).value

        wks.update_cell(row+4, col, cell_value_what+"\n"+what)
        wks.update_cell(row+4, col+1, cell_value_money+"\n"+money) 
        
        #金額の合計
        cell_money = wks.cell(row+4, col+1).value
        wks.update_cell(row+4, col+2, sum([int(i) for i in cell_money.splitlines()]))
        
    elif genre=="趣味":
        #詳細
        cell_value_what = wks.cell(row+5, col).value
        #金額
        cell_value_money = wks.cell(row+5, col+1).value

        wks.update_cell(row+5, col, cell_value_what+"\n"+what)
        wks.update_cell(row+5, col+1, cell_value_money+"\n"+money) 
        
        #金額の合計
        cell_money = wks.cell(row+5, col+1).value
        wks.update_cell(row+5, col+2, sum([int(i) for i in cell_money.splitlines()]))

    elif genre=="その他":
        #詳細
        cell_value_what = wks.cell(row+6, col).value
        #金額
        cell_value_money = wks.cell(row+6, col+1).value

        wks.update_cell(row+6, col, cell_value_what+"\n"+what)
        wks.update_cell(row+6, col+1, cell_value_money+"\n"+money) 
        
        #金額の合計
        cell_money = wks.cell(row+6, col+1).value
        wks.update_cell(row+6, col+2, sum([int(i) for i in cell_money.splitlines()]))

    #書き込みが終了したら、LINEで返す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='書き込んだよ！')
    )

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)