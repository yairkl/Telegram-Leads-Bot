from telegram.ext import Updater, CommandHandler,CallbackQueryHandler,MessageHandler,Filters
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup,ReplyKeyboardRemove,Bot
import requests
import re
import logging
import userKeys
import numpy as np
class LeadBot:
    conversation = {
        'start':{
            'text':'hello!',
            'replays':{
                'number':{
                    'button':KeyboardButton(text="contact", request_contact=True),
                    'callback':lambda bot,update:print('NUMBER WAS GIVEN')
                },
                'remove':{
                    'button':KeyboardButton(text="remove"),
                    'callback':lambda bot,update:print('REMOVE WAS CLICKED')
                }
            }
        },
        'contact':{
            'text':'thenks!',
            'replays':{},
            'reply_markup':ReplyKeyboardRemove()
        },
        'remove':{
            'text':'goodbye!',
            'replays':{
                'restart':{
                    'button':KeyboardButton(text="/start"),
                    'callback':lambda bot,update:print('REMOVE WAS CLICKED')
                }
            }
        }
    }


    def __init__(self):
        # logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.updater = Updater(userKeys.bot_token)
        self.dp = self.updater.dispatcher
        self.bot = Bot(token=userKeys.bot_token)
        self.dp.add_handler(CommandHandler('start',lambda bot,update,code='start':self.handleRequest(bot,update,code)))
        self.dp.add_handler(MessageHandler(Filters.all,self.handleRequest))
            
        # self.dp.add_handler(CommandHandler('start',self.requestNumber))
        # self.dp.add_handler(MessageHandler(Filters.contact, self.contact_callback))
        # self.dp.add_handler(MessageHandler(Filters.all,self.remove_callback))

        # self.dp.add_handler(CallbackQueryHandler(self.buttonPressed))
        # con_keyboard = [[InlineKeyboardButton(text="שתף מספר", request_contact=True),KeyboardButton(text="הסר")]]
        # reply_markup = ReplyKeyboardMarkup(con_keyboard)
        # bot.sendMessage(chat_id=88439707,text="האם תהיה מעוניין לשתף איתנו את מספר הטלפון שלך ולקבל ממנו שיחה?", reply_markup=reply_markup)

        self.updater.start_polling()
        self.updater.idle()
    
    def handleRequest(self,bot,update,code=None):
        text = update.message.text if update.message.text else ""
        contact = update.message.contact
        chatId = update.message.chat.id
        if chatId in userKeys.admins:
            #TODO handle admin request
            pass
        elif contact:
            #TODO handle contact recieved
            context = self.conversation.get('contact')
            reply_markup = context.get('reply_markup',ReplyKeyboardMarkup([[v.get('button') for k,v in context.get('replays',{}).items()]],one_time_keyboard=True))
            update.message.reply_text(context.get('text',''),reply_markup=reply_markup)
            print(update.message.contact)
        elif re.match(r'^/',text):
            print('command:',text)
            if text=='/start':
                context = self.conversation.get(code)
                reply_markup = context.get('reply_markup',ReplyKeyboardMarkup([[v.get('button') for k,v in context.get('replays',{}).items()]],one_time_keyboard=True))
                update.message.reply_text(context.get('text',''),reply_markup=reply_markup,)
            
            #todo handle command                
                
        else:
            context = self.conversation.get(text)
            buttons = np.array([v.get('button') for k,v in context.get('replays',{}).items()])
            if len(buttons)>3:
                
                buttons = buttons.reshape(3,-1)
                print(buttons.shape)
            else:
                buttons = buttons.reshape(1,len(buttons))
            reply_markup = context.get('reply_markup',ReplyKeyboardMarkup(buttons,one_time_keyboard=True))
            update.message.reply_text(context.get('text',''),reply_markup=reply_markup)

            pass

    def addConversationNode(self,id,message,options):
        con_keyboard = [[InlineKeyboardButton(text="שתף מספר"),KeyboardButton(text="הסר")]]
        reply_markup = InlineKeyboardMarkup(con_keyboard)

        # self.conversation[id] = 

    def sendMessage(self,chatId,text,reply_markup):
        self.bot.sendMessage(chat_id=chatId,text=text,reply_markup=reply_markup)

    pass

if __name__=='__main__':
    lb = LeadBot()
