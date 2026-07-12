from sqlalchemy import select
from datetime import datetime, timedelta

from database import get_db

from Entities.Users import User
from Entities.UsersItems import UserItem
from Entities.UsersQuests import UserQuest
from Entities.Quests import Quest
from Entities.Effects import EffectType
from Entities.EffectsUsers import EffectUser
from Entities.EffectsStocks import EffectStock
from Entities.EffectsBusinesses import EffectBusiness

from Utils.DependInject import Depends
from Utils.Time import round_nearest_hour
from Utils.QuestHandler import register_quest
from Utils.EventDispatcher import dispatch_event
from Utils.GlobalFuncs import addexp, addSunlight

async def complete_quest(userquest: UserQuest, quest: Quest, ctx):
    user = ctx.user
    db = ctx.db
    userquest.completed = True
    userquest.completed_at = datetime.now()
    await addSunlight(ctx=ctx, amount=quest.sunlight)
    await addexp(ctx=ctx, amount=quest.exp)
    item_map = {item_link.item.id: item_link.item for item_link in user.item_links}
    for item_link in quest.item_links:
        if item_link.itemid in item_map.keys():
            useritem = item_map.get(item_link.itemid)
            useritem.amount += item_link.amount
            continue
        useritem = UserItem(
            user=user,
            item=item_link.item,
            amount=item_link.amount
        )
        db.add(useritem)
        await dispatch_event("get_items", ctx=ctx, item=item_link.item, amount=item_link.amount)
    monumentids = [monument.id for monument in user.monuments]
    for monument in quest.monuments:
        if monument.id in monumentids:
            continue
        user.monuments.append(monument)
        await dispatch_event("get_monument", ctx=ctx, monument=monument)
    for effect in quest.effects:
        match effect.etype:
            case EffectType.USER:
                effectuser = EffectUser(
                    user=user,
                    effect=effect,
                    expiresat=round_nearest_hour(datetime.now() + timedelta(hours=effect.expiresin))
                )
                db.add(effectuser)
                await dispatch_event("gain_effect", ctx=ctx, effect_link=effectuser)
            case EffectType.STOCK:
                for stock in user.stocks:
                    effectstock = EffectStock(
                        stock=stock,
                        effect=effect,
                        expiresat=round_nearest_hour(datetime.now() + timedelta(hours=effect.expiresin))
                    )
                    db.add(effectstock)
                    await dispatch_event("gain_effect", ctx=ctx, effect_link=effectstock)
            case EffectType.BUISINESS:
                for business in user.businesses:
                    effectbusiness = EffectBusiness(
                        business=business,
                        effect=effect,
                        expiresat=round_nearest_hour(datetime.now() + timedelta(hours=effect.expiresin))
                    )
                    db.add(effectbusiness)
                    await dispatch_event("gain_effect", ctx=ctx, effect_link=effectbusiness)
    await dispatch_event("quest_complete", ctx=ctx, quest=quest)
    db.delete(userquest)

@register_quest("command")
async def handle_use_command(userquest: UserQuest, cmdname: str, ctx):
    quest: Quest = userquest.quest
    if quest.target_identifier != cmdname:
        return
    if userquest.completed:
        return
    userquest.progress += 1
    if userquest.progress >= quest.target:
        await complete_quest(userquest=userquest, quest=quest, ctx=ctx)
    