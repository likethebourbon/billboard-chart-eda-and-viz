import pandas as pd
from fuzzywuzzy import fuzz
from IPython.display import clear_output

# Load show data
shows = pd.DataFrame()
for show in 'stranger things ', 'goldbergs ', 'glow ', 'americans ':
    for season in 's1', 's2':
        dx = pd.read_excel('show data.xlsx', sheet_name=f'{show}{season}')
        dx['show'] = f'{show}{season}'
        shows = shows.append(dx, sort=False, ignore_index=True)

# Load hot-100 charts
database = pd.read_csv('hot 100.csv').drop('Unnamed: 0', axis=1)
database.columns = ['Week', 'Title', 'Artist', 'PeakPos', 'LastPos', 'Weeks', 'Rank', 'IsNew']

# Create tuples for fuzzy matching in both DFs
shows['pair'] = list(zip(shows.Artist, shows.Title))
database['pair'] = list(zip(database.Artist, database.Title))

# Create fuzzy matching function


def match_name(name, list_names, min_score=0):
    # -1 score incase we don't get any matches
    max_score = -1

    # Returning empty name for no match as well
    max_name = ""

    # Iternating over all names in the other
    for name2 in list_names:

        # Finding fuzzy match score
        score = fuzz.ratio(name, name2)

        # Checking if we are above our threshold and have a better score
        if (score > min_score) & (score > max_score):
            max_name = name2
            max_score = score

    return (max_name, max_score)


# Find (Artist, Title) tuples from the show DF in the hot-100 DF
match_list = []
i = 1
for song in shows.pair.values:
    match = match_name(song, database.pair.values, 50)

    # dict for storing data
    match_dict = {}
    match_dict.update({'Show_Pair': song})
    match_dict.update({'Database_pair': match[0]})
    match_dict.update({'Score': match[1]})
    match_list.append(match_dict)

    # print which pairs have been matched
    print(i)
    i += 1
    clear_output(wait=True)

# Transform the list into a DF
match_df = pd.DataFrame(match_list)
match_df

grouped_df = pd.DataFrame(database.groupby('pair').agg({'Week': 'min', 'Rank': 'min', 'pair': 'count'}))
match_df = match_df.join(grouped_df, on='Database_pair', how='left', rsuffix='_db')
match_df.columns = ['Database_pair', 'Score', 'Show_pair', 'First_week', 'Highest_rank', 'Weeks_on_chart']
shows.join(match_df.set_index('Show_pair').drop_duplicates(keep='first'), on='pair', how='left').to_csv('all matches 2.csv')

