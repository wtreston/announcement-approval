import discord
import json

# LOAD CONFIG
def load_config():
    name = 'config.json'
    with open(name, 'r') as config:
        json_ = json.load(config)
        return str(json_['secret_key']), int(json_['submit_channel']), int(json_['staff_channel']), int(json_['public_channel']), json_['role']

SECRET_KEY, SUBMIT_CHANNEL, STAFF_CHANNEL, PUBLIC_CHANNEL, ROLE = load_config()

client = discord.Client()

# CONFIRM LOGIN SUCCESS
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# SEND MESSAGE TO APPROPRIATE CHANNEL
async def send_to_channel(m, channel, add):
    message_content = m.content
    channel = client.get_channel(channel)
    if m.attachments:
        for attachment in m.attachments:
            message_content += '\n' + attachment.url
    if add:
        author_id = '<@' + str(m.author.id) + '>'
        message_content += '\nPosted by: {}'.format(author_id)
    await channel.send(message_content)

# MONITOR MESSAGES
@client.event
async def on_message(m):
    author = m.author   
    channel = m.channel
    channel_id = channel.id

    if not author.bot:
        if channel_id == SUBMIT_CHANNEL:
            if ROLE in [role.name.lower() for role in author.roles]:
                await send_to_channel(m, PUBLIC_CHANNEL, True)
                await m.delete()
                await m.author.send("Message has been sent to the announcement channel.")
            else:
                await send_to_channel(m, STAFF_CHANNEL, True)
                await m.delete()
                await m.author.send("Message has been sent to the staff team for approval.")
                
    elif author.bot and channel_id == STAFF_CHANNEL:
        await m.add_reaction(emoji='❎')
        await m.add_reaction(emoji='✅')  

# MONITOR FOR USER REACTIONS AND THEN POST IT
@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    channel_id = message.channel.id
    emoji = reaction.emoji
    if not user.bot:

        if channel_id == STAFF_CHANNEL:

            if emoji == '❎' or emoji == '✅':
                original_author = message.content.split(' ')[-1]
                original_author = original_author[2:-1]
                user = client.get_user(int(original_author))

                if emoji == '✅':
                    await send_to_channel(message, PUBLIC_CHANNEL, False)
                    await user.send("Your post was approved by the staff team! Keep up the good work!")

                else:
                    await user.send("Unfortunately the mod team didn't think your post was relevant to the important channel.\nMake sure it's on topic and time sensitive before posting.")

            else:
                await message.remove_reaction(emoji, user)

client.run(SECRET_KEY)