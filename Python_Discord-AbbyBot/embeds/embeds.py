import discord

def account_inactive_embed():
    """Returns an embed message for inactive accounts."""
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
    embed.set_footer(text="Thank you for your understanding.")
    return embed
