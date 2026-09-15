# -*-coding:utf8;-*-
# qpy:2
# qpy:console
"""
A set of queries used by various files within the subban library against the database.
"""
# Choose working directory.
from .nhl_data_models import Games
import time, datetime
import numpy as np

#Define the number of teams.
num_teams = 32

###################
# Time Conversion #
###################


def epochtime(datetime_obj):
    """
    Convert time in MON DAY YEAR format to a UNIX timestamp

    Input: datetime object (datetime.game_datetime)
    Output: Unix timestamp
    """
    return time.mktime(datetime_obj.timetuple())


def prettytime(timestamp):
    """
    Convert time since epoch to date
    Input: Unix timestamps
    Output: a datetime object (datetime.game_datetime)
    """
    return datetime.game_datetime.fromtimestamp(timestamp)


#####################
# String Conversion #
#####################


def team_abbreviation(team_alphabetical_id):
    """
    Converts team numerical ids into team names.
    """
    from .nhl_data_models import Teams

    s_query = Teams.select(Teams.abbreviation).where(
        Teams.id == team_alphabetical_id
    )
    s_result = s_query[0]
    return s_result.abbreviation

def full_name_from_abbrev(abbreviation):
    """
    Converts team numerical ids into team names.
    """
    from .nhl_data_models import Teams

    #quick fix
    if abbreviation == "UTA":
        abbreviation = "ARI"
        #print("this code is accesssed")


    s_query = Teams.select(Teams.team_name).where(
        Teams.abbreviation == abbreviation
    )
    
    try:
        s_result = s_query[0]
        name = s_result.team_name
    except IndexError:
        print(abbreviation+" not in list")
        name = ""
    return name

def full_name_to_id(full_team_name):
    """
    Converts 'normal team names', provides the rest of the data needed for processing
    Team id

    Input: a string representing the team's name
    Output: a team id - 1=ATL, 30=WAS

    """
    # Adjusting for previous team names/previous team locations.
    
    if full_team_name == "Phoenix Coyotes" or full_team_name == "Utah Hockey Club" or full_team_name == "Utah Mammoth":
        full_team_name = "Arizona Coyotes"
    if full_team_name == "Atlanta Thrashers":
        full_team_name = "Winnipeg Jets"
    if full_team_name == "Mighty Ducks of Anaheim":
        full_team_name = "Anaheim Ducks"


    # Faut qu'on soit correcte - check this later.
    #if full_team_name == "Montreal Canadiens":
    #    full_team_name = "Montréal Canadiens"


    from .nhl_data_models import Teams

    #print(full_team_name+"query")
    s_query = Teams.select(Teams.id).where(
        Teams.team_name == full_team_name
    )

    s_result = s_query[0]
    return s_result.id


def abbrev_to_id(team_abbrev):
    """
    Converts 'normal team names', provides the rest of the data needed for processing
    Team id
    Input: team abbreviation e.g. "WAS"
    Output: numerical id e.g. "30"
    """
    from .nhl_data_models import Teams

    s_query = Teams.select(Teams.id).where(
        Teams.current_abbreviation == team_abbrev
    )
    s_result = s_query[0]
    return s_result.id


def id_to_name(team_id):
    """
    Converts a team id to a full team name.
    Input: team id e.g. "30"
    Output: team name e.g. "Washington Wizards"
    """
    from .nhl_data_models import Teams

    s_query = Teams.select(Teams.team_name).where(
        Teams.id == team_id
    )
    s_result = s_query[0]
    return s_result.team_name


################################
# Getting Information On Gamess #
################################


def games_query(start_datetime, end_datetime):
    """
    Input: datetime objects
    Output: [visitor_team, visitor_g, home_team, home_g] list
    """
    start_epochtime = epochtime(start_datetime)
    end_epochtime = epochtime(end_datetime)
    played_games = (
        Games.select()
        .where(
            (Games.game_datetime < end_epochtime) &
            (Games.game_datetime > start_epochtime) &
            ((Games.home_g > 0) | (Games.visitor_g > 0))
            #Internal note - here you need a visitor_g or home_g is not zero statement
        )
        .order_by(Games.game_datetime)
    )

    played_games = [
        [g.visitor_team_id, g.visitor_g, g.home_team_id, g.home_g] for g in played_games
    ]
    return played_games


def season_query(season_year):
    """
    Input: a season year
    Output: [visitor_team, visitor_g, home_team, home_g, epochtime, season_year] list
    """

    played_games = (
        Games.select()
        .where(Games.season_year == season_year, Games.visitor_g > 0)
        .order_by(Games.game_datetime)
    )

    played_games = [
        [
            g.visitor_team_id,
            g.visitor_g,
            g.home_team_id,
            g.home_g,
            g.game_datetime,
            season_year,
        ]
        for g in played_games
    ]

    return played_games


def games_won_query(played_games, return_format="list"):
    """
    Input: [visitor_team, visitor_g, home_team, home_g] list
    Output: a list of lists, a list, or a matrix
    """
    winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
    winrows = []
    if return_format == "list_of_lists":
        winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
        winrows = []
        for i in range(1, 31):
            winrows.append([winlist.count(i)])
        return_value = winrows
    elif return_format == "list":
        winlist = [x[0] if x[1] > x[3] else x[2] for x in played_games]
        winrows = []
        for i in range(1, 31):
            winrows.append(winlist.count(i))
        return_value = winrows
    elif return_format == "matrix":
        win_matrix = np.zeros((num_teams, num_teams))
        for x in played_games:
            if x[1] > x[3]:
                win_matrix[x[0] - 1, x[2] - 1] += 1
            elif x[3] > x[1]:
                win_matrix[x[2] - 1, x[0] - 1] += 1
        return win_matrix
    else:
        print("invalid option")
        return_value = 0
    return return_value


def future_games_query(season_datetime, season_year):
    """
    Returns all games past a given datetime for a given season
    including games on that date.
    Inputs: season_datetime, a datetime object
        season_year, the year the season ends in
    Outputs: pending games past that date as a list of away team,
    home team pairs
    """
    season_epochtime = epochtime(season_datetime)
    query = Games.select().where(
        Games.game_datetime >= season_epochtime, Games.season_year == season_year
    )
    matches = [[x.visitor_team_id, x.home_team_id] for x in query]
    return matches


def form_query(team_id):
    """
    Return the form in the last five games for the given team


    Parameters
    ----------
    team_id : standard integer id

    Returns
    -------
    A string representing the current form of the team

    """
    import os

    os.system("")  # required to trigger colouring of text
    COLOR = {
        "HEADER": "\033[95m",
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "YELLOW": "\033[93m",
        "ENDC": "\033[0m",
    }
    q = Games.select().where(
        ((Games.visitor_team_id == team_id) | (Games.home_team_id == team_id))
        & (Games.visitor_g > 0 | Games.home_g > 0)
    )
    x = [[z.visitor_team_id, z.visitor_g, z.home_team_id, z.home_g, z.game_decided_by] for z in q[-5:]]
    winstring = ""
    for g in x:
        if g[4] != "Regulation":
            winstring += COLOR["YELLOW"] + "T" + COLOR["ENDC"]
        elif g[1] > g[3]:
            if g[0] == team_id:
                winstring += COLOR["GREEN"] + "W" + COLOR["ENDC"]
            else:
                winstring += COLOR["RED"] + "L" + COLOR["ENDC"]
        elif g[3] > g[1]:
            if g[0] == team_id:
                winstring += COLOR["RED"] + "L" + COLOR["ENDC"]
            else:
                winstring += COLOR["GREEN"] + "W" + COLOR["ENDC"]
    return winstring


#############################################
# Getting ratings for a given team
#############################################
def team_elo_rating(team_id, epochtime):
    """
    Get the most recent Elo rating for a team given a date and the team_id

    Parameters
    ----------
    team_id : integer team ID 1-30
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    rtg : most recent Elo rating

    """

    from .nhl_data_models import TeamEloData

    rtg_iterable = (
        TeamEloData.select()
        .where(TeamEloData.team_id == team_id, TeamEloData.datetime <= epochtime)
        .order_by(TeamEloData.datetime.desc())
        .limit(1)
    )
    rtg = [x.elo_rating for x in rtg_iterable]
    rtg = rtg[0]
    return rtg


def elo_ratings_list(epochtime):
    """


    Parameters
    ----------
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    ratings_list : list of most recent team ratings to date

    """
    ratings_list = []
    for i in range(1, 33):
        ratings_list.append(team_elo_rating(i, epochtime))
    return ratings_list
    

def new_team_srs_rating(team_id, epochtime):
    
    """
    Get the most recent srs rating for a team given a date and the team_id

    Parameters
    ----------
    team_id : integer team ID 1-30
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    rtg : most recent srs rating

    """

    from .nhl_data_models import SRS

    rtg_iterable = (
        SRS.select()
        .where(SRS.team_id == team_id, SRS.epochtime<= epochtime)
        .order_by(SRS.epochtime.desc())
        .limit(1)
    )
    rtg = [x.srs_rating for x in rtg_iterable]
    #print(rtg)
    try:
        rtg = rtg[0]
        return rtg
    except IndexError as e:
        print("ratings don't exist for team "+str(team_id))
        return 0


def new_srs_ratings_list(epochtime):
    """
    Parameters
    ----------
    epochtime : Unix time in seconds since epoch

    Returns
    -------
    ratings_list : list of most recent team ratings to date

    """
    ratings_list = []
    for i in range(1, 31):
        ratings_list.append(new_team_srs_rating(i, epochtime))
    return ratings_list
    


