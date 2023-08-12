import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

columns_rename = {
    'MP': 'Matches played',
    'W': 'Wins',
    'D': 'Draws',
    'L': 'Losses',
    'GF': 'Goals for',
    'GA': 'Goals against',
    'GD': 'Goal difference',
    'Pts': 'Points',
    'Pts/MP': 'Points per match played',
    'xG': 'Expected goals',
    'xGA': 'Expected goals allowed',
    'xGD': 'Expected goals difference',
    'xGD/90': 'Expected goals difference per 90 minutes',
    'Last 5': 'Last 5 matches'
}

columns_rename_players = {
    'MP': 'MatchesPlayed',
    'Starts': 'MatchesStarting',
    'Min': 'MinutesPlayed',
    '90s': 'MinutesDividedBy90',
    'Gls': 'Goals',
    'Ast': 'Assists',
    'G+A': 'GoalsAndAssists',
    'G-PK': 'NoPenaltyGoals',
    'PK': 'PenaltyGoals',
    'PKatt': 'PenaltyAttempts',
    'CrdY': 'YellowCards',
    'CrdR': 'RedCards',
    'xG': 'xG-ExpectedGoals',
    'npxG': 'npxG-NoPenaltyExpectedGoals',
    'xAG': 'xAG-ExpectedAssistedGoals',
    'PrgC': 'ProgressiveCarries',
    'PrgP': 'ProgressivePasses',
    'PrgR': 'ProgressivePassesReceived'
}

base_url = 'https://fbref.com'
brazil_league_url = f'{base_url}/en/comps/24/Serie-A-Stats'

base_year = '2023'

# Extraction

def extract_classification(columns_rename, brazil_league_url):
    page = requests.get(brazil_league_url)
    soup = BeautifulSoup(page.text, 'lxml')
    table1 = soup.find('table', id='results2023241_overall')

    headers = []
    for i in table1.find_all('th')[1:16]:
        title = i.text
        headers.append(title)
    
    df = pd.DataFrame(columns = headers)
    df['Squad URL'] = ''

    for j in table1.find_all('tr')[1:]:
        row_data = j.find_all('td')[:15]
    
        row_values = [i.text for i in row_data]
        row_values.append(row_data[0].find('a')['href'])
        length = len(df)
        df.loc[length] = row_values

    renamed_df = df.rename(columns_rename, axis=1)
    return renamed_df

#renamed_df = extract_classification(columns_rename, brazil_league_url)
#renamed_df.to_excel('Classificacao.xlsx')

renamed_df = pd.read_csv('Classificacao.csv')

# Extraction squads
squads_urls = renamed_df['Squad URL'].tolist()

full_squads_urls = [base_url + url for url in squads_urls]

for squad in full_squads_urls:
    page = requests.get(squad)
    soup = BeautifulSoup(page.text, 'lxml')
    table1 = soup.find('table', id='stats_standard_24')

    headers = []
    for i in table1.find_all('th')[7:30]:
        title = i.text
        headers.append(title)
        
    df_squad = pd.DataFrame(columns = headers)

    for j in table1.find_all('tr')[2:-2]:
        player_name = j.find_all('th')[0]['csk']
        row_data = j.find_all('td')[:22]

        row_values = [i.text for i in row_data]
        row_values.insert(0, player_name)

        length = len(df_squad)
        df_squad.loc[length] = row_values


    df_squad_renamed = df_squad.rename(columns_rename_players, axis=1)
    pattern_to_get_squad_name = r"/([^/]+)-Stats$" 
    match = re.search(pattern_to_get_squad_name, squad)
    squad_name = match.group(1)
    #df_squad_renamed.to_excel(f'{squad_name}_standard_stats_2023.xlsx')
    #df_squad_renamed.to_csv(f'{squad_name}_standard_stats_2023.csv')
    
    print(f'Exported data for {squad_name} players!')

print('End of extraction')
