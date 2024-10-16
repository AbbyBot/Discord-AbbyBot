import discord
import os
from utils.utils import get_bot_avatar

bot_id = 1028065784016142398


async def account_inactive_embed(bot: discord.Client):
    """Returns an embed message for inactive accounts with an image and bot avatar in the footer."""
    
    # Get the bot avatar URL
    bot_avatar_url = await get_bot_avatar(bot, bot_id)
    
    embed = discord.Embed(
        title="Account Inactive Notice",
        description=(
            "Your account has been marked as **inactive** because you likely chose not to participate in the AbbyBot project.\n\n"
            "As a result, you will no longer be able to send commands or trigger events while this status remains.\n\n"
            "If you believe this was an error, please send a message to [Support URL](https://url1.com).\n"
            "Otherwise, if you opted out voluntarily but have changed your mind, you can fill out a form at [Reactivation Form](https://url2.com) "
            "where an admin will review your request to reinstate your account."
        ),
        color=discord.Color.red()
    )

    # Load the image file
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "user", "abbybot-user_inactive.png")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
    
    # Create the Discord file to attach
    file = discord.File(image_path, filename="abbybot-user_inactive.png")
    
    # Add the image to the embed using the attachment
    embed.set_image(url="attachment://abbybot-user_inactive.png")
    
    # Add footer with bot avatar
    embed.set_footer(text="AbbyBot. Thank you for your understanding.", icon_url=bot_avatar_url)
    
    # Return the embed and the file to attach
    return embed, file
