import requests
import discord
from discord.ext import commands

# Base API URL
BASE_URL = "https://api.bloxybet.com:443"
SOCKET_IO_URL = f"https://api.bloxybet.com/socket.io/?EIO=4&transport=polling&t=PDtdDSq"

# Intents and bot setup
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Precision Prediction Logic
def main_prediction(game_data):
    """
    Primary precision prediction logic based on balance thresholds.
    """
    try:
        balance_amount = game_data.get("balance", {}).get("current", 0)
        if balance_amount > 1375:
            return "🎯 **Prediction**: tails (High confidence - High balance range)"
        elif 1350 <= balance_amount <= 1375:
            return "🎯 **Prediction**: heads (Medium confidence - Balance in mid-range)"
        else:
            return "🎯 **Prediction**: tails (Low balance, fallback to tails)"
    except Exception as e:
        return f"⚠️ Error in main prediction logic: {str(e)}"

# Backup Precision Prediction Logic
def backup_prediction(game_data):
    """
    Backup prediction logic using odd/even balance calibration and dynamic thresholds.
    """
    try:
        balance_amount = game_data.get("balance", {}).get("current", 0)
        if balance_amount % 2 == 0:
            if balance_amount > 1350:
                return "🔄 **Backup Prediction**: heads (Even balance favors heads - Calibrated)"
            else:
                return "🔄 **Backup Prediction**: tails (Even balance, low range favors tails)"
        else:
            if balance_amount > 1370:
                return "🔄 **Backup Prediction**: tails (Odd balance favors tails in high ranges)"
            else:
                return "🔄 **Backup Prediction**: heads (Odd balance, low range favors heads)"
    except Exception as e:
        return f"⚠️ Error in backup prediction logic: {str(e)}"

# Third Prediction Logic (Based on Game ID's Last 2-3 Characters)
def third_prediction(game_id):
    """
    Third prediction logic using the last 2-3 characters of the Game ID.
    """
    try:
        last_chars = game_id[-3:]
        response = "🔮 **Third Prediction**: "
        if last_chars.isnumeric():
            last_num = int(last_chars) % 2
            if last_num == 0:
                return response + "heads (Even numeric characters favor heads)"
            else:
                return response + "tails (Odd numeric characters favor tails)"
        elif last_chars.isalpha():
            vowels = "aeiouAEIOU"
            vowel_count = sum(1 for char in last_chars if char in vowels)
            if vowel_count >= 2:
                return response + "heads (Vowel-dominant favors heads)"
            else:
                return response + "tails (Consonant-dominant favors tails)"
        else:
            last_digit = next((char for char in last_chars[::-1] if char.isdigit()), "0")
            last_digit = int(last_digit) % 2
            if last_digit == 0:
                return response + "heads (Mixed but even numeric tilt)"
            else:
                return response + "tails (Mixed but odd numeric tilt)"
    except Exception as e:
        return f"⚠️ Error in third prediction logic: {str(e)}"

# Fetch game data for a specific game ID
def fetch_game_data(game_id):
    """
    Fetches data for a specific game using its ID.
    """
    try:
        response = requests.get(f"{SOCKET_IO_URL}/{game_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching game data: {str(e)}"}

# Global flag to track if bot is awaiting Game IDs
awaiting_game_ids = False

# Command to start the game prediction loop
@bot.command(name="random")
async def start_prediction(ctx):
    """
    Handles the !random command to start accepting Game IDs for predictions.
    """
    global awaiting_game_ids
    awaiting_game_ids = True
    await ctx.send("🎲 **Prediction Mode Activated!** 🎲\n"
                   "Please provide Game IDs one by one. I will predict for each Game ID.\n"
                   "Type `!stop` to exit prediction mode.")

# Event listener to accept Game IDs
@bot.event
async def on_message(message):
    global awaiting_game_ids

    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Handle stopping the prediction loop
    if message.content.strip() == "!stop" and awaiting_game_ids:
        awaiting_game_ids = False
        await message.channel.send("🛑 **Prediction Mode Stopped!** 🛑")
        return

    # Process Game IDs when in prediction mode
    if awaiting_game_ids:
        game_id = message.content.strip()
        game_data = fetch_game_data(game_id)

        if "error" in game_data:
            await message.channel.send(f"⚠️ {game_data['error']}")
            return

        # Generate predictions
        main_pred = main_prediction(game_data)
        backup_pred = backup_prediction(game_data)
        third_pred = third_prediction(game_id)

        # Send the predictions
        response = (
            f"🎮 **Game Predictions** 🎮\n"
            f"- **Game ID**: {game_id}\n"
            f"{main_pred}\n"
            f"{backup_pred}\n"
            f"{third_pred}"
        )
        await message.channel.send(response)
    else:
        # Process bot commands
        await bot.process_commands(message)

# Run the bot
TOKEN = "MTMxODQ5MzY3MzQ5MDc0MzMxNg.GwKPcd.Lx4dZKT8qIer4HLdwjWx-IGoenzOyvydjRB39M"  # Replace with your bot's token
bot.run(TOKEN)
