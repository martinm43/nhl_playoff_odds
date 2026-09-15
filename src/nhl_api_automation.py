# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 23:31:39 2023

Updated
@author: Martin Miller
A script for updating data between a given certain amount of dates
"""

import requests
from datetime import datetime, timedelta

from pprint import pprint

from nhl_database.queries import epochtime, full_name_from_abbrev
from nhl_database.nhl_data_models import database, Games

#base_url = "https://statsapi.web.nhl.com/api/v1/schedule"
base_url = "https://api-web.nhle.com/v1/schedule/" #Url changes as of Wed Nov 8 2023
# API call variable

start_date = datetime(2025,9,1) #date, used for observation
end_date = datetime(2026,5,1)
loop_date = start_date

while loop_date < end_date:
    game_date = loop_date.strftime("%Y-%m-%d")
    print(game_date+" processing")
    #r = requests.get(url=base_url+"?date="+game_date)
    r = requests.get(url=base_url+game_date)
    data = r.json()
    
    try:
        games = data["gameWeek"][0]["games"]
    except IndexError:
        loop_date = loop_date + timedelta(days=1)
        print("No games played on "+game_date)
        continue 
    
    # NB: Schedule provides all dates in the Zulu time, so some dates are
    # "in the future" but not really.
    
    # As with the NBA data, more advanced information can be obtained using the APO
    # and this file will provide a basis. The NHL API is far easier to use
    # than the NBA API, and has been used by other people for far more advanced
    # projects. Here this is only for scores.
    
    game_list = []
    for g in games:
        #pprint(g)
        if "score" in g["homeTeam"]: #if game was played
            game_dict = {}

            game_dict["away_team_abbrev"] = g["awayTeam"]["abbrev"]
            game_dict["away_team_name"] = full_name_from_abbrev(g["awayTeam"]["abbrev"])
            #print(g["awayTeam"]["abbrev"])
            game_dict["away_g"] = g["awayTeam"]["score"]
            game_dict["home_team_abbrev"] = g["homeTeam"]["abbrev"]
            game_dict["home_team_name"] = full_name_from_abbrev(g["homeTeam"]["abbrev"])
            game_dict["home_g"] = g["homeTeam"]["score"]
        
            #print(g["gameOutcome"]["lastPeriodType"])
            if g["gameOutcome"]["lastPeriodType"] == "SO": 
                game_dict["Game_Decided_By"] = "SO"
            elif g["gameOutcome"]["lastPeriodType"] == "OT":
                game_dict["Game_Decided_By"] = "OT"
            elif g["gameOutcome"]["lastPeriodType"] == "REG":
                game_dict["Game_Decided_By"] = "Regulation"
            else:
                print("Error - check game status for game "+str(g["id"]))
                break
            game_dict["game_date"] = game_date
            game_dict["game_datetime"] = datetime.fromisoformat(game_date)
            game_dict["datetime"] = epochtime(game_dict["game_datetime"])
            #pprint(game_dict)
            print(game_dict["away_team_abbrev"]+" "+str(game_dict["away_g"])+", "+game_dict["home_team_abbrev"]+" "+str(game_dict["home_g"])+" "+game_dict["Game_Decided_By"])

            #Applying rename fixes here.
            if game_dict["away_team_abbrev"] == "UTA":
                game_dict["away_team_abbrev"] = "ARI"

            if game_dict["home_team_abbrev"] == "UTA":
                game_dict["home_team_abbrev"] = "ARI"

            game_list.append(game_dict)
    
    for z in game_list:
        #Quick 
        Games.update(visitor_g = z["away_g"], home_g = z["home_g"],game_decided_by = z["Game_Decided_By"]).where((Games.game_date == z["game_date"]) & (Games.away_abbreviation == z["away_team_abbrev"]) & (Games.home_abbreviation == z["home_team_abbrev"])).execute()


    loop_date = loop_date + timedelta(days=1)
