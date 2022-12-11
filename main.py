import pandas as pd
from scrapers.teams import get_all_team_data
from scrapers.players import get_all_team_rosters
from scrapers.players import get_team_routes
from sqlalchemy import create_engine
from decouple import config
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def getSQLConnection():
    """
    Get SQL Connection
    """

    class db_conns:
        engine = create_engine(f'mysql+pymysql://{config("DB_USER")}:{config("DB_PASS")}@{config("DB_HOST")}/{config("DB_NAME")}', echo=False)
        conn = engine.connect()
        cursor = engine.raw_connection().cursor()

    return db_conns

def main():
    """
    Main function
    """

    logging.info('STARTING MAIN FUNCTION')

    df = pd.read_csv('data/team_rosters.csv')
    df = df.rename(columns = {'number': 'jersey_number'})
    print(df.columns)
    df.to_sql('players', getSQLConnection().conn, 'nfl_api', if_exists='append', index=False)

    # print(df)

    # get all team data
    
    # team_data = get_all_team_data(get_team_routes())
    
    # print(team_data)
    
    # team_data.to_sql('teams', getSQLConnection().conn, 'nfl_api', if_exists='append', index=False)
    
    
    # logging.info('COMPLETED PUSH TO TEAMS TABLE')

    # get all team rosters
    # team_rosters = get_all_team_rosters()
    # print(team_rosters)
    # team_rosters.to_sql('players', getSQLConnection(), if_exists='replace', index=False)

def update_teams():
    """
    Update teams table
    """

    logging.info('STARTING UPDATE TEAMS FUNCTION')

    db = getSQLConnection()

    # get all team data
    team_data = get_all_team_data(get_team_routes())

    query = """
        INSERT INTO teams (name, city, website, wins, losses, ties, position, division, coach, stadium, owners, established)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name)
    """

    # TURN TEAMS_DATA INTO A LIST OF TUPLES
    team_data = [tuple(x) for x in team_data.values]

    db.cursor.executemany(query, team_data)

    logging.info('COMPLETED PUSH TO TEAMS TABLE')
    logging.info('ROWS UPDATED: %s', db.cursor.rowcount)

    db.conn.close()

    

def load_players():
    """
    Load players table
    """
    
    logging.info('STARTING LOAD PLAYERS FUNCTION')

    db = getSQLConnection()

    # get all team rosters
    logging.info('GETTING TEAM ROSTERS')
    team_rosters = get_all_team_rosters()
    logging.info('TEAM ROSTERS LOADED')
    

    print('team rosters', team_rosters)

    # get team key to use as foreign key for team column
    logging.info('GETTING TEAM KEYS')
    team_keys = pd.read_sql('SELECT team_key, name FROM teams', db.conn)
    team_keys.rename(columns = {'name': 'team'}, inplace = True)
    logging.info('TEAM KEYS LOADED')

    print('team keys', team_keys)

    
    # merge team keys with team rosters
    logging.info('MERGING TEAM KEYS WITH TEAM ROSTERS')
    team_rosters = pd.merge(team_rosters, team_keys, how='left', on='team')
    team_rosters.drop('team', axis=1, inplace=True)
    logging.info('TEAM KEYS MERGED WITH TEAM ROSTERS')


    # drop team name column
    # team_rosters.drop('name', axis=1, inplace=True)

    team_rosters.to_sql('players', db.conn, if_exists='replace', index=False)

    # logging.info('CONVERTING TO CSV')
    # team_rosters.to_csv('team_rosters.csv', index=False, sep = ',')
    # logging.info('CSV CREATED')


if __name__ == "__main__":
    # load_players()
    main()
    # update_teams()
    # print(getSQLConnection())
