import requests_html as rh
import json
import pandas as pd



baseUrl = 'https://www.nfl.com'
sess = rh.HTMLSession()

# output = {
#     'players': []
# }

def get_team_routes() -> list:
    """
    Get the team routes from the NFL.com website.
    """

    url = 'https://www.nfl.com/teams/'
    r = sess.get(url)

    table = r.html.find('main#main-content', first = True)
    table_urls = table.find('div.d3-o-media-object__cta')
    team_route_list = [x for x in list(table_urls[0].links) if x.startswith('/teams/')]
    
    return team_route_list

def player_row_cleanse(row: list) -> list:
    """
    Small clean up the player row data from the NFL.com website.
    """

    if not row[1].isdigit():
        row.insert(1, None)
    if not row[2].isalpha():
        row.insert(2, None)
    if not row[3].isalpha():
        row.insert(3, None)
    if not row[4].isdigit():
        row.insert(4, None)
    if not row[5].isdigit():
        row.insert(5, None)
    if not row[6].isdigit():
        row.insert(6, None)
        
    # remove last element (make sure row is 8 elements long)
    while len(row) > 8:
        del row[-1]
    return row


def get_team_roster(team_route: str) -> pd.DataFrame:
    """
    Get the team roster from the NFL.com website.
    """

    team_url = baseUrl + team_route + 'roster' if team_route.endswith('/') else baseUrl + team_route + '/roster'
    team_r = sess.get(team_url)
    
    team_table = team_r.html.find('main#main-content', first = True)
    team_info = team_table.find('div.nfl-c-team-header__info', first = True)
    team_name = team_info.find('div.nfl-c-team-header__title', first = True).element.text
    
    team_roster_div = team_table.find('div.d3-l-col__col-12', first = True)
    team_roster_div = team_roster_div.find('div.nfl-o-roster', first = True)
    
    team_roster_table = team_roster_div.find('table', first = True)
    team_roster_table = team_roster_table.find('tbody', first = True)
    team_roster_table = team_roster_table.find('tr')
    
    # list of lists
    team_roster = [player_row_cleanse(x.find('td')[0].text.split('\n')[0:8]) for x in team_roster_table]
    
    # storing as pd dataframe for now (might need to push list of lists into db)
    team_roster = pd.DataFrame(team_roster, columns = ['name', 'number', 'position', 'status', 'height', 'weight', 'experience', 'college'])
    team_roster['team'] = team_name
    return team_roster

def player_row_to_dict(row: list) -> dict:
    """
    Convert the player row data to a dict.
    """
    d = {
        'name': row[1],
        'jersey_number': row[2],
        'position': row[3],
        'status': row[4],
        'height': row[5],
        'weight': row[6],
        'experience': row[7],
        'college': row[8],
        'team': row[0]
    }
    
    return d

def get_all_team_rosters() -> pd.DataFrame:
    """
    Get all the team rosters from the NFL.com website.
    """
    
    team_routes = get_team_routes()

    # may need to change this to a list of lists (for db)
    team_rosters = [get_team_roster(x) for x in team_routes]
    team_rosters = pd.concat(team_rosters)
    return team_rosters



def get_all_team_rosters_to_dict() -> list:
    """
    Get all the team rosters from the NFL.com website.
    """
    
    team_routes = get_team_routes()

    # may need to change this to a list of lists (for db)
    team_rosters = [get_team_roster(x) for x in team_routes]
    team_rosters = pd.concat(team_rosters)
    team_rosters = team_rosters.to_dict('records')
    return team_rosters