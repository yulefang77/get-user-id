import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# 加載 .env 文件中的環境變量
load_dotenv()

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

app = Flask(__name__)

configuration = Configuration(access_token=ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id

        if event.source.type == 'group':
            try:
                profile = line_bot_api.get_group_member_profile(event.source.group_id, user_id)
                user_name = profile.display_name
                user_text = "我是" + user_name + ", 我們在群組裡。"
                print(user_text)
            except Exception as e:
                print("Exception when calling MessagingApi->get_profile: %s\n" % e)
        else:
            try:
                profile = line_bot_api.get_profile(user_id)
                user_name = profile.display_name
                user_text = "我是" + user_name + ", 我不在群組裡。"
                print(user_text)
            except Exception as e:
                print("Exception when calling MessagingApi->get_profile: %s\n" % e)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=user_text)]
            )
        )


if __name__ == "__main__":
    app.run()
