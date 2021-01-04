# Telegram-Leads-Bot
Before working with Telegram’s API, you need to get your own API ID and hash:

1. [Login to your Telegram account](https://my.telegram.org/) with the phone number of the developer account to use.
Click under API Development tools.
2. A Create new application window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.
3. Enter your api id and hash into your userKeys.py file
4. Click on Create application at the end. Remember that your API hash is secret and Telegram won’t let you revoke it. Don’t post it anywhere!
5. [Create new Telegram bot](https://core.telegram.org/bots) and copy its token to userKeys.py file
6. add your user id to the admins list so you can control the bot
7. create new group and add your telegram user to it, set the links_group field in userKeys.py to be this group id

you are ready to go!, now run both scraper.py and ConversationBot.py
