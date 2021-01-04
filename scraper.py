from telethon import TelegramClient
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest,GetParticipantsRequest,LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest,CheckChatInviteRequest
from telethon.tl.types import InputChannel
from telethon.tl.types import ChannelAdminLogEventsFilter,ChannelParticipantsSearch
from telethon.errors import *
from database import database
import asyncio
import re
import userKeys
import pandas as pd

class scraper:
    # client = TelegramClient('anon', userKeys.api_id, userKeys.api_hash)
    def __init__(self):
        if userKeys.proxy is None:
            self.client = TelegramClient('anon', userKeys.api_id, userKeys.api_hash)
        else:
            self.client = TelegramClient('anon', userKeys.api_id, userKeys.api_hash, proxy=userKeys.proxy)
        # self.client.start()
        self.db = database('users.db')
        self.db.createTable('users',{
            'id':'int unique',
            'username':'varchar(60)',
            'firstName':'varchar(60)',
            'lastName':'varchar(60)',
            'checked':'bit default 0'
            })

        # @self.client.on(events.NewMessage(pattern=r'https://t.me/'))
        async def onNewLink(event):
            if re.match(r'https://t.me/joinchat/',event.message.message) is not None:
                users = await self.getChatMembers(event.message.message.split('https://t.me/joinchat/').pop())
            else:
                users = await self.getChannelMembers(event.message.message.split('https://t.me/').pop())
            print(event.chat_id)
            await event.reply(f'Added: {len(users)}')
        
        @self.client.on(events.NewMessage(func=lambda e: e.chat_id in userKeys.admins))
        async def onAdminMessage(event):
            matches = re.findall(r'https://t.me/\w+/*\w*',event.message.message)
            print('admin message:',matches)
            users=[]
            for link in matches:
                if re.match(r'https://t.me/joinchat/',link) is not None:
                    users += await self.getChatMembers(link.split('https://t.me/joinchat/').pop())
                else:
                    print(link.split('https://t.me/').pop())
                    users += await self.getChannelMembers(link.split('https://t.me/').pop())
            pd.DataFrame(users).to_csv('usres.csv',encoding='utf-8')
            await event.reply(f'Added: {len(users)}',file=open('users.csv','rb'))


    def listen(self,time=-1):
        with self.client:
            self.client.loop.run_until_complete(self.waitOnEvent(time=time))


    async def joinChat(self,url):
        chat = url.split('/').pop()
        if chat==url:
            return False
        await self.client(ImportChatInviteRequest(chat))


    async def getChatMembers(self,chat):
        result = await self.client(CheckChatInviteRequest(chat))
        users = [{
                'id':usr.id,
                'username':usr.username,
                'firstName':usr.first_name,
                'lastName':usr.last_name
            } for usr in result.participants]
        self.db.insertIgnoreAll('users',users)
        return users

    async def getChannelMembers(self,channel):
        updates = await self.client(JoinChannelRequest(channel))
        input_channel = InputChannel(updates.chats[0].id, updates.chats[0].access_hash)
        users = []
        num = 0
        result = await self.client(GetParticipantsRequest(input_channel, ChannelParticipantsSearch(''), num, 100,hash=0))
        while len(result.users)!=0:
            users+=[{
                'id':user.id,
                'username':user.username,
                'firstName':user.first_name,
                'lastName':user.last_name
            } for user in result.users]
            # print('added:',len(result.users))
            num+=100
            result = await self.client(GetParticipantsRequest(input_channel, ChannelParticipantsSearch(''), num, 100,hash=0))
        self.db.insertIgnoreAll('users',users)
        await self.client(LeaveChannelRequest(channel=input_channel))
        return users


    async def waitOnEvent(self,time=-1):
        if time<0:
            while True:
                await asyncio.sleep(0.2)
        else:
            for i in range(time*5):
                await asyncio.sleep(0.2)


pass

if __name__=='__main__':
    s = scraper()
    s.listen()
    # with client:
    #     client.loop.run_until_complete(waitOnEvent())
    # #     client.loop.run_until_complete(getChannelMembers('Stocks_US'))
    # db = database('users.db')
    # db.disconnect()

