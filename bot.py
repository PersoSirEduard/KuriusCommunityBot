import discord
from spellchecker import SpellChecker
from num2words import num2words

intents = discord.Intents.default()
intents.presences = True
intents.members = True
client = discord.Client(intents=intents)

spell = SpellChecker()
cities = []

voting = False
focus_channel = False
votes = {}

TOKEN = ''

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord.')

	# Extract cities from file
	with open("cities.txt") as f:
		for line in f:
			cities.append(line.strip())
	spell.known(cities) # Add cities to the spellchecker

@client.event
async def on_message(message):

	global voting
	global focus_channel
	global votes

	if message.author == client.user: return # Ignore self messages
	
	# Admin commands
	if hasAuthority(message.author):

		# Setup channel
		if message.content.startswith("!setupchannel"):
			focus_channel = message.channel.id
			await message.channel.edit(topic="City Guesser Activity")
			print("Channel setup")
			return
			# await message.channel.set_permissions(message.guild.default_role, send_messages=False)

		if focus_channel and message.channel.id == focus_channel:
			if message.content.startswith("!newround"):
				if voting: return
				voting = True
				print("New round started")
				await message.channel.send("Starting a new round! Please vote.")
				votes = {}
				return
			
			if message.content.startswith("!endround"):
				if not voting: return
				voting = False
				print("Round ended")
				# Get the top 3 votes
				top_votes = getTopVotes(3)
				await message.channel.send("Did you vote? Well, it's too late now. The round ended.")

				response = "**The top 3 votes were:**\n"
				for i in range(len(top_votes)):
					response += f":{num2words(i+1)}:. {top_votes[i]['title']} with {top_votes[i]['count']} votes\n"
				await message.channel.send(f"**The top 3 votes are**:\n1️⃣ {top_votes[0]['title']} ({top_votes[0]['count']} votes)\n2️⃣ {top_votes[1]['title']} ({top_votes[1]['count']} votes)\n3️⃣ {top_votes[2]['title']} ({top_votes[2]['count']} votes)")
				return

	if focus_channel and voting and message.channel.id == focus_channel:
		vote = sanitizeVote(message) # Get the sanitized vote

		# Check if the vote is a valid city
		vote = isCity(vote)
		if not vote:
			await message.add_reaction("❌")
			return

		# Erase previous vote if applicable
		if didVote(message.author):
			eraseVote(message.author)

		# Add vote
		if vote in votes:
			votes[vote].append(message.author.id)
		else:
			votes[vote] = [message.author.id]

		# Confirm vote with a reaction
		await message.add_reaction("✅")

def hasAuthority(user):
	return "Kurius Executive" in [role.name for role in user.roles]

def didVote(user):
	return user.id in votes.values()

def eraseVote(user):
	for vote in votes:
		if user.id in votes[vote]:
			votes[vote].remove(user.id)

def getTopVote():
	top_vote = None
	top_vote_count = 0

	for vote in votes:
		if len(votes[vote]) > top_vote_count:
			top_vote = vote
			top_vote_count = len(votes[vote])

	return (top_vote, top_vote_count)

def getTopVotes(num):
	top_votes = []
	
	for i in range(num):
		if len(votes) == 0: break
		top_vote_title, top_vote_count = getTopVote()
		top_votes.append({"title": top_vote_title, "count": top_vote_count})
		del votes[top_vote_title]

	return top_votes

def sanitizeVote(string):
	string = " ".join(string.content.lower().split()) # Lower and remove extra spaces
	# Remove accents
	string = string.replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ô", "o").replace("î", "i").replace("û", "u")
	string = "".join(filter(str.isalnum, string)) # Remove non-alphanumeric characters
	string = string.capitalize() # Capitalize first letter
	return string

def isCity(string):
	prediction = spell.correction(string)
	if prediction in cities:
		return prediction
	else:
		return False

if __name__ == '__main__':
	client.run(TOKEN)