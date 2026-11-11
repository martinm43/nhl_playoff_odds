"""Unit tests for the information table data and renderer."""
from datetime import datetime
from unittest.mock import call, Mock

import info_table as table


def _wins_result(team_id, points_pct):
    return {
        "visitor_record": f"away-{team_id}",
        "home_record": f"home-{team_id}",
        "record": f"overall-{team_id}",
        "points": team_id * 2,
        "pts_pct": points_pct,
    }


def test_info_table_data_combines_sources_and_sorts_by_points_percentage(monkeypatch):
    season_year = 2025
    start_datetime = datetime(2024, 10, 1)
    end_datetime = datetime(2025, 4, 20)
    games = [[1, 2, 2, 3]]
    pythagorean_results = [[2, 31.6], [1, 27.4]]
    wins_by_team = {
        1: _wins_result(1, 0.5006),
        2: _wins_result(2, 0.7506),
    }
    wins_mock = Mock(side_effect=lambda team_id, *_: wins_by_team.get(
        team_id, _wins_result(team_id, 0.0)
    ))
    pythagorean_mock = Mock(return_value=pythagorean_results)
    srs_mock = Mock(return_value=[-99] * 32)
    new_srs_mock = Mock(return_value=[4.32149, 5.67891] + [0] * 30)
    elo_mock = Mock(return_value=[100, 200] + [0] * 30)
    form_mock = Mock(side_effect=lambda team_id: f"form-{team_id}")

    monkeypatch.setattr(table, "games_query", Mock(return_value=games))
    monkeypatch.setattr(table, "get_wins", wins_mock)
    monkeypatch.setattr(table, "league_pythagorean_wins", pythagorean_mock)
    monkeypatch.setattr(table, "SRS", srs_mock)
    monkeypatch.setattr(table, "new_srs_ratings_list", new_srs_mock)
    monkeypatch.setattr(table, "elo_ratings_list", elo_mock)
    monkeypatch.setattr(table, "form_query", form_mock)
    monkeypatch.setattr(table, "team_abbreviation", lambda team_id: f"T{team_id}")
    monkeypatch.setattr(table, "epochtime", lambda value: value.toordinal())

    results = table.info_table_data(season_year, start_datetime, end_datetime)

    assert results == [
        (
            "T2", 32.0, 5.679, 200, "away-2", "home-2", "overall-2", 4,
            0.751, "form-2",
        ),
        (
            "T1", 27.0, 4.321, 100, "away-1", "home-1", "overall-1", 2,
            0.501, "form-1",
        ),
    ]
    assert wins_mock.call_args_list == [
        call(team_id, season_year, start_datetime, end_datetime)
        for team_id in range(1, 33)
    ]
    pythagorean_mock.assert_called_once_with(
        table.Games,
        mincalcdatetime=start_datetime.toordinal(),
        maxcalcdatetime=end_datetime.toordinal(),
    )
    srs_mock.assert_called_once_with(
        games, max_MOV=100, home_team_adv=0, win_floor=0
    )
    new_srs_mock.assert_called_once_with(end_datetime)
    elo_mock.assert_called_once_with(end_datetime.toordinal())
    assert form_mock.call_args_list == [call(team_id) for team_id in range(1, 33)]


def test_info_table_data_returns_empty_when_there_are_no_pythagorean_rows(monkeypatch):
    monkeypatch.setattr(table, "games_query", Mock(return_value=[]))
    monkeypatch.setattr(table, "get_wins", Mock(return_value=_wins_result(1, 0)))
    monkeypatch.setattr(table, "league_pythagorean_wins", Mock(return_value=[]))
    monkeypatch.setattr(table, "SRS", Mock(return_value=[]))
    monkeypatch.setattr(table, "new_srs_ratings_list", Mock(return_value=[]))
    monkeypatch.setattr(table, "elo_ratings_list", Mock(return_value=[]))
    monkeypatch.setattr(table, "form_query", Mock(return_value=""))
    monkeypatch.setattr(table, "team_abbreviation", lambda team_id: str(team_id))
    monkeypatch.setattr(table, "epochtime", lambda value: 0)

    assert table.info_table_data(2025, datetime(2024, 10, 1), datetime(2025, 4, 20)) == []


def test_print_results_table_includes_date_range_headers_and_rows(monkeypatch, capsys):
    start_datetime = datetime(2024, 10, 1)
    end_datetime = datetime(2025, 4, 20)
    monkeypatch.setattr(table, "start_datetime", start_datetime, raising=False)
    monkeypatch.setattr(table, "end_datetime", end_datetime, raising=False)
    results = [
        ("T1", 40.0, 3.125, 1500, "10-5-2", "12-4-1", "22-9-3", 47, 0.691, "WWLWW")
    ]

    table.print_results_table(results)

    output = capsys.readouterr().out
    assert "Pythagorean Win Expectations, Est. SRS, Elo, and Records" in output
    assert "Based on Games Played Between: Oct 01 2024 and Apr 20 2025" in output
    assert "Pythag. Wins" in output
    assert "Overall Record" in output
    assert "T1" in output
    assert "WWLWW" in output
