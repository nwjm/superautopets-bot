import discord
import re
import string

class petFinder(discord.Client):

    file = open('keywords.txt')
    lines = file.read().split('\n')
    keywords = dict.fromkeys(lines)

    file = open('firstname.txt')
    lines = file.read().split('\n')
    firstnames = dict.fromkeys(lines)

    file = open('lastname.txt')
    lines = file.read().split('\n')
    lastnames = dict.fromkeys(lines)

    users_to_tag = set()

    role_message_id = 0
    emoji_to_role = {
        discord.PartialEmoji(name='👍'): True,
        discord.PartialEmoji(name='👎'): False
    }

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print(f"id is: {payload.message_id}")
        print(f"id should be: {self.role_message_id}")
        if payload.message_id != self.role_message_id:
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
            print(f"added {payload.user_id}")

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return
        if payload.user_id == self.user.id:
            return
        
        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return
        
        if role_id:
            self.users_to_tag.remove(payload.user_id)
            print(f"removed {payload.user_id}")




    async def on_ready(self):
        print(f'We have logged in as {self.user.id}')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        
        if message.content.startswith('!petfinder'):
            sent = await message.channel.send('React with :thumbsup: for Super Auto Pets notifications!')
            self.role_message_id = sent.id
            await sent.add_reaction(discord.PartialEmoji(name='👍'))
            print(f"id is: {self.role_message_id}")
            return
        
        contents = message.content.lower()
        contents = contents.translate(contents.maketrans('', '', string.punctuation))
        split = contents.split(' ')
        messageDict = dict.fromkeys(split)

        for word in self.keywords:
            if word in contents:
                regString = "^" + word + " | " + word + "$|." + word + " | " + word + ".|^" + word + "$"
                found = re.search(regString, contents)
                if found:
                    for user in self.users_to_tag:
                        await message.channel.send(f'Hey <@{user}>, looks like someone is playing Super Auto Pets!\nCheck out that '
                                                    + word.upper() + '!')
        
        for first in self.firstnames:
            if first in messageDict:
                for last in self.lastnames:
                    if last in messageDict:
                        regString = first + "." + last
                        print(regString)
                        found = re.search(regString, contents)
                        if (found):
                            for user in self.users_to_tag:
                                await message.channel.send (f'Hey <@{user}>, looks like someone is playing Super Auto Pets!\nCheck out those '
                                                            + first.capitalize() + ' ' + last.capitalize() + "!")   

client = petFinder()
client.run('OTI3Nzk0MzQ3OTYzOTg1OTUw.YdPZ0g.3KiX9XwXqH3QXkoUzPVkyfxgjNI')
