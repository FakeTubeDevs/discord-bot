import discord
import platform
import requests
import time
import os

from dotenv import load_dotenv
from typing import Optional, Callable
from colorama import Back, Fore, Style
from datetime import datetime
from discord.ext import commands
from discord import ui
from keep_alive import keep_alive

load_dotenv()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.event
async def on_ready():
  prefix = Back.RESET + Fore.WHITE + Style.BRIGHT
  print(prefix + " Přihlášen jako: " + Fore.YELLOW + client.user.name)
  print(prefix + " Bot ID: " + Fore.YELLOW + str(client.user.id))
  print(prefix + " Verze Discord: " + Fore.YELLOW + discord.__version__)
  print(prefix + " Verze Python: " + Fore.YELLOW + platform.python_version())

  # nastavení aktivity na "Sleduje FakeTube.cz"
  await client.change_presence(activity=discord.Activity(
    type=discord.ActivityType.watching, name=os.getenv("AKTIVITA_STAV")))
  print(prefix + " Aktivita nastavena na:" + Fore.YELLOW + " " +
        os.getenv("AKTIVITA_TEXT"))
  synced = await client.tree.sync()
  print(prefix + f" {len(synced)} příkazy aplikace synchronizovány")

  print(Fore.RESET + Style.RESET_ALL)


@client.event
async def on_member_join(member):
  if client.get_guild(os.getenv("SERVER_ID")).get_channel(
      os.getenv("KANAL_VITEJ")):
    channel_id = os.getenv(
      "KANAL_VITEJ")  # ID kanálu, kam se má uvítací embed odeslat

    embed = discord.Embed(
      title=f"Vítej {member.display_name}",
      description=f"📥 Uživatel **{member.display_name}** se připojil na server",
      colour=discord.Colour(3715072))
    embed.set_footer(
      text=
      f"Je nás tu celkem {client.get_guild(os.getenv('KANAL_VITEJ')).member_count}"
    )

    channel = client.get_channel(channel_id)
    if channel is not None:
      await channel.send(embed=embed)


@client.hybrid_command(description="Zobrazí informace o videu na FakeTube")
async def video(ctx, kod: str):
  """Příkaz pro odeslání pravidel discord serveru"""
  api_endpoint = f'https://api.faketube.cz/api/v1/videos/single/{kod}?api_key=abcd'

  try:
    response = requests.get(api_endpoint)
    if response.status_code == 200:
      data = response.json()
      title = data[0].get('title')
      description = data[0].get('description')
      uploaderName = data[0].get('uploaderName')
      keywords = data[0].get('keywords')
      thumbnail = data[0].get('thumbnailUrl')
      numLikes = data[0].get('numLikes')
      numDislikes = data[0].get('numDislikes')
      views = data[0].get('views')
      datePublished = data[0].get('datePublished')

      embed = discord.Embed()
      embed.title = "Informace o videu"
      embed.description = f"**{title}**\n{description}"
      embed.color = discord.Colour(47087)
      embed.set_thumbnail(url=thumbnail)
      embed.add_field(name="Klíčová slova",
                      value=f"{keywords.replace(',', ', ')}",
                      inline=False)
      embed.add_field(name="Autor", value=f"{uploaderName}", inline=False)
      embed.add_field(name="Hodnocení",
                      value=f"Líbí se: {numLikes}\nNelíbí se: {numDislikes}",
                      inline=True)
      embed.add_field(name="Počet zhlédnutí", value=f"{views}", inline=True)
      embed.add_field(name="Publikováno",
                      value=f"{datetime.fromisoformat(datePublished)}",
                      inline=False)
      await ctx.send(embed=embed)
    else:
      await ctx.send(
        f'Failed to load data from API. Status Code: {response.status_code}')
  except requests.exceptions.RequestException as e:
    await ctx.send(f'Error occurred while fetching data from API: {str(e)}')


@client.hybrid_command(description="Zobrazí pravidla serveru")
async def pravidla(ctx):
  """Odeslání pravidel discord serveru do aktuálního kanálu"""
  if (ctx.message.author.id == os.getenv("AUTOR_ID")):
    embed = discord.Embed(
      title="Pravidla serveru",
      description=
      "Toto jsou pravidla discord serveru projektu FakeTube. Všichni uživatelé, bez ohledu na jejich role, se svou přítomností zavazují je dodržovat.",
      colour=discord.Colour(47087))
    embed.add_field(
      name="1. Respekt k ostatním členům",
      value=
      "Buďte zdvořilí a respektujte názory a přesvědčení ostatních. Nemocneťte, urážejte ani nesnažte se ostatní provokovat.",
      inline=False)
    embed.add_field(
      name="2. Vhodný obsah",
      value=
      "Neposílejte, nezveřejňujte ani nesdílejte obsah, který je násilný, urážlivý, nevhodný nebo porušuje autorská práva.",
      inline=False)
    embed.add_field(
      name="3. Bez spamu",
      value="Opakovaně nezasílejte stejný obsah nebo zbytečné zprávy.",
      inline=False)
    embed.add_field(
      name="4. Žádná propagace bez povolení",
      value=
      "Neposílejte žádnou nežádanou reklamu nebo propagaci bez předchozí domluvy s Týmem FakeTube.",
      inline=False)
    embed.add_field(
      name="5. Dodržujte kanály",
      value="Posílejte obsah ve správných kanálech a dodržujte jejich témata.",
      inline=False)
    embed.add_field(name="6. Bez NSFW obsahu",
                    value="Neposílejte jakýkoli NSFW materiál.",
                    inline=False)
    embed.add_field(name="7. Dodržujte Discord pravidla",
                    value="Dodržujte pravidla Discordu.",
                    inline=False)
    embed.add_field(
      name="8. Nevýhodné chování",
      value=
      "Nebudeme tolerovat šikanování, obtěžování nebo jakékoli jiné nevhodné chování.",
      inline=False)
    embed.add_field(
      name="9. Nejste členy týmu",
      value=
      "Nenařizujte ostatním, co mají dělat. Respektujte všechny členy Týmu FakeTube.",
      inline=False)
    embed.add_field(
      name="10. Rozhodnutí týmu",
      value=
      "Rozhodnutí členů Týmu FakeTube jsou konečná. Pokud máte nějaký problém, obraťte se na ně soukromou zprávou.",
      inline=False)
    embed.set_footer(
      text=
      "Tato pravidal se mohou kdykoli bez předchozího upozornění změnit.\nNeznalost pravidel neomlouvá!"
    )
    await ctx.send(embed=embed)


@client.hybrid_command(description="Zobrazí důležité odkazy")
async def odkazy(ctx):
  """Odeslání důležitých odkazů do aktuálního kanálu"""
  if (ctx.message.author.id == os.getenv("AUTOR_ID")):
    embed = discord.Embed(
      title="Důležité odkazy",
      description="Tady najdete všechny důležité odkazy projektu FakeTube",
      colour=discord.Colour(47087))
    embed.add_field(name="Webová stránka",
                    value="https://faketube.cz",
                    inline=False)
    embed.add_field(name="FakeTube Wiki",
                    value="https://wiki.faketube.cz",
                    inline=False)
    embed.add_field(name="Twitter",
                    value="https://twitter.com/FakeTube_CZ",
                    inline=False)
    embed.add_field(name="Facebook",
                    value="https://facebook.com/faketubeofficial",
                    inline=False)
    embed.add_field(name="Instagram",
                    value="https://instagram.com/faketubecz",
                    inline=False)
    await ctx.send(embed=embed)


@client.hybrid_command(description="Seznam všech příkazů")
async def pomoc(ctx):
  """Odeslání seznamu příkazů (help)"""
  embed = discord.Embed(
    title="Seznam příkazů",
    description="Seznam všech příkazů, kterým <@1131813041739153509> rozumí",
    color=discord.Colour(47087))
  embed.add_field(name="Pro všechny",
                  value="`/pomoc` - zobrazí tento seznam",
                  inline=False)
  embed.add_field(
    name="Pro uživatele",
    value=
    "`/video kod` - zobrazí informace o videu podle kódu videa\n`/navrh projekt|discord text` - odešle text návrhu do určité kategorie",
    inline=False)
  embed.add_field(
    name="Pro členy týmu",
    value="`/oznameni zprava` - odešle text oznámení do kanálu pro oznámení",
    inline=False)
  embed.add_field(
    name="Pro autora",
    value=
    "`/odkazy` - odešle embed s důležitými odkazy projektu FakeTube\n`/pravidla` - odešle sembed s pravidly discord serveru pro projekt FakeTube\n`/navrh přijmout|zamítnout zprava_id` - přijme nebo zamítne návrh s daným ID zprávy (nutno použít v kanálu kde se zpráva s návrhem nachází)",
    inline=False)
  await ctx.send(embed=embed)


@client.hybrid_command(aliases=['oznam'],
                       description="Odešle oznámení do kanálu")
async def oznameni(ctx, zprava: str):
  # Kontrola, zda autor je autorem bota nebo má určité ID
  allowed_ids_str = os.getenv("SPRAVCI_ID").split(",")  # ID členů, kteří mají povolení
  allowed_ids = [int(x) for x in allowed_ids_str]

  if ctx.author.id not in allowed_ids:
    await bezOpravneny(ctx=ctx)
    return

  try:
    channel = client.get_channel(int(os.getenv("KANAL_OZNAMENI")))
    if channel is None:
      await prikazChyba(
        ctx=ctx,
        title="Kanál nenalezen",
        description=f"Kanál pro oznámení nebyl nalezen.")
      return

    embed = discord.Embed(title="Oznámení",
                          description=zprava,
                          colour=discord.Colour(16483584))
    embed.set_thumbnail(
      url=
      "https://lh3.googleusercontent.com/fife/AKsag4Pge46fV73PLGLAhHUg8RgY-JV9lHcZ8K9h2-e4pbRs7Eu-VomO6mYCh2XaYUikKwqU6S50TH8-ZwYZhW8ZS79f2d3pVh0IxMZs6sz8A0-cnkBOuYSA1F071fDQfai6G-wUJG74CrsZgMA-NBLaSnmW3_U2jKAFp7UahU2t8KCHmSZi0Bpz5lupW7orIJJVcXAcxxUN5lk605KSlZt5LGi76C2mroadeGiL6fB_qxCLv7WNNakrCzeKUg1pfdg352P_1t9ac3yKMyCfQ7YE7VK0SDLyj2xSlrJuuTlt81nz4Ou6g-Umaw-h97bN3MdsSnuFO5LNZhz_6zrv_qLGHCi77QBUfCs8sQ8Er7IkoABEPpv4127vSGoEVNSf6mMwBv2bsDzYcLFfXy8kTBRFhypane1jzyzJNuu3XGtvZJbAlZAGwZ-zLcXLiNuFc3NxGSGqhKHzNGaVcXHDqB3st2N1MPP9U9F0gIbXV4AsckcfjY8h9Oh8eP1SCSGWBzNeWwRCe9fx0oP8hOjHhFrXGw_mJHH0m8qZa2A80ENPVu4RDIex59vuKPqXK6ZnLchTsqUkfcJC-gZ3-ZbwaGctuiTcnRU5UsXJ15Rumi-XViVfCoihnz6NHuxY835FZAuxbeIxnsc4yNwfX8ft0HY1XYTYJpohJIGmXiUSKkRL3y8ngOFFxKQFe5zPzHwW9PDf68E84KTxDQxeh-V-bQ72EnQHGNc-9pmUS_slXlyaAMtLWEFh68nkSyFVlWr4Hoj3SBIk2TMZAd2-Wohy9zZxYhvVU3k1g2FBOY2EvH4zcEQfCMLa0MGc3NorNvH0IQNWvRsyuXL_6y7HdonwN1mmwB3RK--s_aC0tnhkM42EnpUOl0NUQRWowJ7A9f6Z4rItnUzUhY18f2MiK51eFOMwwtPTqrp6Q_9Ks0k2s8CwQKlUgfaqYrNKAwpN_zzo5SXagR6N9GCD-BalC_oM_vx2JWcTL6mWroSGAFmNkZy2G0tumoASkIQUNnZ6PV6emAdbeP5yVC9G4TPtz7f9NkcoAnTC086PaOJIGTFiWINa40FICK6OaeOiLj73hXLWUvLOYRHvw1if1JHXpLopHKa4W70lJjBIM1W0SCIdgRWl1YCQx8Y73kXT1ZG6uDodJm-A9khi8ITmSLYVQckjyglWQlKt0oFITWPJQvmx9AEGIuPwyttGEuopvCkQa8KGBdgHoQXlFumrBO6QFvWIHv3TY451RMmZHHZS_5d6LCoSM08MAnOC0oD8w-Z7bnQxQY3yPq1ezISW3UyRImSVy5YQk_9ZCXS4_nRMLIXZrHVSS7L17elxQQtFC9EGo_naBWzkqCe67OpgjhwgQxe16xYUEItXoBr5kvFO31ltiSGFtXW_8hWB8IV3oTzotT5SDn5WiC8_3ivWhPLGP92r-XQgld3LmIKVwVFsMLSyt5bHinhh0MymPKXuTKxdhQasRkYmnrvyGk4e2PGfTBtmgncTlFJUvkr6w7hvDa-I1zmvBBnHx73M0mhIdD4X8pyv2VShRgcmbHN-lCdq88tgqGwfZP1dt5dYt091KPxDck5K8RUL3Q=w1280-h657"
    )
    await channel.send(content="@everyone", embed=embed)

    await prikazUspech(
      ctx=ctx,
      title="Oznámení odesláno",
      description=f"Oznámení bylo úspěšně odesláno do kanálu {channel.mention}."
    )
  except Exception as e:
    await prikazChyba(
      ctx=ctx,
      title="Chyba při odesílání",
      description=f"Nastala chyba při odesílání oznámení: {str(e)}")


@client.hybrid_command(name="navrh", description="Vytvoří návrh")
async def navrh(ctx, category, text):
  category = category.lower()
  if category not in ('projekt', 'discord', 'přijmout', 'zamítnout'):
    await prikazChyba(
      ctx=ctx,
      title="Nesprávná kategorie",
      description="Použijte `projekt`, `discord`, `přijmout`, `zamítnout`.")
    return

  if category in ('přijmout', 'zamítnout'):
    allowed_role = ctx.guild.get_role(os.getenv("ROLE_TYM"))
    if allowed_role is None or allowed_role not in ctx.author.roles:
      await prikazChyba(
        ctx=ctx,
        title="Neorpávněné použití",
        description="Nemáte oprávnění použít tuto kategorii příkazu.")
      return

  channel = None

  # Zde určete, kam se má zaslat návrh.
  if category == "projekt":
    channel = client.get_channel(os.getenv("KANAL_PROJEKT"))
  elif category == "discord":
    channel = client.get_channel(os.getenv("KANAL_DISCORD"))
  elif category == "přijmout":
    await prijmout_navrh(ctx, message_id=text)
  elif category == "zamítnout":
    await zamitnout_navrh(ctx=ctx, message_id=text)

  # Pošlete návrh do vybraného kanálu.
  if channel:
    embed = discord.Embed(title=f'Návrh od {ctx.author}',
                          description=text,
                          color=discord.Colour(7473591))
    message = await channel.send(embed=embed)
    await prikazUspech(ctx=ctx,
                       title="Návrh odeslán",
                       description="Návrh byl úspěšně odeslán.")
    await message.add_reaction('🔼')
    await message.add_reaction('🔽')


async def prijmout_navrh(ctx, message_id):
  await schvalit_zamitnout_navrh(ctx, message_id, "Přijatý", "přijat",
                                 discord.Colour(3715072))


async def zamitnout_navrh(ctx, message_id):
  await schvalit_zamitnout_navrh(ctx, message_id, "Zamítnutý", "zamítnut",
                                 discord.Colour(13631488))


async def schvalit_zamitnout_navrh(ctx, message_id, status, status_text,
                                   status_color):
  if ctx.channel.id not in (1131510319274004562, 1131510321106931833):
    await prikazChyba(
      ctx=ctx,
      title="Nesprávné použití",
      description=
      "Tento příkaz lze použít pouze v kanálech pro projekt a discord.")
    return

  try:
    message_id = int(message_id)
    message = await ctx.fetch_message(message_id)
  except (ValueError, discord.NotFound):
    await prikazChyba(
      ctx=ctx,
      title="Nenalezená zpráva",
      description="Zprávu s tímto ID se v tomto kanálu nepodařilo najít.")
    return

  embed = message.embeds[0]
  puvodni_titulek = embed.title.replace("Návrh", "návrh")
  embed.title = f'{status} {puvodni_titulek}'
  embed.color = status_color
  await message.edit(embed=embed)


async def bezOpravneny(ctx):
  embed = discord.Embed(
    title="Nedostatečná oprávnění",
    description="K použití tohoto příkazu nemáš dostatečná oprávnění!",
    colour=discord.Colour(13631488))
  await ctx.reply(embed=embed)


async def prikazChyba(ctx, title: str, description: str):
  embed = discord.Embed(title=title,
                        description=description,
                        colour=discord.Colour(13631488))
  await ctx.reply(embed=embed)


async def prikazUspech(ctx, title: str, description: str):
  embed = discord.Embed(title=title,
                        description=description,
                        colour=discord.Colour(3715072))
  await ctx.reply(embed=embed)


keep_alive()
client.run(os.getenv("TOKEN"))