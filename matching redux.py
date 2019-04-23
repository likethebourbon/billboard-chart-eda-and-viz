import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from IPython.display import clear_output
pd.set_option('max_colwidth', 300)

# Load show data
shows = pd.DataFrame()
for show in 'stranger things', 'goldbergs', 'glow', 'americans':
    for season in 's1', 's2':
        dx = pd.read_excel('show data.xlsx', sheet_name=f'{show} {season}')
        dx['show'] = f'{show}{season}'
        shows = shows.append(dx, sort=False, ignore_index=True)

# Load hot-100 charts
database = pd.read_csv('hot 100.csv').drop('Unnamed: 0', axis=1)
database.columns = ['Week', 'Title', 'Artist',
                    'PeakPos', 'LastPos', 'Weeks', 'Rank', 'IsNew']

# Create tuples for fuzzy matching in both DFs
shows['pair'] = list(zip(shows.Artist, shows.Title))
database['pair'] = list(zip(database.Artist, database.Title))


# Feel free to comment out either method below, or run them both to compare results


# Method 1: find artist and title matches separately
matches = []
i = 1

# Find artist matches, and then songs by given artists that match
# Only add songs to the results if the title is above the defined threshold
for artist, title in shows.pair:
    temp_dict = {}
    temp_dict['Artist'] = artist
    temp_dict['Title'] = title
    amatch = process.extractBests(str(artist), database.Artist.unique(), limit=10, score_cutoff=64, scorer=fuzz.token_sort_ratio)
    for j, k in enumerate(amatch):
        tmatch = process.extractBests(title, database.loc[database['Artist'] == k[0], 'Title'].unique(), score_cutoff=70, scorer=fuzz.partial_token_sort_ratio)
        n = 1
        for l, m in enumerate(tmatch):
            if m:
                temp_dict[f'Artist score {n}'] = k[1]
                temp_dict[f'Title score {n}'] = m[1]
                temp_dict[f'Match {n}'] = (k[0], m[0])
            n += 1
    matches.append(temp_dict)
    print(f'Songs analyzed: {i}')
    i += 1
    clear_output(wait=True)

# Make a df from the results and order the columns
matchesdf = pd.DataFrame(matches)
cols = ['Artist', 'Title']
for i in range(int((len(matchesdf.columns) - 2) / 3)):
    cols.append(f'Match {i+1}')
    cols.append(f'Artist score {i+1}')
    cols.append(f'Title score {i+1}')

matchesdf = matchesdf[cols]
# matchesdf
matchesdf.to_csv('matches.csv')


# Method 2: search for artist/title tuple matches using the token_sort_ratio scorer
pair_matches = []
i = 1

for song in shows.pair:
    temp_dict = {}
    temp_dict['Query'] = song
    match = process.extractBests(str(song), database.pair.unique(
    ), limit=10, score_cutoff=60, scorer=fuzz.token_sort_ratio)
    for n, result in enumerate(match):
        if result:
            temp_dict[f'Match {n}'] = result[0]
            temp_dict[f'Score {n}'] = result[1]
    pair_matches.append(temp_dict)
    print(f'Songs analyzed: {i}')
    i += 1
    clear_output(wait=True)

pair_matches_df = pd.DataFrame(pair_matches)
cols = ['Query']
for i in range(int((len(matchesdf.columns) - 1) / 2)):
    cols.append(f'Match {i}')
    cols.append(f'Score {i}')
pair_matches_df = pair_matches_df[cols]
# pair_matches_df
pair_matches_df.to_csv('pair matches.csv')
