import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# Function to scrape statistics from Basketball Reference into a DataFrame
def get_stats(year, stattype):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_{stattype}.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]
    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    return pd.DataFrame(player_stats, columns=headers)

# Function to merge together two dataframes, tailored to our specific use case
def merge_frames(frame, aframe):
    aframe = aframe.drop(['Player', 'Pos', 'Age', 'Tm', 'G', 'MP', '\xa0'], axis = 1)
    df = frame.join(aframe)
    return df

# Function to stack the merged dataframes on top of each other for a range of years
def yearsonyears(years):
    df = pd.DataFrame()
    for year in years:
        frames = [get_stats(year, 'totals'), get_stats(year, 'advanced')]
        year_df = merge_frames(frames[0], frames[1])
        year_df['year'] = [f'{year}'] * len(year_df)
        df = df.append(year_df, ignore_index = True)
        df = df.dropna()
    return df

df = yearsonyears(np.arange(1976,2020,1))

# Changing necessary columns to numeric types
cols = df.columns.to_list()
skip_col = ['Player', 'Pos', 'Tm', 'year']
for col in cols:
    if col in skip_col:
        pass
    else:
        df[col] = pd.to_numeric(df[col], errors = 'coerce')

df = df.dropna()
df = df.reset_index(drop = True)

df.to_csv('player_stats_1976-2019.csv', index=False)