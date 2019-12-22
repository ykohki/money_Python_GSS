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

    credentials = ServiceAccountCredentials.from_json_keyfile_name('money-line-python-638e48c935e8.json', scope)
    gc = gspread.authorize(credentials)
    text = event.message.text

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