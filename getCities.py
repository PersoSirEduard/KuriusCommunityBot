import pandas as pd

def sanitizeVote(string):
	string = " ".join(string.lower().split()) # Lower and remove extra spaces
	# Remove accents
	string = string.replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ô", "o").replace("î", "i").replace("û", "u")
	string = "".join(filter(str.isalnum, string)) # Remove non-alphanumeric characters
	string = string.capitalize() # Capitalize first letter
	return string

df = pd.read_csv('canadacities.csv')
df = df["city"]

f = open("cities.txt", "w")
for city in df.values:
    f.write(sanitizeVote(city) + "\n")
f.close()



