import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

registrations = []

class RegistrationModal(Modal, title="Iscrizione Torneo"):
    referente = TextInput(label="Nome Referente")
    team_name = TextInput(label="Nome Team")
    members = TextInput(label="Nomi Partecipanti", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        global registrations
        registration = {
            "user_id": interaction.user.id,
            "referente": self.referente.value,
            "team_name": self.team_name.value,
            "members": self.members.value
        }
        registrations.append(registration)
        await update_participants_channel(interaction.guild)
        embed = discord.Embed(title="Iscrizione completata!", color=0x8800ff)
        embed.set_thumbnail(url="attachment://logo.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfirmUnregister(View):
    def __init__(self, user_id):
        super().__init__(timeout=30)
        self.user_id = user_id

    @discord.ui.button(label="Si", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        global registrations
        registrations = [r for r in registrations if r['user_id'] != self.user_id]
        await update_participants_channel(interaction.guild)
        embed = discord.Embed(title="Iscrizione annullata", color=0xff0000)
        embed.set_thumbnail(url="attachment://logo.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(title="Operazione annullata", color=0xaaaaaa)
        embed.set_thumbnail(url="attachment://logo.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class RegisterView(View):
    @discord.ui.button(label="Iscriviti", style=discord.ButtonStyle.success)
    async def register(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RegistrationModal())

    @discord.ui.button(label="Annulla Iscrizione", style=discord.ButtonStyle.danger)
    async def unregister(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(view=ConfirmUnregister(interaction.user.id), ephemeral=True)


async def update_participants_channel(guild):
    channel = discord.utils.get(guild.text_channels, name="partecipanti-torneo")
    if not channel:
        return

    await channel.purge()
    for i, reg in enumerate(registrations):
        await channel.send(
            f"**Team {i+1}**\nReferente: {reg['referente']}\nTeam: {reg['team_name']}\nPartecipanti: {reg['members']}"
        )

@bot.event
async def on_ready():
    print(f"Bot connesso come {bot.user}")
    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name="torneo")
        if category:
            channel = discord.utils.get(category.text_channels, name="iscrizioni-torneo")
            if channel:
                await channel.purge()
                embed = discord.Embed(title="Iscrizioni Torneo", description="Premi un pulsante per iscriverti o annullare.", color=0xffff00)
                embed.set_thumbnail(url="attachment://logo.png")
                await channel.send(embed=embed, view=RegisterView())

bot.run("YOUR_BOT_TOKEN")
