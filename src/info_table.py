"""

A script that produces a table of information. Inputs below.
-- start date
-- end date
-- season year (denoted by end)

Output: table (string)

"""
# Standard imports
from datetime import datetime, timedelta

# Third Party Imports
from tabulate import tabulate

# Query imports
from nhl_database.queries import (
    games_query,
    team_abbreviation,
    epochtime,
    elo_ratings_list,
    form_query,
    new_srs_ratings_list
)
from nhl_database.nhl_data_models import Games

# Analytics imports
from analytics.SRS import SRS
from analytics.pythag import league_pythagorean_wins
# Wins script import
from analytics.wins_script import get_wins

""" # Query Testing
season_year = 2023
#start_datetime = datetime(season_year-1, 9, 1)
analysis_days = input("Please enter the number of days, min 7, to use for analysis. If all, enter -1: ")
    
try:
    analysis_days = int(analysis_days)
except ValueError:
    sys.exit("Invalid value entered, program exiting")
    
    
if analysis_days == -1:
    start_datetime = datetime(2022, 10, 10)
elif analysis_days >= 7:
    start_datetime = datetime.today()-timedelta(days=analysis_days)
else:
    sys.exit("Number of days invalid, program exiting.")
end_datetime = datetime.today()-timedelta(days=1)
#end_datetime = datetime(season_year,5,1) """

def info_table_data(season_year, start_datetime, end_datetime):

    games_list = games_query(start_datetime, end_datetime)

    # Custom SRS calculation options
    max_MOV = 100  # no real max MOV
    home_team_adv = 0
    win_floor = 0

    wins_dict_list = [
        get_wins(i, season_year, start_datetime, end_datetime) for i in range(1, 33)
    ]
    wins_list = [[x["visitor_record"], x["home_record"], x["record"],x["points"],x["pts_pct"]] for x in wins_dict_list]

    # Pythagorean Wins
    lpw_results = league_pythagorean_wins(
        Games,
        mincalcdatetime=epochtime(start_datetime),
        maxcalcdatetime=epochtime(end_datetime),
    )

    srs_list = SRS(
        games_list, max_MOV=max_MOV, home_team_adv=home_team_adv, win_floor=win_floor
    )
    srs_list = new_srs_ratings_list(end_datetime)
    #srs_list = [0 for i in range(1,33)]

    elo_list = elo_ratings_list(epochtime(end_datetime))

    form_list = [form_query(i) for i in range(1, 33)]

    lpw_results.sort(key=lambda x: x[0]) 

    results = list(zip(lpw_results, srs_list, wins_list, elo_list, form_list))

    #print(results)

    results = [
        [x[0][0], x[0][1], x[1], x[2][0], x[2][1], x[2][2], x[3], x[2][3], x[2][4], x[4]] for x in results
    ]

    results_tuples = [
        (
            team_abbreviation(x[0]),
            round(x[1], 0),
            round(x[2] * 100.0 / 100.0, 3),
            x[6],
            x[3],
            x[4],
            x[5],
            x[7],
            round(x[8],3),
            x[9],
        )
        for x in results
    ]

    results_tuples.sort(key=lambda x: -x[2]) #formerly x[8], otherwise will return alphabetical sort
    return results_tuples

def print_results_table(results_tuples):
    results_table = tabulate(
        results_tuples,
        headers=[
            "Team",
            "Pythag. Wins",
            "Est. SRS",
            "Elo Rating",
            "Away Record",
            "Home Record",
            "Overall Record",
            "Pts",
            "Pts %",
            "Form",
        ],
        tablefmt="rst",
        numalign="left",
    )

    print(
        "Pythagorean Win Expectations, Est. SRS, Elo, and Records \n"
        + "Based on Games Played Between: "
        + start_datetime.strftime("%b %d %Y")
        + " and "
        + end_datetime.strftime("%b %d %Y")
    )
    print(results_table)

if __name__ == "__main__":
    import sys
    season_year = 2026
    start_datetime=datetime(season_year-1,10,1)
    end_datetime = datetime(season_year,5,1)
    a = info_table_data(season_year,start_datetime,end_datetime)
    print_results_table(a)
