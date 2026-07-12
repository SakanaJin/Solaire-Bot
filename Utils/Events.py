import random
from discord import Embed

from Utils.Notifications import senddm
from Utils.EventDispatcher import register_event
from Utils.QuestHandler import quest_handlers
from Utils.QuestConsts import QuestTypes

@register_event("user_lvlup")
async def handle_user_lvlup(*, ctx, lvldiff, **kwargs):
    await senddm(ctx=ctx, content=f"Leveled up to lvl {ctx.user.lvl:,}.")

@register_event("add_userexp")
async def handle_add_userexp(*, ctx, amount, **kwargs):
    pass

@register_event("add_sunlight")
async def handle_add_sunlight(*, ctx, amount, **kwargs):
    pass

@register_event("sub_sunlight")
async def handle_sub_sunlight(*, ctx, amount, **kwargs):
    pass

@register_event("quest_complete")
async def handle_quest_complete(*, ctx, quest, **kwargs):
    embed = Embed(
        title=quest.name,
        color=quest.rarity.value
    )
    embed.description = quest.description
    embed.add_field(name="Rewards:", value="", inline=False)
    embed.add_field(name="Sunlight:", value=f"{quest.sunlight:,}", inline=True)
    embed.add_field(name="exp:", value=f"{quest.exp:,}", inline=True)
    embed.add_field(name="Effects:", value="", inline=False)
    for index, effect in enumerate(quest.effects):
        embed.add_field(name=effect.name, value=effect.description, inline=index % 3 != 0)
    item_strings = [f"{item_link.item.name}: {item_link.amount}" for item_link in quest.item_links]
    embed.add_field(name="Items:", value="\n".join(item_strings), inline=False)
    monument_strings = [f"{monument.name}" for monument in quest.monuments]
    embed.add_field(name="Monuments:", value="\n".join(monument_strings), inline=False)
    await senddm(ctx=ctx, content="Quest Completed", embed=embed)

@register_event("gain_effect")
async def handle_gain_effect(*, ctx, effect_link, **kwargs):
    embed = Embed(
        title=effect_link.effect.name,
        color=random.randint(0, 255)
    )
    timestamp = None
    if effect_link.expiresat != 0:
        timestamp = int(effect_link.expiresat.timestamp())
    embed.description = effect_link.effect.description
    embed.footer = f"Expires: <t:{timestamp}:R> (<t:{timestamp}:t>)"
    await senddm(ctx=ctx, content="Gained Effect", embed=embed)

@register_event("effect_expire")
async def handle_effect_expire(*, ctx, effect_link, **kwargs):
    pass

@register_event("get_monument")
async def handle_get_monument(*, ctx, monument, **kwargs):
    pass

@register_event("get_items")
async def handle_get_items(*, ctx, item, amount, **kwargs):
    pass

@register_event("command")
async def handle_command(*, command, ctx, **kwargs):
    quest_links = ctx.user.quest_links
    for quest_link in quest_links:
        if quest_link.quest.type != QuestTypes.COMMAND or quest_link.quest.target_identifier != command:
            continue
        handler = quest_handlers.get(QuestTypes.COMMAND)
        if handler:
            await handler(userquest=quest_link, cmdname=command, ctx=ctx)

