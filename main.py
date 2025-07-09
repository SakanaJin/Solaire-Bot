import discord
from discord import Client, Intents, Message
import responses

TOKEN = 'MTIwOTYwMjc0ODkwODA0ODQ2NA.GmC8Ay.we4tIuF9OKsKTpgzrDoLSMsjU6nGzuAWBAMyQk'

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents = intents)

async def send_message(message, user_message):
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response = responses.handle_response(message, user_message)
        if response != None: 
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is ready!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
        
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f"{username} said: {user_message} ({channel})")

    await send_message(message, user_message)
   
def main():
 client.run(token = TOKEN)

if __name__ == "__main__":
    main()
