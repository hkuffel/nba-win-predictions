# 1. import Flask
from flask import Flask, jsonify
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
    plow = player.replace(' ', '').lower()
    prow = players_next_season.loc[players_next_season['Player'].str.replace(' ', '').str.lower() == plow]
    age = prow['Age'].item()
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
    plow = player.replace(' ', '').lower()
    idx = ids_.loc[ids_['Player'].str.replace(' ', '').str.lower() == plow].index[0]
    scores = pd.Series(cs[idx]).sort_values(ascending = False)
    top_300 = list(scores.iloc[1:301].index)
    
    # Finding the name, year and score for each of the top 300 and adding to list
    for i in top_300:
        if ids_.loc[i][0].replace(' ', '').lower() != plow:
            comps.append((ids_.loc[i][0], ids_.loc[i][1], round(scores.loc[i], 5)))
    return comps


def predict(player, bpm):
    plow = player.replace(' ', '').lower()
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
    
    # fitting a regression model
    reg = LinearRegression().fit(x,y)
    
    # Predicting next year's BPM for the player in question
    previous_row = df.loc[(df['Player'].str.replace(' ', '').str.lower() == plow) & (df['year'] == 2019)]
    previous_bpm = previous_row[bpm].item()
    minutes = previous_row['MP'].item()
    bpm_pred = round(reg.predict(np.array(previous_bpm).reshape(-1,1)).item(),5)
    
    return bpm_pred, minutes

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
    f"Welcome to the NBA player API!<br/>"
    f"Available Routes:<br/>"
    f"predict/James%20Harden"
    )

@app.route("/predict/<player>")
def predictify(player):
    d = {player: predict(player, 'OBPM')}
    return f"We predict that {player} will have a OBPM of {d[player][0]} next year, and he'll play {d[player][1]} minutes."

if __name__ == "__main__":
    app.run(debug=True)