import discord
import os

def account_inactive_embed():
    """Returns an embed message for inactive accounts with an image."""
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
    
    # Verificar si el archivo existe
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
    
    # Crear el archivo de Discord para adjuntar
    file = discord.File(image_path, filename="abbybot-user_inactive.png")
    
    # Añadir la imagen al embed usando el archivo adjunto
    embed.set_image(url="attachment://abbybot-user_inactive.png")
    
    # Añadir pie de página
    embed.set_footer(text="Thank you for your understanding.")
    
    # Devolver el embed y el archivo para adjuntar
    return embed, file
