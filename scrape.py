import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def stattaboy(year, stattype):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_{stattype}.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]
    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    return pd.DataFrame(player_stats, columns=headers)

def merge_frames(frame, aframe):
    aframe = aframe.drop('Player', axis = 1)
    aframe = aframe.drop('Pos', axis = 1)
    aframe = aframe.drop('Age', axis = 1)
    aframe = aframe.drop('Tm', axis = 1)
    aframe = aframe.drop('G', axis = 1)
    aframe = aframe.drop('MP', axis = 1)
    aframe= aframe.drop('\xa0', axis = 1)
    df = frame.join(aframe)
    return df

def yearsonyears(years):
    df = pd.DataFrame()
    for year in years:
        frames = [stattaboy(year, 'totals'), stattaboy(year, 'advanced')]
        year_df = merge_frames(frames[0], frames[1])
        year_df['year'] = [f'{year}'] * len(year_df)
        df = df.append(year_df, ignore_index = True)
        df = df.dropna()
    return df

df = yearsonyears(np.arange(2000,2020,1))

cols = df.columns.to_list()
cols.remove('Player')
cols.remove('Pos')
cols.remove('Tm')
cols.remove('year')

for col in cols:
    df[col] = pd.to_numeric(df[col], errors = 'coerce')

df = df.dropna()

df.to_csv('player_stats_2000-2019.csv', index=False)