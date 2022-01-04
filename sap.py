import discord
import re
import string

client = discord.Client()

file = open('keywords.txt')
lines = file.read().split('\n')
keywords = dict.fromkeys(lines)

file = open('firstname.txt')
lines = file.read().split('\n')
firstnames = dict.fromkeys(lines)

file = open('lastname.txt')
lines = file.read().split('\n')
lastnames = dict.fromkeys(lines)

count = 0

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    contents = message.content.lower()
    contents = contents.translate(contents.maketrans('', '', string.punctuation))
    split = contents.split(' ')
    messageDict = dict.fromkeys(split)

    for word in keywords:
        if word in contents:
            regString = "^" + word + " | " + word + "$|." + word + " | " + word + ".|^" + word + "$"
            print(regString)
            found = re.search(regString, contents)
            if found:
                await message.channel.send(f'Hey <@{109464483914579968}>, looks like someone is playing Super Auto Pets!\nCheck out that '
                                            + word.upper() + '!')
    
    for first in firstnames:
        if first in messageDict:
            for last in lastnames:
                if last in messageDict:
                    regString = first + "." + last
                    print(regString)
                    found = re.search(regString, contents)
                    if (found):
                        await message.channel.send (f'Hey <@{109464483914579968}>, looks like someone is playing Super Auto Pets!\nCheck out those '
                                                    + first.capitalize() + ' ' + last.capitalize() + "!")   

client.run('OTI3Nzk0MzQ3OTYzOTg1OTUw.YdPZ0g.3KiX9XwXqH3QXkoUzPVkyfxgjNI')
