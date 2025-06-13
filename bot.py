import discord
from discord.ext import commands
from discord import ForumOrderType

import asyncio

from dotenv import load_dotenv
import os 

load_dotenv()

print("bot launch ...")

intents = discord.Intents.default()
intents.message_content = True	# important si tu veux lire le contenu des messages
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================== Macro ========================== #

ANNOUNCE_CHANNEL = 1380334157040717995 # ID of announce channel
EMOJI = "✅"  # Emoji for the role

stuffNewParty_prompt:str="Réagissez à ce message pour qu'on voie notre stuff ( pour les matelats qui se murge la gueule et à une place et inversement ) :\n\
- 🥔 : Vodka\n\
- 🏴‍☠️ : Rhum Blanc\n\
- 🥃 : Rhum Brun\n\
- 🇲🇽 : Tequilla\n\
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 : Whisky\n\
- 🍷 : Pinard\n\
- 🦌 : Jaëger\n\
- 🔴 : Liqueur Random\n\
- 🍎 : Jus de Fruit\n\
- 🫧 : Soda / Booster\n\
- 🥜 : Biscuit Apéro\n\
- ♦️ : paquet de Cartes\n\
- 🎲 : Jeux de Sociétés\n\
- 📻 : Enceinte\n\
- 🛏️ : Lit / Matelas pour les gens Humain\n\
- ⚰️ : Lit / Matelas pour les déchets"

# ======================== Bot Events ======================== #

@bot.event
async def on_ready():
	print(f"{bot.user.name} is connected !")

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("⚠️ Your command is missing one or more arguments.")
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send("❌ thos command does not exist.")
	else:
		raise error

@bot.event
async def on_raw_reaction_add(payload):
	last_announces = bot.get_channel(ANNOUNCE_CHANNEL).history(limit=15)
	async for anc in last_announces:
		if payload.message_id == anc.id:
			if str(payload.emoji.name) == EMOJI:
				guild = bot.get_guild(payload.guild_id)
				if guild is not None:
					member = guild.get_member(payload.user_id)
					if member is not None and not member.bot:
						if "👽 Rôle :" in anc.content:
							ligne = anc.content.split("\n")
							role = discord.utils.get(guild.roles, name=ligne[2])
							if role:
								await member.add_roles(role)
								print(f"✅ Rôle '{role.name}' ajouté à {member.name}")
								return 

@bot.event
async def on_raw_reaction_remove(payload):
	last_announces = bot.get_channel(ANNOUNCE_CHANNEL).history(limit=15)
	async for anc in last_announces:
		if payload.message_id == anc.id:
			if str(payload.emoji.name) == EMOJI:
				guild = bot.get_guild(payload.guild_id)
				if guild is not None:
					member = guild.get_member(payload.user_id)
					if member is not None and not member.bot:
						if "👽 Rôle :" in anc.content:
							ligne = anc.content.split("\n")
							role = discord.utils.get(guild.roles, name=ligne[2])
							if role:
								await member.remove_roles(role)
								print(f"❌ Rôle '{role.name}' retiré de {member.name}")
								return 


# ======================== Bot Commmand ======================== #

@bot.command()
@commands.has_permissions(manage_channels=True)
async def delete_category(ctx, *, nom_categorie):
	guild = ctx.guild

	# Recherche de la catégorie
	categorie = discord.utils.find(
		lambda c: c.name.lower() == nom_categorie.lower(),
		guild.categories
	)

	if not categorie:
		await ctx.send(f"❌ Category '{nom_categorie}' unfindable.")
		return

	# Suppression de tous les salons de la catégorie
	for channel in categorie.channels:
		try:
			await channel.delete()
			await ctx.send(f"🗑️ Room suppressed : {channel.name}")
		except Exception as e:
			await ctx.send(f"⚠️ Error deliting room {channel.name} : {e}")

	# Suppression de la catégorie
	try:
		await categorie.delete()
		await ctx.send(f"✅ Catégory suppressed : {categorie.name}")
	except Exception as e:
		await ctx.send(f"⚠️ Error deleting category : {e}")


@bot.command()
async def create_party(ctx, new_party:str, announce_message:str):
	# research of the template
	template = discord.utils.find(lambda c: c.name.lower() == "Template".lower(), ctx.guild.categories)
	if template is None:
		await ctx.send(f"❌ the template category have not been found.")
	else:
		await ctx.send(f"✅ The Category was found : {template.name} (ID: {template.id})")

	role = await ctx.guild.create_role(name=new_party)

	overwrites = {
		ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Nobody can see
		role: discord.PermissionOverwrite(view_channel=True, send_messages=True), # Exept this role
		ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True) # And the guys
	}

	# creation of the new category
	new_category = await ctx.guild.create_category(name=new_party, overwrites=overwrites)

	# Added the new role to the creator of the party
	# await ctx.author.add_roles(role)
	
	# creation of every channel of the new category
	for ch in template.channels:
		if isinstance(ch, discord.TextChannel):
			await ctx.guild.create_text_channel(
				name=ch.name,
				category=new_category,
				overwrites=overwrites,
				position=ch.position,
				topic=ch.topic,
				nsfw=ch.nsfw,
				slowmode_delay=ch.slowmode_delay
			)
		elif isinstance(ch, discord.VoiceChannel):
			await ctx.guild.create_voice_channel(
				name=ch.name,
				category=new_category,
				overwrites=overwrites,
				position=ch.position,
				bitrate=ch.bitrate,
				user_limit=ch.user_limit
			)
		elif isinstance(ch, discord.ForumChannel):
			# 📋 Copy the FAQ channel tags from the template
			tags = [
				discord.ForumTag(
					name=tag.name,
					emoji=tag.emoji,
					moderated=tag.moderated
				) for tag in ch.available_tags
			]
			await ctx.guild.create_forum(
				name=ch.name,
				category=new_category,
				available_tags=tags,
				default_sort_order=ForumOrderType.latest_activity,
				default_layout=ch.default_layout
			)
		if (ch.name == "inventaire"):
			await ctx.send("test")

	newParty_prompt:str = "🎉🎉 Nouvelle Soirée 🎉🎉 :\n👽 Rôle :\n" + role.name + "\n" + announce_message
	await bot.get_channel(ANNOUNCE_CHANNEL).send(newParty_prompt)
	last_msg_anc = [msg async for msg in bot.get_channel(ANNOUNCE_CHANNEL).history(limit=1)][0]
	await last_msg_anc.add_reaction(EMOJI)
	await bot.process_commands(last_msg_anc)

@bot.command()
async def clear_channel(ctx):
	try:
		await ctx.channel.purge()
	except Exception as e:
		await ctx.send(f"Error during the suppresion : {e}")


bot.run(os.getenv('BEBER_AVOUV_TOKEN'))