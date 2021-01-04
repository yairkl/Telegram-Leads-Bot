#!/usr/bin/env python
"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import userKeys
import pandas as pd
import numpy as np
from database import database
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    KeyboardButton,
    Bot, replymarkup)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext)

first_massege = "שלום!"
second_message = "האם תהיה מעוניין לשתף איתנו את מספר הטלפון שלך ולקבל ממנו שיחה?"
interested = "מעוניין"
not_interested ="לא מעוניין"
semi_interested = "אשמח לשמוע עוד"
removeMessage = 'הוסרת מרשימת התפוצה.'
contactMessage = '.ניצור איתך קשר בהקדם'
moreInfo = 'ליותר פרטים על אודותינו את\ה מוזמן לפנות אל @finderela'
admin_message ='\n'.join([
    'ברוך הבא לממשק הניהול!',
    '/getLeads בכדי לקבל קובץ לידים',
    '/sendMessges על מנת לשלוח הודעות גיוס',
    '/cancel בכדי לבטל'
    ])
sendMessgesMessage = 'ישנם {num} משתמשים בבסיס הנתונים, שלח את מספר האנשים שהיית רוצה שיקבלו הודעה או קובץ המכיל רשימת אנשים'
messagesSentMessageFormat = '{num} הודעות נשלחו'
cancelMessage = 'בוטל'

replys = [[KeyboardButton(text=interested, request_contact=True),KeyboardButton(text=not_interested)]]

DB_NAME = 'users.db'
LEADS_TABLE = 'leads'
USERS_TABLE = 'users'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


NUMBER, CONTACT_US, NO_COMMENT, ADMIN , SEND_MESSAGES,ADD_USERS= range(6)

def sendMessage(userId,text):
    bot = Bot(token=userKeys.bot_token)
    bot.sendMessage(chat_id=userId,text=text)

def StartConversation(user_id,message):
    bot = Bot(token=userKeys.bot_token)
    db = database(DB_NAME)
    user =next(iter(db.selectWhere(USERS_TABLE,{'id':user_id})), {'checked':False}) 
    #TODO enable
    if not user['checked']:
        bot.sendMessage(chat_id=user_id,text=message)
        db.insertOrUpdate(USERS_TABLE,{'id':user_id,'checked':True})
    db.disconnect()


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = replys
    user = update.message.from_user
    update.message.reply_text(
        second_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return NUMBER

def number(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    contact = update.effective_message.contact
    #TODO INSERT CONTACT
    db = database(DB_NAME)
    db.insertOrUpdate(USERS_TABLE,{'id':user.id,'checked':True})
    db.insert(LEADS_TABLE,{'id':user.id,'phone':contact.phone_number,'interested':1})
    db.disconnect()

    logger.info("contact of %s: %s", user.first_name, contact)
    update.message.reply_text(
        contactMessage,
        reply_markup=ReplyKeyboardRemove(),
    )
    return CONTACT_US

def notInterested(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    #TODO CLASSIFY AS NOT INTERESTED
    db = database(DB_NAME)
    db.insertOrUpdate(USERS_TABLE,{'id':user.id,'checked':1})
    # db.update(USERS_TABLE,{'checked':1},{'id':user.id})
    db.insertOrUpdate(LEADS_TABLE,{'id':user.id,'interested':0})
    db.disconnect()

    update.message.reply_text(
        removeMessage,
        reply_markup=ReplyKeyboardRemove(),
    )
    return CONTACT_US

def contactUs(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        moreInfo,
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def admin(update: Update, context: CallbackContext) -> int:
    message = update.message.text if update.message.text else ""
    logger.info("Command %s", message)
    user = update.message.from_user
    if user.id in userKeys.admins:
        update.message.reply_text(admin_message,
            reply_markup=ReplyKeyboardRemove()
            )
        return ADMIN
    else:
        update.message.reply_text('Not permitted!')
        return ConversationHandler.END

def getLeads(update: Update, context: CallbackContext) -> int:
    db = database(DB_NAME)
    leads = pd.DataFrame(db.selectJoin(USERS_TABLE,LEADS_TABLE,('id','id')))
    leads.to_csv('leads.csv',encoding='utf-8')
    update.message.reply_document(document=open('leads.csv','rb'))
    db.disconnect()
    return ADMIN

def messages(update: Update, context: CallbackContext) -> int:
    db=database(DB_NAME)
    users = db.selectWhere(USERS_TABLE,{'checked':False})
    update.message.reply_text(sendMessgesMessage.format(num=len(users)))
    return SEND_MESSAGES

def sendMessages(update: Update, context: CallbackContext) -> int:
    limit = int(update.message.text if update.message.text else 0)
    if update.message.document:
        file = context.bot.getFile(update.message.document.file_id)
        file.download(update.message.document.file_name)
        users = pd.read_csv(update.message.document.file_name).to_dict(orient="records")
    else:
        db=database(DB_NAME)
        users = db.selectWhereLimit('users',{'checked':False},limit)
        db.disconnect()
    for i in users:
        StartConversation(i['id'],first_massege)
    update.message.reply_text(messagesSentMessageFormat.format(num=len(users)))
    return ADMIN


def addUsers(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'please send group url')
    return ADD_USERS

def addUsersFromUrl(update: Update, context: CallbackContext) -> int:
    message = update.message.text if update.message.text else ""
    sendMessage(userKeys.links_group,message)
    update.message.reply_text(f'users added!')
    return ADMIN

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        cancelMessage, reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(userKeys.bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin),MessageHandler(Filters.all, start)],
        states={
            NUMBER: [
                MessageHandler(Filters.regex(f'^{not_interested}$'), notInterested),
                MessageHandler(Filters.regex(f'^{semi_interested}$'), contactUs),
                MessageHandler(Filters.contact, number)],
            CONTACT_US: [MessageHandler(Filters.all, contactUs)],
            ADMIN:[
                CommandHandler('getLeads', getLeads),
                CommandHandler('sendMessges', messages),
            ],
            ADD_USERS:[
                MessageHandler(Filters.regex(f'^https://t.me/'), addUsersFromUrl),
            ],
            SEND_MESSAGES:[
                MessageHandler(Filters.regex(f'^[0-9]+$')|Filters.document,sendMessages),
            ],
            NO_COMMENT: [
                # MessageHandler(Filters.location, location),
                # CommandHandler('skip', skip_location),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel),CommandHandler('admin', admin)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    db = database(DB_NAME)
    db.disconnect()
    main()
