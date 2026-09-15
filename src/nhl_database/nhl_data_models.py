"""
ORM class objects for the tables within the nhl_data.sqlite database.

"""
# from peewee import *
from peewee import TextField, FloatField, IntegerField, SqliteDatabase, Model

database = SqliteDatabase("nhl_data.sqlite", **{})


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class Games(BaseModel):
    """ORM object for the Games table"""

    notes = TextField(column_name="Notes", null=True)
    game_decided_by = TextField(null=True)
    visitor_g = IntegerField(null=True)
    visitor = TextField(null=True)
    visitor_team_id = IntegerField(null=True)
    game_date = TextField(null=True)
    game_datetime = IntegerField(null=True)
    home_g = IntegerField(null=True)
    home = TextField(null=True)
    home_team_id = IntegerField(null=True)
    season_year = IntegerField(null=True)
    log = TextField(null=True)
    attendance = IntegerField(null=True)
    home_abbreviation = TextField(null=True)
    away_abbreviation = TextField(null=True)


    class Meta:
        table_name = "games"


class Teams(BaseModel):
    """ORM object for the Teams table"""

    """
    CREATE TABLE "teams" (
	`id`	INTEGER NOT NULL,
	`abbreviation`	TEXT,
	`city`	TEXT,
	"conference"	TEXT,
	`division`	TEXT,
	`team_name`	TEXT,
	"alternate_name"	TEXT, primary_color text, legacy_divisions_1 text, legacy_divisions_2 text, legacy_divisions_3 text,
	PRIMARY KEY(id)
    )
    """

    abbreviation = TextField(null=True)
    team_name = IntegerField(null=True)  
    city = TextField(null=True)
    conference = TextField(null=True)
    team_name = TextField(null=True)
    division = TextField(null=True)
    alternate_name = TextField(null=True)
    primary_color = TextField(null=True)
    legacy_divisions_1 = TextField(null=True)
    legacy_divisions_2 = TextField(null=True)
    legacy_divisions_3 = TextField(null=True)

    class Meta:
        table_name = "teams"


class ProlineData(BaseModel):
    """ORM object for the historic ProLine Data table"""

    away_1st = IntegerField(null=True)
    away_2nd = IntegerField(null=True)
    away_3rd = IntegerField(null=True)
    away_4th = IntegerField(null=True)
    away_ot_pts = IntegerField(column_name="away_OT_pts", null=True)
    away_pts = IntegerField(null=True)
    away_team = TextField(null=True)
    away_team_id = IntegerField(null=True)
    away_v_money_line = FloatField(null=True)
    away_v_ou = FloatField(null=True)
    away_v_pts_money = FloatField(null=True)
    away_v_pts_sprd = FloatField(null=True)
    date = TextField(null=True)
    home_1st = IntegerField(null=True)
    home_2nd = IntegerField(null=True)
    home_3rd = IntegerField(null=True)
    home_4th = IntegerField(null=True)
    home_ot_pts = IntegerField(column_name="home_OT_pts", null=True)
    home_pts = IntegerField(null=True)
    home_team = TextField(null=True)
    home_team_id = IntegerField(null=True)
    home_v_money_line = FloatField(null=True)
    home_v_ou = FloatField(null=True)
    home_v_pts_money = FloatField(null=True)
    home_v_pts_sprd = FloatField(null=True)
    home_v_total = FloatField(null=True)
    season = IntegerField(null=True)
    time_of_day = TextField(null=True)
    unix_date = FloatField(null=True)

    class Meta:
        table_name = "proline_data"


class TeamEloData(BaseModel):
    """ORM object for the team elo table"""

    season_year = IntegerField(null=True)  #
    team_abbreviation = TextField(null=True)
    datetime = FloatField(null=True)
    elo_rating = FloatField(null=True)
    team_id = IntegerField(null=True)

    class Meta:
        table_name = "team_elo_data"


class SRS(BaseModel):
    """ORM object for the team elo table"""

    team_id = IntegerField(null=True)  #
    team_abbreviation = TextField(null=True)
    current_abbreviation = TextField(null=True)
    srs_rating = FloatField(null=True)
    epochtime = FloatField(null=True)
    year = IntegerField(null=True)

    class Meta:
        table_name = "SRS"



