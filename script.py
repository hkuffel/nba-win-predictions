import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression

df = pd.read_csv('player_stats_1976-2019.csv', encoding = "UTF-8")

idx = []
for i in range(1, len(df)):
    if df.at[i,'Player'] == df.at[(i-1),'Player']:
        idx.append(i)
df = df.drop(idx)

players_next_season = df.loc[df['year'] == 2019]

def find_peers(player):
    player_row = players_next_season.loc[players_next_season['Player'] == player]
    age = player_row['Age'].item()
    peers = df.loc[df['Age'] == age].reset_index(drop=True)
    return peers

def find_comps(player):
    df = find_peers(player)
    # saving each player season with its index to refer to later
    ids_ = df[['Player', 'year']]
    
    # Removing unwanted columns and creating a cosine similarity matrix
    df = df.drop(['Player', 'Tm', 'year'], axis = 1)
    df = pd.get_dummies(df, columns = ['Pos'])
    cs = cosine_similarity(df)
    
    # Extracting the top 300 similarity scores for the player in question
    comps = []
    idx = ids_.loc[ids_['Player'] == player].index[0]
    scores = pd.Series(cs[idx]).sort_values(ascending = False)
    top_300 = list(scores.iloc[1:301].index)
    
    # Finding the name, year and score for each of the top 300 and adding to list
    for i in top_300:
        if ids_.loc[i][0] != player:
            comps.append((ids_.loc[i][0], ids_.loc[i][1], round(scores.loc[i], 5)))
    return comps


def predict(player, bpm):
    x, y = [], []
    
    # collecting the BPM for each comp, as well as the BPM for the next year (if possible)
    for comp in find_comps(player):
        try:
            year2 = df.loc[(df['Player'] == comp[0]) & (df['year'] == (comp[1]+1))]
            year1 = df.loc[(df['Player'] == comp[0]) & (df['year'] == comp[1])]
            y.append(year2[bpm].item())
            x.append(year1[bpm].item())
        except:
            pass
    
    # converting from a list to a numpy array
    x = np.array(x)
    x = x.reshape(-1, 1)
    y = np.array(y)
    
    # fitting a regression model and predicting next year's BPMs
    # These predictions are just for the purpose of visualization
    reg = LinearRegression().fit(x,y)
    y_pred = reg.predict(x)
    
    # Predicting next year's BPM for the player in question
    previous_row = df.loc[(df['Player'] == 'Derrick Rose') & (df['year'] == 2019)]
    previous_bpm = previous_row[bpm].item()
    minutes = previous_row['MP'].item()
    bpm_pred = round(reg.predict(np.array(previous_bpm).reshape(-1,1)).item(),5)
    
    return bpm_pred, minutes

def team_eval(team):
    opms, dpms = [], []
    for p in team:
        obpm_pred, minutes = predict(p, 'OBPM')
        dbpm_pred = predict(p, 'DBPM')[0]
        opms.append(obpm_pred)
        dpms.append(dbpm_pred)
    team_opm = sum([opm * 0.1417 for opm in opms[:5]]) + sum([opm * 0.0417 for opm in opms[5:10]])
    team_opm += + sum([opm * 0.0167 for opm in opms[11:]])
    team_dpm = sum([dpm * 0.1417 for dpm in dpms[:5]]) + sum([dpm * 0.0417 for dpm in dpms[5:10]])
    team_dpm += + sum([dpm * 0.0167 for dpm in dpms[11:]])

    win_percent = (108 + team_opm)**14 / ((108 + team_opm)**14 + (108 - team_dpm)**14)
    win_percent

    wins = []
    for _ in range(50000):
        record = 0
        for g in range(82):
            toss = np.random.rand()
            if toss <= win_percent:
                record += 1
        wins.append(record)
    win_total = sum(wins) // len(wins)
    
    return win_total

def walkthrough():
    team = []
    print("Hello! Let's start making your team!")
    starters = 5
    while starters > 0:
        p = input("Pick a starter: ")
        if p in players_next_season['Player'].to_list():
            team.append(p)
            starters -= 1
        else:
            print("Hmmm, I'm not sure about him. Did you spell it right?")
    backups = 10
    while backups > 0:
        p = input("Pick a backup: ")
        if p in players_next_season['Player'].to_list():
            team.append(p)
            backups -= 1
        else:
            print("Hmmm, I'm not sure about him. Did you spell it right?")
    print("Alright, you have your team! Brb, crunching numbers.")
    print(f'The numbers have been crunched! Your team will win {team_eval(team)} games this season. Good luck!')

walkthrough()