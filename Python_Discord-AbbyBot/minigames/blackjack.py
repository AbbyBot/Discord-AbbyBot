import discord
from discord.ext import commands
from discord import app_commands
import random

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
