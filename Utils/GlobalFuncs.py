from Utils.EventDispatcher import dispatch_event

async def addexp(ctx, amount) -> int:
        user = ctx.user
        total = amount
        total += sum(effect_link.effect.value for effect_link in user.effect_links if not effect_link.effect.ispercent and not effect_link.effect.forsunlight)
        total += sum((effect_link.effect.value // 100) * total for effect_link in user.effect_links if effect_link.effect.ispercent and not effect_link.effect.forsunlight)
        lvldiff = 0
        while(total >= user.nextlvl):
            lvldiff += 1
            user.lvl += 1
            total -= user.nextlvl
            user.calc_nextlvl()
        user.nextlvl - total
        if lvldiff > 0:
            await dispatch_event("user_lvlup", ctx=ctx, lvldiff=lvldiff)
        await dispatch_event("add_userexp", ctx=ctx, amount=total)
        return total

async def addSunlight(ctx, amount) -> int:
    user = ctx.user
    total = amount
    total += sum(effect_link.effect.value for effect_link in user.effect_links if not effect_link.effect.ispercent and effect_link.effect.forsunlight)
    total += sum((effect_link.effect.value // 100) * total for effect_link in user.effect_links if effect_link.effect.ispercent and effect_link.effect.forsunlight)
    user.sunlight += total
    await dispatch_event("add_sunlight", ctx=ctx, amount=total)
    return total

async def subSunlight(ctx, amount) -> int:
    user = ctx.user
    user.sunlight -= amount
    if user.sunlight < 0:
        raise ValueError(f"{amount} > {user.sunlight}")
    await dispatch_event("sub_sunlight", ctx=ctx, amount=amount)
    return amount