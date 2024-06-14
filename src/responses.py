import random
import discord
from discord import Message, Member
import GetImageLink
import pandas as pd
headsortails = ['Heads', 'Tails']

def handle_response(message, user_message) -> str:
    member = discord.Member = message.author

    if user_message.startswith('!complain'):
        user_message = user_message[10:]
        return (f"{member.mention} nobody cares about '{user_message}', cry about it.")
    
    p_message = user_message.replace(" ","") #deletes white space

    if p_message.startswith("!gift"):
        p_message = p_message[5:]
        points = pd.read_csv("Points.csv")

        for name in points['Users']:
            if name in p_message:
                try:
                    member2 = discord.Member = name
                except Exception as e:
                    print(e)
                num = p_message[(len(name)):]
                break
            num = p_message

        if num == p_message:
            return "Invalid User"
        
        if int(num) > int(points[points['Users'].str.contains(str(member))].iat[0,1]):
            return (f"{member.mention} broke ass")
        
        a = points['Users'].str.contains(str(member))
        b = points['Users'].str.contains(str(member2))
        points.loc[a, 'Points'] = int(points[points['Users'].str.contains(str(member))].iat[0,1]) - int(num)
        points.loc[b, 'Points'] = int(points[points['Users'].str.contains(str(member2))].iat[0,1]) + int(num)
        points.to_csv("Points.csv", index=False)

        return (f"{member.mention} gifted {num} points to {member2}")

    p_message = p_message.lower() #lowercases the whole message
    
    if p_message == "!test":
        return str(message.author)
    
    if p_message == "!points":
        points = pd.read_csv("Points.csv")
        userpts = points[points['Users'].str.contains(str(message.author))].iat[0,1]
        return (f"{member.mention} has {userpts} points.")
    
    if p_message == "!leaderboard":  #needs better formatting
        points = pd.read_csv("Points.csv")
        sortedpts = points.sort_values(by='Points', ascending=False)
        sortedpts['place'] = range(1, 5)
        sortedpts = sortedpts[['place', 'Users', 'Points']]
        print(sortedpts)
        widths = [5, 18, 20]
        formats = ['{' + f':<{i}' + '}' for i in widths]
        return sortedpts.to_string(index=False, header=False, col_space= widths, formatters=[(lambda x: fmt.format(x)) for fmt in formats])

    if p_message == "!flip":
        return headsortails[random.randint(0,1)]
    
    if p_message == "!roll":
        return str(random.randint(1,6))
    
    if p_message.startswith('!rolld'):
        try:
            num = int(p_message[6:])
            return str(random.randint(1,num))
        except Exception as e:
            print(e)
    
    if p_message == "🌞":
        return "Praise the sun!"
    
    if p_message == "!traumatize":
        return GetImageLink.get_trauma()
    
    if "french" in p_message: #takes lots of power so maybe delete when not funny
        return "Eww French"
    
    if p_message == "!meme":
        return GetImageLink.get_meme()

    if p_message == "!berserk":
        return GetImageLink.get_berserk()
    
    if p_message.startswith('!waifu'):
        if "-n" in p_message:
            return GetImageLink.waifu_snake(1)
        else:
            return GetImageLink.waifu_snake(0)
        
    if p_message == '!help':
        return "`!complain: complaints\n!test: checks if Solaire is working\n!flip: flips a coin\n!roll: rolls a d6\n!rolld{number}: rolls a {number} sided die\n!meme: sends a random meme\n!berserk: sends a random berserk related image\n!waifu(optional)[-n]: throws a waifu [warning -n is dangerous]`"