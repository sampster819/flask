import os
from flask import Flask, request
from discord_webhook import DiscordWebhook, DiscordEmbed

app = Flask(__name__)

whitelisted_webhooks = {}

@app.route('/')
def home():
    return 'Protected webhook service is running!'

@app.route('/protect', methods=['POST'])
def protect():
    webhook_url = request.form.get('webhook_url')
    user_id = request.form.get('user_id')
    
    webhook = DiscordWebhook(url=webhook_url)
    response = webhook.execute()

    if 'id' in response:
        whitelisted_webhooks[webhook_url] = user_id
        protected_url = f"https://dismod.net/protectedwebhook/{webhook_url.split('/')[-2]}/{webhook_url.split('/')[-1]}"
        return protected_url
    else:
        return 'Invalid webhook URL'

@app.route('/<folder>/<filename>', methods=['POST'])
def handle_webhook(folder, filename):
    webhook_url = f"https://discord.com/api/webhooks/{folder}/{filename}"
    if webhook_url in whitelisted_webhooks:
        data = request.get_json()
        if data:
            message = data.get('content')
            if message:
                user_id = whitelisted_webhooks[webhook_url]
                username = data.get('username')
                avatar_url = data.get('avatar_url')
                embed = DiscordEmbed(description=message, color='blue')
                embed.set_author(name=username, icon_url=avatar_url)
                webhook = DiscordWebhook(url=webhook_url)
                webhook.add_embed(embed)
                webhook.execute()
        return ''
    else:
        return 'Invalid webhook URL'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
