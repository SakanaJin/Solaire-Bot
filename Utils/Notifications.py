import asyncio

async def senddm(ctx, content, embed=None):
    user = await ctx.bot.fetch_user(ctx.user.id)
    await user.send(content, embed=embed)