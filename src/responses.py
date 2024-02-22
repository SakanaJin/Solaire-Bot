import random
import discord
from discord import Message
headsortails = ['Heads', 'Tails']

def handle_response(message, user_message) -> str:

    if user_message.startswith('!complain'):
        user_message = user_message[10:]
        member = discord.Member = message.author
        return (f"{member.mention} nobody cares about '{user_message}', cry about it.")
    
    p_message = user_message.lower()

    p_message = p_message.replace(" ","")

    if p_message == "!help":
        return "`[Help Message Here]`"
    
    if p_message == "!test":
        return 'working'
    
    if p_message == "!flip":
        return headsortails[random.randint(0,1)]
    
    if p_message == "!roll":
        return str(random.randint(1,6))
    
    if p_message.startswith('!rolld')
        try:
            num = int(p_message[6:])
            return str(random.randint(1,num))
        except Exception as e:
            print(e)
    
    if p_message == "🌞":
        return "Praise the sun!"
    
    if "french" in p_message: #takes lots of power so maybe delete when not funny
        return "Eww French"
    