# [username] ________
from model import *
import discord
import json
import difflib

players = []
moves = 0

client = discord.Client()
board_solution_tuple = board_solution_generator()
board_solution = board_solution_tuple[0]
sum_up_to = board_solution_tuple[1]

new_board = Board(board_solution, sum_up_to)
new_game = Game(new_board)

with open("files/profile.json") as profile_file:
    profile = json.load(profile_file)

def reset(): # hacky way to reset, not good practice, mostly because the Player class does not have a 'name'
    global board_solution_tuple
    global board_solution
    global sum_up_to
    global new_board
    global new_game
    global players
    global moves

    players = []
    moves = 0
    board_solution_tuple = board_solution_generator()
    board_solution = board_solution_tuple[0]
    sum_up_to = board_solution_tuple[1]

    new_board = Board(board_solution, sum_up_to)
    new_game = Game(new_board)

@client.event
async def on_ready():
    global client
    game = discord.Game("with my hugs and kisses! :)")
    await client.change_presence(activity=game)
    print(f"{client.user} is ready!")

async def reply(message, content):
    await message.channel.send(f"{message.author.mention}, {content}")

@client.event
async def on_message(message):
    global players
    if message.author == client.user:
        return

    if not message.content.startswith(profile["prefix"]):
        return

    text = message.content[2:].split()

    if len(text) == 2 and text[0] == "force" and len(message.mentions) == 1:
        if message.mentions[0] in players:
            await message.channel.send(f"The player ({message.mentions[0].mention}) you are trying to force is already ingame.")
            return
        if len(players) >= 2:
            await message.channel.send(f"I can't force in {message.mentions[0].mention} 'cause there are too many players!")
            return 

        players.append(message.mentions[0])
        if len(players) == 1:
            new_game.player1.name = message.mentions[0].name
        else:
            new_game.player2.name = message.mentions[0].name
        await message.channel.send(f"I have forced {message.mentions[0].mention} into the game.")
        return

    if len(text) != 1:
        await reply(message, "all commands must consist of one 'word' or 'number'.")
        return
    
    if text[0] == "help":
        with open("files/help.txt") as help_file:
            out = help_file.read()
        await message.channel.send(out.format(prefix=profile["prefix"]))
    
    elif text[0] == "join":
        if message.author in players:
            await reply(message, "you've already joined the game.")
            return
        
        if len(players) >= 2:
            await reply(message, "there are too many players.")
            return 


        players.append(message.author)
        if len(players) == 1:
            new_game.player1.name = message.author.name
        else:
            new_game.player2.name = message.author.name
        await reply(message, "you have joined the game.")
    
    elif text[0] == "stop":
        await reply(message, "sorry, you can't stop the bot which has been deployed!")
    
    elif text[0] == "version":
        await reply(message, "this command is used for ensuring the deployed version is up-to-date. v1.0.1")
    
    elif text[0] == "reset":
        reset()
        await reply(message, "the game has been reset.")
    
    elif text[0] == "board":
        await message.channel.send(new_game.board)
    
    elif text[0] == "players":
        out = "Joined players:\n"
        if len(players) == 0:
            await message.channel.send("No players have joined.")
            return
        for player in players:
            out += player.mention + "\n"
        await message.channel.send(out)
    
    elif text[0] == "start":
        if message.author not in players:
            await reply(message, "you haven't joined the game.")
            return
        
        if len(players) < 2:
            await reply(message, "there aren't enough players.")
            return
        
        try:
            new_game.start()
            await message.channel.send("The game has started!")
            await message.channel.send(new_game.board)
            await message.channel.send(f"It is {players[new_game.current_player.num].mention}'s turn.")
            if new_game.current_player.num == 0:
                await message.channel.send("Their symbol is 💚.")
            else:
                await message.channel.send("Their symbol is ❤️.")
        except Exception as e:
            await reply(message, str(e))

    elif text[0] == "forcestart":
        if len(players) < 2:
            await reply(message, "there aren't enough players.")
            return
        try:
            new_game.start()
            await message.channel.send("The game has started! Player order is the order in which you joined.")
            await message.channel.send(new_game.board)
            await message.channel.send(f"It is {players[new_game.current_player.num].mention}'s turn.")
            if new_game.current_player.num == 0:
                await message.channel.send("Their symbol is 💚.")
            else:
                await message.channel.send("Their symbol is ❤️.")
        except Exception as e:
            await reply(message, str(e))

    
    elif text[0].isdigit() or text[0][0] == "-" and text[0][1:].isdigit():
        if message.author not in players:
            await reply(message, "you haven't joined the game.")
            return
        
        if players.index(message.author) == 0:
            actual_player = new_game.player1
        else:
            actual_player = new_game.player2

        try:
            actual_player.select_square(int(text[0]))
            global moves
            moves += 1
            await message.channel.send(new_game.board)
            has_won = new_game.game_finished()
            if not has_won:
                if moves == len(new_game.board.board_values):
                    await message.channel.send(f"A tie game!")
                    reset()
                    return
                new_game.next_turn()
                await message.channel.send(f"It is {players[new_game.current_player.num].mention}'s turn.")
                if new_game.current_player.num == 0:
                    await message.channel.send("Their symbol is 💚.")
                else:
                    await message.channel.send("Their symbol is ❤️.")
            else:
                if has_won[1] == new_game.player1:
                    await message.channel.send(f"{players[0].mention} has won!")
                    await message.channel.send(f"The winning set was: `{str(has_won[2])}`")
                else:
                    await message.channel.send(f"{players[1].mention} has won!")
                    await message.channel.send(f"The winning set was: `{str(has_won[2])}`")
                reset()
        except Exception as e:
            await message.channel.send(str(e))
    
    else:
        commands = ["force", "help", "join", "start", "stop", "reset", "board", "players", "forcestart"]
        ratio = -1
        actual = ""
        for command in commands:
            if difflib.SequenceMatcher(None, command, text[0]).ratio() > ratio:
                ratio = difflib.SequenceMatcher(None, command, text[0]).ratio()
                actual = command
        out = f"that is an invalid command. Did you mean `{profile['prefix']}{actual}` instead? Type `{profile['prefix']}help` for more information."
        await reply(message, out)

import os
is_production = os.environ.get("token", None)

if not is_production:
    client.run(profile["token"])
else:
    client.run(is_production)

"""
board_solution_tuple = board_solution_generator()
board_solution = board_solution_tuple[0]
sum_up_to = board_solution_tuple[1]

new_board = Board(board_solution, sum_up_to)
new_game = Game(new_board)
players = []
moves = 0

while True:
    author = input("Player: ").lower()
    if author == "stop":
        break
    message = input("Message: ").lower().split()

    if len(message) != 1:
        print(f"All commands must consist of one 'word' or 'number'.")
        continue

    if message[0] == "stop" or author == "stop":
        break

    if message[0] == "join":
        if author in players:
            print(f"You already joined.")
            continue

        if len(players) >= 2:
            print(f"Too many players.")
            continue

        players.append(author)
        print(f"@{author} joined the game.")
    
    if message[0] == "start":
        if author not in players:
            print(f"You haven't joined the game.")
            continue

        if len(players) < 2:
            print(f"Not enough players.")
            continue

        new_game.start()
        print(f"Game has started.")
        print(new_game.board)
    
    if message[0].isdigit():
        if author not in players:
            print(f"You haven't joined the game.")
            continue

        if players.index(author) == 0:
            actual_player = new_game.player1
        else:
            actual_player = new_game.player2

        try:
            actual_player.select_square(int(message[0]))
            moves += 1
            print(new_game.board)
            has_won = new_game.game_finished()
            if not has_won:
                if moves == len(new_game.board.board_values):
                    print(f"A tie game!")
                    break
                new_game.next_turn()
            else:
                if has_won[1] == new_game.player1:
                    print(f"{players[0]} has won!")
                else:
                    print(f"{players[1]} has won!")
                break
        except Exception as e:
            print(e)
"""
