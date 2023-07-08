#-- coding: utf-8 --

import RPi.GPIO as GPIO #Importe la bibliotheque pour controler les GPIOs
from pirc522 import RFID
import time
import firebase_admin
from firebase_admin import credentials, messaging
import datetime

# FCM登録トークン
registration_token_0 = "" #ユーザ1のトークン
registration_token_1 = "" #ユーザ2のトークン

token_admin = registration_token_0 #管理者ユーザのトークン

# 各ユーザのID, 名前, トークン
# IDはタグに合わせて変える
idList = [[[136, 4, 96, 231, 11], "User 01", registration_token_0],
          [[136, 4, 96, 238, 2], "User 02", registration_token_1]]

# IDの照合を行う, インデックスを返す
def collation(idList, uid):
    for i, idi in enumerate(idList):
        if idi[0] == uid:
            return i

GPIO.setmode(GPIO.BOARD) #ピンのナンバリング方式の設定
GPIO.setwarnings(False)

rc522 = RFID() #インスタンス化

# サービスアカウントキーの読み込み
cred = credentials.Certificate("serviceAccuntKey.json")
# FirebaseAdminの初期化
firebase_admin.initialize_app(cred)

mode = int(input("モード選択 0 or 1 \n"))
print("--準備完了--")

while True :
    rc522.wait_for_tag() #認識範囲にタグがあるか確認
    (error, tag_type) = rc522.request() #タグ情報を取得(error:成功時に)
    if not error : #タグ認識時
        (error, uid) = rc522.anticoll() #衝突の排除
        if not error : #衝突排除時
            print("get ID : {}".format(uid))
            if True:
                index = collation(idList, uid) #照合
                if index != None:
                    name = idList[index][1]
                    dt_now = datetime.datetime.now()
                    title=""
                    body=""
                    token=""

                    if(mode == 0):
                        title="通過通知"
                        body=dt_now.strftime('%Y/%m/%d %H:%M:%S \n')+name
                        token=token_admin
                    elif(mode == 1):
                        title="通過通知"
                        body=dt_now.strftime('%Y/%m/%d %H:%M:%S \n')+"〇〇駅 : 改札を通過"
                        token=idList[index][2]
                    
                    message = messaging.Message( # メッセージの作成
                        notification=messaging.Notification(
                            title=title,
                            body=body,
                        ),
                        token=token,
                    )
                    response = messaging.send(message) # メッセージの送信
                    print("send to ", name)
            time.sleep(2) #連続読み取りの防止