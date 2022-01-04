import discord
import re
import string
import os.path

from discord.errors import NotFound

def writeListToFile(filename, list):
    file = open(filename, 'w')
    for item in list:
        file.write(str(item))
        file.write('\n')
    file.close()

def writeDictToFile(filename, d):
    file = open(filename, 'w')
    print('writing to ', filename)
    for key in d:
        buffer = str(key) + "," + str(d[key])
        file.write(buffer)
        file.write('\n')
    file.close()

def writeDictListToFile(filename, d):
    file = open(filename, 'w')
    print('writing to ', filename)
    for key in d:
        buffer = str(key)
        for value in d[key]:
            buffer += "," + str(value)
        file.write(buffer)
        file.write('\n')
    file.close()

def createDictFromFile(filename, d):
    if os.path.exists(filename):
        print(filename +  " exists")
        file = open(filename)
        lines = file.read().split('\n')
        for line in lines:
            if line:
                pair = line.split(',')
                if len(pair) == 2:
                    d[int(pair[0])] = int(pair[1])
        file.close()

def createDictListFromFile(filename, d):
    if os.path.exists(filename):
        print(filename + " exists")
        file = open(filename)
        lines = file.read().split('\n')
        for line in lines:
            if line:
                list = line.split(',')
                if len(list) > 1:
                    key = int(list[0])
                    values = d.get(key, [])
                    for i, value in enumerate(list):
                        if i == 0: continue
                        values.append(int(value))
                    d[key] = values
        file.close()

def appendDictToFile(filename, key, value):
    file = open(filename, 'a')
    buffer = str(key) + ',' + str(value) + '\n'
    file.write(buffer)
    file.close()
    



class petFinder(discord.Client):
    file = open('keywords.txt')
    lines = file.read().split('\n')
    keywords = dict.fromkeys(lines)
    file.close()

    file = open('firstname.txt')
    lines = file.read().split('\n')
    firstnames = dict.fromkeys(lines)
    file.close()

    file = open('lastname.txt')
    lines = file.read().split('\n')
    lastnames = dict.fromkeys(lines)
    file.close()

    users_to_tag = set()
    if os.path.exists('users.txt'):
        print("users.txt exists")
        file = open('users.txt')
        lines = file.read().split('\n')
        for line in lines:
            if line:
                users_to_tag.add(int(line))
        file.close()

    # await channel.history().find(lambda m: m.author.id == users_id) 



    role_message_id = {}
    createDictFromFile('signup.txt', role_message_id)

    oldCommandMessages = {}
    createDictListFromFile('oldcommands.txt', oldCommandMessages)

    

    emoji_to_role = {
        discord.PartialEmoji(name='👍'): True,
        discord.PartialEmoji(name='👎'): False
    }

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id.get(payload.channel_id, 0):
            return
        if payload.user_id == self.user.id:
            return
        print("checking reactions")
        
        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return
        
        if role_id:
            self.users_to_tag.add(payload.user_id)
            file = open('users.txt', 'a')
            file.write(str(payload.user_id))
            file.write('\n')
            file.close()
            print(f"added {payload.user_id}")

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id.get(payload.channel_id, 0):
            return
        if payload.user_id == self.user.id:
            return
        
        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return
        
        if role_id:
            self.users_to_tag.remove(payload.user_id)
            file = open('users.txt', 'w')
            for user in self.users_to_tag:
                file.write(str(user))
                file.write('\n')
            file.close()
            print(f"removed {payload.user_id}")




    async def on_ready(self):
        print(f'We have logged in as {self.user.id}')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        
        if message.content.startswith('!petfinder'):
            # Delete old commands in this channel
            oldCommandList = self.oldCommandMessages.get(message.channel.id, [])
            for message_id in oldCommandList:
                print("id", message_id)
                try:
                    oldmessage = await message.channel.fetch_message(message_id)
                    await oldmessage.delete()
                except NotFound:
                    print(f"message {message_id} not found")
                    

            # Add to list of old command messages
            self.oldCommandMessages[message.channel.id] = [message.id]
            writeDictListToFile('oldcommands.txt', self.oldCommandMessages)

            # Fetch old reaction message from this channel
            if message.channel.id in self.role_message_id:
                try:
                    oldmessage = await message.channel.fetch_message(self.role_message_id[message.channel.id])
                    await oldmessage.delete()
                except NotFound:
                    print(f'message {message.channel.id} not found')

            sent = await message.channel.send('React with :thumbsup: for Super Auto Pets notifications!')
            await sent.add_reaction(discord.PartialEmoji(name='👍'))
            
            #Store key-value pair
            self.role_message_id[message.channel.id] = sent.id
            print('trying to write to file')
            writeDictToFile('signup.txt', self.role_message_id)
            return
        
        contents = message.content.lower()
        contents = contents.translate(contents.maketrans('', '', string.punctuation))
        split = contents.split(' ')
        messageDict = dict.fromkeys(split)

        for word in self.keywords:
            if word in contents:
                regString = "^" + word + " | " + word + "$| " + word + "|^" + word + "$"
                found = re.search(regString, contents)
                if found:
                    mymessage = 'Hey '
                    usercount = 0
                    for user in self.users_to_tag:
                        if not user: continue
                        usercount += 1
                        mymessage += f'<@{user}>, '
                        mymessage += 'looks like someone is playing Super Auto Pets!\n'
                        if word != 'super':
                            mymessage += 'Check out that ' + word.upper() + '!'
                    
                    if usercount > 0:
                        await message.channel.send(mymessage)
        
        for first in self.firstnames:
            if first in messageDict:
                for last in self.lastnames:
                    if last in messageDict:
                        regString = first + "." + last
                        print(regString)
                        found = re.search(regString, contents)
                        if (found):
                            for user in self.users_to_tag:
                                if not user: continue
                                await message.channel.send (f'Hey <@{user}>, looks like someone is playing Super Auto Pets!\nCheck out those '
                                                            + first.capitalize() + ' ' + last.capitalize() + "!")   

client = petFinder()
client.run('OTI3Nzk0MzQ3OTYzOTg1OTUw.YdPZ0g.3KiX9XwXqH3QXkoUzPVkyfxgjNI')
