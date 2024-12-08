import discord
from discord.ext import commands
from discord import app_commands
from utils.db_utils import get_db_connection

class StoryView(discord.ui.View):
    def __init__(self, chapters, bot):
        super().__init__(timeout=120)
        self.chapters = chapters
        self.bot = bot  

        for chapter in chapters:
            self.add_item(StoryButton(chapter_id=chapter[0], chapter_name=chapter[1], bot=self.bot))


class StoryButton(discord.ui.Button):
    def __init__(self, chapter_id, chapter_name, bot):
        super().__init__(label=chapter_name, style=discord.ButtonStyle.primary, custom_id=f"chapter_{chapter_id}")
        self.chapter_id = chapter_id
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        db, cursor = get_db_connection()
        cursor.execute("""
            SELECT page_number, content, image_url
            FROM story_pages
            WHERE chapter_id = %s
            ORDER BY page_number
        """, (self.chapter_id,))
        pages = cursor.fetchall()
        cursor.close()
        db.close()

        if not pages:
            await interaction.followup.send("This chapter has no pages yet.", ephemeral=True)
            return

        # Mostrar la primera página
        view = PageView(pages)
        embed = view.create_embed(0)
        await interaction.followup.send(embed=embed, view=view)


class PageView(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.current_page = 0

        self.add_item(PreviousPageButton(self))
        self.add_item(NextPageButton(self))

    def create_embed(self, page_index):
        page = self.pages[page_index]
        embed = discord.Embed(
            title=f"📖 Page {page[0]}",
            description=page[1],
            color=discord.Color.green()
        )
        if page[2]:
            embed.set_image(url=page[2])
        embed.set_footer(text=f"Page {page_index + 1}/{len(self.pages)}")
        return embed


class PreviousPageButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.current_page > 0:
            self.parent_view.current_page -= 1
            embed = self.parent_view.create_embed(self.parent_view.current_page)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


class NextPageButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="➡️ Next", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.current_page < len(self.parent_view.pages) - 1:
            self.parent_view.current_page += 1
            embed = self.parent_view.create_embed(self.parent_view.current_page)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


class TellGroup(commands.GroupCog, name="tell"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="story", description="Let AbbyBot tell you a story interactively!")
    async def story(self, interaction: discord.Interaction):
        db, cursor = get_db_connection()

        # Obtener capítulos
        guild_id = interaction.guild_id
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()
        if not result:
            await interaction.response.send_message("This server is not registered.", ephemeral=True)
            return

        language_id = result[0]
        cursor.execute("""
            SELECT id, chapter_name, description 
            FROM story_chapters 
            WHERE language_id = %s
        """, (language_id,))
        chapters = cursor.fetchall()
        cursor.close()
        db.close()

        if not chapters:
            await interaction.response.send_message("No chapters are available.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📚 AbbyBot's Story",
            description="Select a chapter to begin exploring.",
            color=discord.Color.blurple()
        )
        for chapter in chapters:
            embed.add_field(name=chapter[1], value=chapter[2], inline=False)

        view = StoryView(chapters, self.bot)
        await interaction.response.send_message(embed=embed, view=view)
