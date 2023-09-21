import asyncio
import os
import re

import discord
from PIL import Image

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

client = discord.Client(intents=intents)

pausedPings = []
q=[]
xcoord = 0
ycoord = 0
planet = ''

@client.event
async def on_ready():
  print('The bot is ready')
  taskQueue = asyncio.create_task(message_queue())
  await taskQueue

#timer to remove base from timeout
async def pause_timer(message):
  global pausedPings
  await asyncio.sleep(600)
  for i in pausedPings:
    pMessage = i
    if pMessage.content == message.content:
      pausedPings.remove(i)
      print('removed pause on message')

#repeating timer to dequeue messages
async def message_queue():
  global q
  while True:
    if len(q) > 0:
      msg = q.pop(0)
      await handle_message(msg)
    await asyncio.sleep(5)

#take one message passed from dequeue method and create map and format text for waypoint.
async def handle_message(message):
  msg = message.content
  #Rebel base attacked
  if 'Rebel base' in message.content and 'is under attack' in message.content:
    reaction_emoji = discord.utils.get(message.guild.emojis, name='empire')
    await message.add_reaction(reaction_emoji)
    await message.reply(
        '<@&1090033169782296627> Imperial troops have entered the base!')
    mess = await editWaypoint(msg)
    await message.channel.send(mess)
    await editImg(msg)
    await message.channel.send(file=discord.File('pasted_picture.png'))
  #Rebel turrets attacked
  elif 'Rebel base' in message.content and 'turrets' in message.content:
    reaction_emoji = discord.utils.get(message.guild.emojis, name='empire')
    await message.add_reaction(reaction_emoji)
    await message.reply('<@&1090033169782296627> Our turrets are taking fire!')
    mess = await editWaypoint(msg)
    await message.channel.send(mess)
    await editImg(msg)
    await message.channel.send(file=discord.File('pasted_picture.png'))
  #Imperial turrets attacked
  elif 'Imperial base' in message.content and 'turrets' in message.content:
    reaction_emoji = discord.utils.get(message.guild.emojis, name='reb')
    await message.add_reaction(reaction_emoji)
    mess = await editWaypoint(msg)
    await message.channel.send(mess)
    await editImg(msg)
    await message.channel.send(file=discord.File('pasted_picture.png'))
  #Imperial base attacked
  elif 'Imperial base' in message.content and 'is under attack' in message.content:
    reaction_emoji = discord.utils.get(message.guild.emojis, name='reb')
    await message.add_reaction(reaction_emoji)
    await message.reply(
        'Our forces have begun an assault on an Imperial base.')
    mess = await editWaypoint(msg)
    await message.channel.send(mess)
    await editImg(msg)
    await message.channel.send(file=discord.File('pasted_picture.png'))

  if 'testpost' in message.content:
    #reaction_emoji = discord.utils.get(message.guild.emojis, name='reb')
    #await message.add_reaction(reaction_emoji)
    filelist = [
      discord.File("pasted_picture.png"),
      discord.File("Tatooine.png"),
      discord.File("Naboo.png")
    ]
    await message.channel.send(files = filelist)

#event for incoming messages
#checks channel id and content for keywords for attacks
@client.event
async def on_message(message):
  global rebBaseTime, rebTurretTime, impBaseTime, impTurretTime, q, pausedPings
  msg = message.content

  if message.channel.id in [
      1149773441956851713, 1127862884618211328, 1152231778342408223
  ]:
    #if any keyboards present, queue message
    if 'base' in message.content and 'attack' in message.content:
      newMessage = True
      for i in pausedPings:
        pMessage = i
        pContent = pMessage.content
        if message.content == pContent:
          newMessage = False
          print('repeat message found. Discarded')
          break

      if newMessage == True:  
        q.append(message) #dd message to queue
        pausedPings.append(message)
        await pause_timer(message)

#take the GCW text and place waypoint on correct map image
async def editImg(message):
  global xcoord, ycoord
  if 'Tatooine' in message:
    img = Image.open("Tatooine.png")
  elif 'Lok' in message:
    img = Image.open("Lok.png")
  elif 'Naboo' in message:
    img = Image.open("Naboo.png")
  elif 'Rori' in message:
    img = Image.open("Rori.png")
  elif 'Corellia' in message:
    img = Image.open("Corellia.png")
  elif 'Talus' in message:
    img = Image.open("Talus.png")
  elif 'Dantooine' in message:
    img = Image.open("Dantooine.png")
  planetUVx = 0
  planetUVy = 0

  if xcoord < 0:
    planetUVx = 8200 + xcoord
  elif xcoord >= 0:
    planetUVx = 16400 - (8200 - xcoord)

  if ycoord < 0:
    planetUVy = 8200 + ycoord
  elif ycoord >= 0:
    planetUVy = 16400 - (8200 - ycoord)

  markerx = int((planetUVx / 16400) * 380)
  markery = int((planetUVy / 16400) * 340)
  markery = 340 - markery

  #Relative Path
  #Image which we want to paste
  img2 = Image.open("MapIcon.png")
  img.paste(img2, (markerx, markery), img2)

  #Saved in the same relative location
  img.save("pasted_picture.png")

  return

#format GCW text from RESTO into /waypoint that can be pasted in game
async def editWaypoint(msg):
  global xcoord, ycoord
  mess = msg
  if 'Tatooine' in msg:
    mess = re.sub(r'^.*?[(]', '/way tatooine (', msg)
  elif 'Dantooine' in msg:
    mess = re.sub(r'^.*?[(]', '/way dantooine (', msg)
  elif 'Naboo' in msg:
    mess = re.sub(r'^.*?[(]', '/way naboo (', msg)
  elif 'Talus' in msg:
    mess = re.sub(r'^.*?[(]', '/way talus (', msg)
  elif 'Corellia' in msg:
    mess = re.sub(r'^.*?[(]', '/way corellia (', msg)
  elif 'Rori' in msg:
    mess = re.sub(r'^.*?[(]', '/way rori (', msg)
  elif 'Lok' in msg:
    mess = re.sub(r'^.*?[(]', '/way lok (', msg)
  mess = re.sub('[)]', '', mess)
  index0 = mess.index('(', 0)
  index0 += 1
  index1 = mess.index(',', 0)
  index11 = index1
  index11 += 2
  index2 = mess.rindex('.')
  index3 = mess.index(',', index11, index2)
  index3 += 1
  xstr = mess[index0:index1]
  ystr = mess[index3:]
  ystr = ystr.rstrip('.')
  xcoord = int(float(xstr))
  ycoord = int(float(ystr))

  mess = mess[:index11] + mess[index3:]
  mess = mess.rstrip('.')
  mess = re.sub('[(,]', '', mess)

  return mess
#bot responds to 'Separatist' emoji reactions and posts a map to the base location of the message reacted to
@client.event
async def on_raw_reaction_add(payload):
  #get channel and message content
  channelID = payload.channel_id
  messageID = payload.message_id
  user_id = payload.user_id
  
  channel = client.get_channel(channelID)
  message = await channel.fetch_message(messageID)
  msg= message.content

  if channelID in [
      1149773441956851713, 1127862884618211328, 1152231778342408223
  ]:
    if 'base' in msg.lower() and '(' in msg: #GCW message containing base info and waypoint
      if payload.emoji.name == 'separatist': #correct reaction emoji
        mess = await editWaypoint(msg)       #format to /waypoint yada yada
        await channel.send(mess)
        await editImg(msg)                   #add the waypoint to the correct map image
        await channel.send(file=discord.File('pasted_picture.png'))

client.run(TOKEN)