from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

# Define a common User-Agent header
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Scrape anime data
anime_source = requests.get('https://myanimelist.net/topanime.php', headers=headers)
anime_soup = BeautifulSoup(anime_source.content, "html.parser")

anime_animes = anime_soup.select("tr.ranking-list")
anime_names = [i.find('h3').get_text() for i in anime_animes]

anime_score = anime_soup.select("td.score")
anime_scores = [s.get_text() for s in anime_score]
if anime_scores and anime_scores[0] == "Score":
    anime_scores = anime_scores[1:]

anime_details = anime_soup.select("div.information")
anime_detailsText = [t.get_text() for t in anime_details]

anime_episodes_list = []
anime_airtime_list = []
anime_members_list = []

for text in anime_detailsText:
    lines = text.strip().split('\n')
    if len(lines) >= 3:
        episodes = lines[0].strip()
        airTime = lines[1].strip()
        members = lines[2].strip()

        episodes = episodes.split('(')[1].split('eps')[0].strip()
        airTime = airTime.split(' - ')[0].strip()
        members = members.replace(",", "").split()[0].strip()

        anime_episodes_list.append(episodes)
        anime_airtime_list.append(airTime)
        anime_members_list.append(members)

anime_listAnimes = []
for i in range(len(anime_animes)):
    data = {
        "title": anime_names[i],
        "score": anime_scores[i],
        "episodes": anime_episodes_list[i],
        "airtime": anime_airtime_list[i],
        "members": anime_members_list[i],
    }
    anime_listAnimes.append(data)

# Create a DataFrame for anime data
anime_df = pd.DataFrame(anime_listAnimes, columns=['title', 'score', 'episodes', 'airtime', 'members'])

# Scrape game data
game_source = requests.get('https://www.metacritic.com/browse/game/', headers=headers)
game_soup = BeautifulSoup(game_source.content, "html.parser")

game_games = game_soup.select("div.c-finderProductCard")
game_title = [i.find('h3').get_text() for i in game_games]

game_numbers_list = []
game_titles_list = []

for i in game_title:
    match = re.match(r'^(\d+)\.\s+(.*)$', i)
    if match:
        number = match.group(1)
        game_title = match.group(2)
        game_numbers_list.append(number)
        game_titles_list.append(game_title)

game_detail = game_soup.select('div.c-finderProductCard_description')
game_desc = [s.get_text('span') for s in game_detail]

game_rate = game_soup.select('div.c-finderProductCard_meta')
game_dataRatingandDate = [t.find('span').get_text() for t in game_rate]

game_metascore = []

for i in range(1, len(game_dataRatingandDate), 2):
    game_metascore += game_dataRatingandDate[i].strip('Metascore').split('\n')

game_releasedate = []

for i in range(0, len(game_dataRatingandDate), 2):
    game_releasedate += game_dataRatingandDate[i].strip().split('\n')

game_listgames = []
for i in range(len(game_games)):
    data = {
        "Rank": game_numbers_list[i],
        "title": game_titles_list[i],
        "Score": game_metascore[i],
        "ReleaseDate": game_releasedate[i],
        "Desc": game_desc[i],
    }
    game_listgames.append(data)

# Create a DataFrame for game data
game_df = pd.DataFrame(game_listgames, columns=['Rank', 'title', 'Score', 'ReleaseDate', 'Desc'])

# Save both DataFrames to CSV files
anime_df.to_csv('anime.csv', index=False)
game_df.to_csv('game.csv', index=False)

# Read the CSV files into DataFrames
anime_df_read = pd.read_csv('anime.csv')
game_df_read = pd.read_csv('game.csv')

# Print the first few rows of the DataFrames
print("Anime DataFrame:")
print(anime_df_read.head())

print("\nGame DataFrame:")
print(game_df_read.head())