#!/usr/bin/python3

import discord
import json
from sb_commandcenter import *
import sb_command_funcs as funcs
import mysql.connector
from sb_command import Command
from sb_channelcommand import ChannelCommand
from sb_constants import *
from sb_db.accessor import DBAccessor
import sys

SECRET_CONFIG_FILE = './super_secret_config.json'

NSA_IS_WATCHING = {}

TEST_MODE = len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test")

command_prefix = "8!"

if TEST_MODE:
    command_prefix = "7!"

with open(SECRET_CONFIG_FILE) as json_file:  
    NSA_IS_WATCHING = json.load(json_file)

db_accessor = DBAccessor(NSA_IS_WATCHING["db_host"], NSA_IS_WATCHING["db_name"], NSA_IS_WATCHING["db_user"], NSA_IS_WATCHING["db_pass"])

client = discord.Client() 

command_center = CommandCenter(db_accessor, client)
command_center.register_command(Command(       "help",         funcs.help))
command_center.register_command(ChannelCommand("register",     funcs.register))
command_center.register_command(Command       ("update",       funcs.update))
command_center.register_command(ChannelCommand("playerlist",   funcs.player_list))
command_center.register_command(Command(       "profile",      funcs.profile))
command_center.register_command(ChannelCommand("whois",        funcs.who_is))
command_center.register_command(Command(       "iplay",        funcs.i_play))
command_center.register_command(Command(       "imain",        funcs.i_main))
command_center.register_command(Command(       "ipocket",      funcs.i_pocket))
command_center.register_command(ChannelCommand("whoplays",     funcs.who_plays))
command_center.register_command(ChannelCommand("olimariscool", funcs.olimar_is_cool))

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="{}help for commands".format(command_prefix)))
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    channel = message.channel
    author = message.author
    
    if author == client.user:
        return

    if(not message.content.startswith(command_prefix)):
        return

    command_string = message.content[len(command_prefix):].strip()
    # override message content with sanitized input
    message.content = command_string
    command_name =  message.content.split(' ')[0]
    rc = await command_center.run_command(command_name, client, message)

    if(rc == RC_COMMAND_DNE):
        await channel.send("Command not recognized, {}".format(author.mention))
    elif(rc == RC_CHANNEL_ONLY):
        await channel.send("That command only works in channels.")


token = NSA_IS_WATCHING["discord_token"]
if TEST_MODE:
    token = NSA_IS_WATCHING["test_token"]

client.run(token)