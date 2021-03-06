from fastai.collab import *
from fastai.tabular.all import *
from pathlib import Path
path = Path()
    
def create_params(size):
    return nn.Parameter(torch.zeros(*size).normal_(0, 0.01))

# @st.experimental_memo(ttl=24*60*60)
def most_similar_games(gamename, m, selectedmodel):
    model = m.modelstandard if selectedmodel == 'standard' else m.modeltransform
    
    gameidx = m.games.o2i[gamename]
    distances = nn.CosineSimilarity(dim=1)(model.game_factors, model.game_factors[gameidx][None])
    idx = distances.argsort(descending=True)
    gamesdf = m.df.copy()
    gamesdf['similarity'] = distances.detach().numpy().copy()
    return gamesdf.iloc[idx.numpy()]

def most_similar_users(username, n=10):
    idx = users.o2i[username]
    distances = nn.CosineSimilarity(dim=1)(m.user_factors, m.user_factors[idx][None])
    idx = distances.argsort(descending=True)[:n]
    return users[idx]


def get_user_best_unseen(user, verbose=False):
    user_reviews = experienced_ratings.loc[experienced_ratings['user']==user]
    if verbose:
        print('num ratings', len(user_reviews))
    best = get_user_best(user)
    if verbose:
        for idx, name in enumerate(best):
            if name not in seen:
                print(idx, name, name in seen)
            else:
                print(idx, name, user_reviews.loc[user_reviews['name']==name]['rating'].values)
    return [name for name in best if name not in seen]

def gameid(gamename):
    return games.o2i[gamename]

def search_game(gamename):
    return [(name, idx) for idx, name in enumerate(games) if gamename in name]
def search_user(username):
    return [(name, idx) for idx, name in enumerate(users) if username in name]

def get_user_preds(user, m, selectedmodel):
    user_idx = m.users.o2i[user]
    
    model = m.modelstandard if selectedmodel == 'standard' else m.modeltransform

    preds = ((model.user_factors[user_idx] * model.game_factors).sum(dim=1) + model.game_bias + model.user_bias[user_idx])
    preds = sigmoid_range(preds, 0,11)
    user_preds = m.df.copy()
    user_preds['preds'] = preds.detach().numpy().clip(1,10)
    user_preds.sort_values('preds', ascending=False, inplace=True)
    
    return user_preds

def get_user_best(user, n=100):
    preds = get_user_preds(user)
    best_idx = preds.argsort(descending=True)[0:n]
    return games[best_idx]

def get_game_preds(game):
    if isinstance(game,int):
        game_idx = game
    else:
        game_idx = gameid(game)

    preds = ((m.game_factors[game_idx] * m.user_factors).sum(dim=1) + m.user_bias + m.game_bias[game_idx])
    preds = sigmoid_range(preds, 0,11)
    best_idx = preds.argsort(descending=True)[0:10]
    # print(preds.sort(descending=True)[0:10])
    users[best_idx]
    return preds



