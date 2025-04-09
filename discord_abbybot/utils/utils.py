import discord

bot_avatar_url_cache = None  # Cache to save avatar URL

async def get_bot_avatar(bot: discord.Client, bot_id: int):
    global bot_avatar_url_cache
    
    # If we have already obtained the avatar, use the cache
    if bot_avatar_url_cache:
        return bot_avatar_url_cache
    
    # If it's not cached, get it from Discord
    bot_user = await bot.fetch_user(bot_id)
    bot_avatar_url_cache = bot_user.display_avatar.url  # Save in Cache
    return bot_avatar_url_cache
