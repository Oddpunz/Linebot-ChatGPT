from openai import OpenAI
import os , requests
import base64
import hashlib
import hmac
from flask import Flask, request, abort

access_token = os.environ.get('CHANNEL_ACCESS_TOKEN')
channel_secret = os.environ.get('CHANNEL_SECRET')
chatgpt_secret = os.environ.get('CHATGPT_SECRET')

app = Flask(__name__)

def handler(event):
    if(event['type']!="message"):
        reply("尚不支持文字以外的輸入", event['replyToken'])
    else:
        reply(ChatGPT(event['message']['text']), event['replyToken']) 

@app.route('/', methods=['GET', 'POST'])
def main(Request):
    if request.method == 'GET':
        # 取得GET請求的參數
        parameters = request.args
        if parameters:
            return f"Received GET request with parameters: {parameters}"
        else:
            return "Received GET request without parameters"
    elif request.method == 'POST':
        body = request.get_json()
        event = body['events'][0]
        handler(event)
        
        Signature = request.headers.get('x-line-signature')
        body = request.data
        if (signature(body)!=Signature):
            return "401"   
        return "OK"

def signature(Request):
    # Compare x-line-signature request header and the signature
    body = Request.decode('utf-8')
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(hash)
    
def ChatGPT(Message):
    Client = OpenAI(api_key=chatgpt_secret)
    try:
        completion = Client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你的主人叫做施博剴，而你是個默認使用繁體中文的有趣助理，偶爾會對使用者開玩笑。"},
                {"role": "user", "content": Message}
            ]
        )
        return completion.choices[0].message.content
    except Exception:
        return "或許博剴的chatGPT沒有餘額了!!" 

def reply(message_text, reply_token):
    api_url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    res = requests.post(api_url, headers=headers, json=data)
