import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio
from aiohttp import web
import random

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
prefix = os.getenv("PREFIX")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix,intents=intents)
bot.remove_command("help")

# Web server
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

# Evenimente bot

@bot.event
async def on_ready():
    print(f"Botul a pornit cu numele {bot.user.name}")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="g!help"
        )
    )

    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")


# Variabile globale sau liste

lista_culori = [discord.Color.red(), discord.Color.blue(), discord.Color.green(), discord.Color.yellow(), discord.Color.purple(), discord.Color.orange(), discord.Color.teal(), discord.Color.dark_blue(), discord.Color.dark_green(),]

lista_zaruri = [
    "<:zar1:1429269726046982186>",
    "<:zar2:1429269727649202237>",
    "<:zar3:1429269729331118090>",
    "<:zar4:1429269731759886496>",
    "<:zar5:1429269734142246912>",
    "<:zar6:1429269735870038016>",
]

# Comenzi bot

@bot.command()
async def salut(ctx):
    await ctx.reply(f"Salut {ctx.author.mention}, latenta mea este {round(bot.latency*1000)} ms!")

@bot.tree.command(name="salut", description="Te saluta si iti arata latenta botului")
async def slash_salut(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Salut {interaction.user.mention}, latenta mea este {round(bot.latency*1000)} ms!"
    )

@bot.command()
async def help(ctx):
    culoare = random.choice(lista_culori)
    embed = discord.Embed(
        title="Comenzi",
        description=(
            "Lista de comenzi disponibile\n"
            "1. help - te aduce aici\n"
            "2. salut - te saluta si iti arata latenta botului\n"
            "3. quote - face un quote\n"
            "4. poll - face un sondaj\n"
            "5. diceroll - arunci cu un zar \n"
            "6. avatar - primesti o imagine cu avatarul tau sau persoanei mentionate\n"
            "6. userinfo - arata informatii despre un utilizator\n"
            "7. kick - dai afara pe cineva de pe server (necesita permisiunea de kick)\n"
            "8. ban - banezi pe cineva de pe server (necesita permisiunea de ban)\n"
            "9. purge - sterge mesaje (necesita permisiunea de manage messages)\n"
        ),
        color=culoare
    )
    embed.set_footer(text="Toate comenzile trebuie scrise cu litere mici si cu prefixul " + prefix + ".")
    await ctx.send(embed=embed)

@bot.command()
async def poll(ctx, *, message: str):
    await ctx.message.delete()
    culoare = random.choice(lista_culori)
    embed = discord.Embed(title="Sondaj nou!", description=message, color=culoare)
    embed.set_footer(text=f"Sondaj creat de {ctx.author}")
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("✅")
    await poll_message.add_reaction("❌")

@bot.command()
async def quote(ctx, *, message: str):
    parts = message.rsplit(" ", 1)

    if len(parts) < 2 or not parts[1].startswith("<@"):
        await ctx.send("❌ Comanda se foloseste astfel: `!quote <mesajul> <@mention>`")
        return

    quote_text = parts[0]
    mentioned_user = parts[1]
    await ctx.message.delete()
    sent_message = await ctx.send(f"📜 **Quote:** {quote_text} / ** {mentioned_user}** 2025")
    await sent_message.add_reaction("<:pepe_crying:1429109461309587537>")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    color = random.choice(lista_culori)
    embed = discord.Embed(title=f"Avatarul lui {member.name}", color=color)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def diceroll(ctx):
    zar = random.choice(lista_zaruri)
    await ctx.send(f"{zar}")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author  # Default to command author if no user is mentioned
    color = random.choice(lista_culori)
    embed = discord.Embed(title=f"Informatii despre utilizatorul {member}:", color=color)
    embed.set_thumbnail(url=member.avatar.url)

    embed.add_field(name="🆔 ID", value=member.id, inline=False)
    embed.add_field(name="👤 Username", value=f"{member.name}#{member.discriminator}", inline=True)
    embed.add_field(name="📛 Nickname", value=member.nick if member.nick else "Niciunul", inline=True)
    embed.add_field(name="📅 Si-a creat contul pe data de", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="📥 A intrat pe server pe data de", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown", inline=False)
    embed.add_field(name="🔧 Roluri", value=", ".join(role.name for role in member.roles[1:]) or "Niciunul", inline=False)

    embed.set_footer(text=f"Solicitat de catre {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        return await ctx.send("Nu te poți da singur afară!")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("Nu poți da afară pe cineva cu rol egal sau mai mare decât al tău.")
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} a fost dat afară din server!")
    except discord.Forbidden:
        await ctx.send("❌ Nu am permisiunea să dau afară acest membru.")
    except Exception as e:
        await ctx.send(f"❌ Eroare: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        return await ctx.send("Nu te poți banui singur!")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("Nu poți banui pe cineva cu rol egal sau mai mare decât al tău.")
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} a fost banat din server!")
    except discord.Forbidden:
        await ctx.send("❌ Nu am permisiunea să banui acest membru.")
    except Exception as e:
        await ctx.send(f"❌ Eroare: {e}")

@kick.error
@ban.error
async def mod_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nu ai permisiunea necesară pentru a folosi această comandă.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Te rog menționează un membru pentru această comandă.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 1):

    # Restricții
    if amount > 100:
        return await ctx.send("❌ Pot șterge maxim 100 mesaje.")
    if amount <= 0:
        return await ctx.send("❌ Te rog să specifici un număr pozitiv de mesaje de șters.")

    try:
        # Purge mesaje, excludem mesajul botului dacă se șterge doar 1 mesaj
        if amount == 1:
            # Sterge ultimul mesaj din canal care nu este al botului
            messages = [m async for m in ctx.channel.history(limit=5) if m.id != ctx.message.id]
            if messages:
                await messages[0].delete()
                await ctx.send(f"✅ Am șters 1 mesaj.", delete_after=5)
            else:
                await ctx.send("❌ Nu am găsit mesaje de șters.", delete_after=5)
        else:
            deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.id != ctx.message.id)
            await ctx.send(f"✅ Am șters {len(deleted)} mesaje.", delete_after=5)
    except discord.Forbidden:
        await ctx.send("❌ Nu am permisiunea să șterg mesaje aici.")
    except Exception as e:
        await ctx.send(f"❌ Eroare: {e}")

# Mesaje de eroare
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nu ai permisiunea necesară pentru a folosi această comandă.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Te rog să introduci un număr valid de mesaje.")

# Pornire bot si webserver
@bot.event
async def main():
    await start_webserver()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())