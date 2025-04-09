import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from utils.utils import get_bot_avatar

bot_id = 1028065784016142398  # AbbyBot ID

class Minigames_commands(commands.GroupCog, name="minigames"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Play Rock/Paper/Scissors with AbbyBot. Choose between rock, paper or scissors to play!")    
    @app_commands.choices(option=[
        discord.app_commands.Choice(name="Rock", value=1),
        discord.app_commands.Choice(name="Paper", value=2),
        discord.app_commands.Choice(name="Scissors", value=3),
    ])

    async def rockpaperscissors(self, interaction: discord.Interaction, option: int):
            choices = ["Rock", "Paper", "Scissors"]
            user_choice = choices[option - 1]
            
            await interaction.response.send_message(f"You chose {user_choice}.")

            await asyncio.sleep(1)
            await interaction.channel.send("Hmm... I'll choose...")

            await asyncio.sleep(2)  
            bot_choice = random.choice(choices)

            await interaction.channel.send(f"{bot_choice}.")

            result = self.determine_rps_winner(user_choice, bot_choice)

            embed = discord.Embed(title="Rock, Paper, Scissors", description=result, color=discord.Color.blue())
            embed.add_field(name="Your choice", value=user_choice, inline=True)
            embed.add_field(name="Bot's choice", value=bot_choice, inline=True)

            # Get the bot's avatar (cached if it's been called before)
            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
    
            embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

            await interaction.channel.send(embed=embed)

    def determine_rps_winner(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            return "It's a tie!"
        elif (user_choice == "Rock" and bot_choice == "Scissors") or \
            (user_choice == "Paper" and bot_choice == "Rock") or \
            (user_choice == "Scissors" and bot_choice == "Paper"):
            return "Congratulations! You won!"
        else:
            return "You lose! The bot wins this time."

    # Start blackjack
    @app_commands.command(name="blackjack", description="Play Blackjack with AbbyBot!")
    async def blackjack(self, interaction: discord.Interaction):
        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        embed = discord.Embed(title="Blackjack", description="Let's play Blackjack!", color=discord.Color.blue())
        embed.add_field(name="Your hand", value=self.display_hand(player_hand), inline=False)
        embed.add_field(name="Dealer shows", value=dealer_hand[0], inline=False)
        embed.set_footer(text="Do you want 'Hit' to ask for a menu or 'Stand' to stand?")

        view = BlackjackButtons(deck, player_hand, dealer_hand, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    def create_deck(self):
        card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Hearts', 'Diamonds', 'Clovers', 'Spades']
        deck = [f'{value} of {suit}' for value in card_values for suit in suits]
        random.shuffle(deck)
        return deck

    def calculate_hand_value(self, hand):
        card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        value = 0
        aces = 0
        for card in hand:
            card_value = card.split()[0]
            value += card_values[card_value]
            if card_value == 'A':
                aces += 1
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def display_hand(self, hand):
        return ', '.join(hand)


class BlackjackButtons(discord.ui.View):
    def __init__(self, deck, player_hand, dealer_hand, player):
        super().__init__()
        self.deck = deck
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.player = player

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("You are not playing in this game. ", ephemeral=True)
            return

        self.player_hand.append(self.deck.pop())
        player_value = self.calculate_hand_value(self.player_hand)

        if player_value > 21:
            embed = discord.Embed(title="Blackjack", description="You went too far! The dealer wins.", color=discord.Color.red())
            embed.add_field(name="Your hand", value=self.display_hand(self.player_hand), inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title="Blackjack", description="Do you want 'Hit' to ask for a menu or 'Stand' to stand?", color=discord.Color.blue())
            embed.add_field(name="Your hand", value=self.display_hand(self.player_hand), inline=False)
            embed.add_field(name="Dealer shows", value=self.dealer_hand[0], inline=False)
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("You are not playing in this game.", ephemeral=True)
            return

        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

        dealer_value = self.calculate_hand_value(self.dealer_hand)
        player_value = self.calculate_hand_value(self.player_hand)

        if dealer_value > 21 or player_value > dealer_value:
            result = "Congratulations, you won!"
            color = discord.Color.green()
        elif player_value < dealer_value:
            result = "The dealer wins."
            color = discord.Color.red()
        else:
            result = "It's a tie."
            color = discord.Color.orange()

        embed = discord.Embed(title="Blackjack", description=result, color=color)
        embed.add_field(name="your hand", value=self.display_hand(self.player_hand), inline=False)
        embed.add_field(name="Dealer's hand", value=self.display_hand(self.dealer_hand), inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)

    def calculate_hand_value(self, hand):
        card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        value = 0
        aces = 0
        for card in hand:
            card_value = card.split()[0]
            value += card_values[card_value]
            if card_value == 'A':
                aces += 1
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def display_hand(self, hand):
        return ', '.join(hand)