import json
import pandas as pd
import requests_html as rh
from players import get_team_routes


sess = rh.HTMLSession()
baseUrl = 'https://www.nfl.com'
team_routes = get_team_routes()
team_routes = [x + '/' if not x.endswith('/') else x for x in team_routes]

def get_team_city(team_name: str) -> str:
    if len(team_name.split(' ')) > 2:
        return ' '.join(team_name.split(' ')[:-1])
    return team_name.split(' ')[0]  

def get_team_info_standings(r: rh.HTMLResponse) -> object:
    standing = r.html.xpath('//*[@id="main-content"]/div/div/section/div/div/div/div[2]')[0].element.text
    
    
    class return_vals:
        position = standing.split(' ')[0]
        division = " ".join(standing.split(' ')[1:])
    
    return return_vals

def get_team_w_l(r: rh.HTMLResponse) -> object:
    w_l = r.html.xpath('//*[@id="main-content"]/div/div/section/div/div/div/div[3]')[0].element.text
    
    class return_vals:
        wins = int(w_l.split('-')[0])
        losses = int(w_l.split('-')[1])
        tie = int(w_l.split('-')[2])
    
    return return_vals

def get_team_coach_data(r: rh.HTMLResponse) -> object:
    try:
        path = r.html.xpath('//*[@id="main-content"]/section[5]/div/div[1]/div/section/div/div[2]/ul/li')[0]
        
        coach_ = path.find('div.nfl-c-team-info__info-value')[0].element.text
        stadium_ = path.find('div.nfl-c-team-info__info-value')[1].element.text
        owners_ = path.find('div.nfl-c-team-info__info-value')[2].element.text.split(',')[0]
        established_ = int(path.find('div.nfl-c-team-info__info-value')[3].element.text)
        
        class return_vals:
            coach = coach_
            stadium = stadium_
            owners = owners_
            established = established_
        
        return return_vals
    except:
        path = r.html.xpath('//*[@id="main-content"]/section[4]/div/div[1]/div/section/div/div[2]/ul/li')[0]
        coach_ = path.find('div.nfl-c-team-info__info-value')[0].element.text
        stadium_ = path.find('div.nfl-c-team-info__info-value')[1].element.text
        owners_ = path.find('div.nfl-c-team-info__info-value')[2].element.text.split(',')[0]
        established_ = int(path.find('div.nfl-c-team-info__info-value')[3].element.text)
        
        class return_vals:
            coach = coach_
            stadium = stadium_
            owners = owners_
            established = established_
        
        return return_vals

def get_team_info(r: rh.HTMLResponse) -> object:
    team_standings = get_team_info_standings(r)
    team_w_l = get_team_w_l(r)
    team_name = r.html.xpath('//*[@id="main-content"]/div/div/section/div/div/div/div[1]')[0].element.text
    team_city = get_team_city(team_name)
    team_website = r.html.xpath('//*[@id="main-content"]/div/section/div/div/div/ul/li[1]/a')[0].attrs['href']
    coach_data = get_team_coach_data(r)
    
    class return_vals:
        name = team_name
        city = team_city
        website = team_website
        position = team_standings.position
        division = team_standings.division
        wins = team_w_l.wins
        losses = team_w_l.losses
        tie = team_w_l.tie
        coach = coach_data.coach
        stadium = coach_data.stadium
        owners = coach_data.owners
        established = coach_data.established
    
    return return_vals

def get_team_data(team_route: str):
    team_route = team_route + '/' if not team_route.endswith('/') else team_route
    sess = rh.HTMLSession()
    r = sess.get(baseUrl + team_route)
    
    team_data = []

    team_info = get_team_info(r)

    team_data.append({
        'name': team_info.name,
        'city': team_info.city,
        'website': team_info.website,
        'wins': team_info.wins,
        'losses': team_info.losses,
        'tie': team_info.tie,
        'position': team_info.position,
        'division': team_info.division,
        'coach': team_info.coach,
        'stadium': team_info.stadium,
        'owners': team_info.owners,
        'established': team_info.established
    })

    return team_data


def get_all_team_data(team_routes: list) -> pd.DataFrame:
    team_data = []
    for team_route in team_routes:
        team_data.extend(get_team_data(team_route))
    return pd.DataFrame(team_data)