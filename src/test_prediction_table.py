"""Unit tests for playoff odds calculation and table rendering."""
from datetime import datetime
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call
import sys

import numpy as np
import pytest

import prediction_table as table


class _TeamQuery:
    def __init__(self, teams):
        self.teams = teams

    def order_by(self, _field):
        return self.teams


def _teams(rows):
    class FakeTeams:
        id = object()

        @classmethod
        def select(cls):
            return _TeamQuery(rows)

    return FakeTeams


def _team_rows(count=32):
    return [
        SimpleNamespace(
            id=team_id,
            team_name=f"Team {team_id}",
            abbreviation=f"T{team_id}",
            division=f"Division {team_id}",
            conference="E" if team_id % 2 else "W",
            legacy_divisions_3=f"Legacy {team_id}",
        )
        for team_id in range(1, count + 1)
    ]


def _install_calc_dependencies(monkeypatch, teams, future_games):
    import analytics.SRS as srs_module
    import analytics.purdy as purdy_module
    import analytics.wins_script as wins_module
    import nhl_database.queries as queries_module

    monkeypatch.setattr(table, "Teams", _teams(teams))
    monkeypatch.setattr(queries_module, "games_query", Mock(return_value=[[1, 2, 3, 4]]))
    monkeypatch.setattr(queries_module, "games_won_query", Mock(return_value=SimpleNamespace(
        tolist=lambda: [[0] * 32 for _ in range(32)]
    )))
    monkeypatch.setattr(queries_module, "future_games_query", Mock(return_value=future_games))
    monkeypatch.setattr(wins_module, "points_list", Mock(return_value=list(range(32))))
    monkeypatch.setattr(queries_module, "epochtime", Mock(return_value=12345))
    monkeypatch.setattr(table, "epochtime", Mock(return_value=12345))
    monkeypatch.setattr(table, "elo_ratings_list", Mock(return_value=[100 + 10 * i for i in range(32)]))

    srs_ratings = np.arange(32, dtype=float) * 1.5
    srs_mock = Mock(return_value=srs_ratings)
    monkeypatch.setattr(srs_module, "SRS", srs_mock)
    monkeypatch.setattr(purdy_module, "SRS_regress", Mock(side_effect=lambda difference: difference / 10))
    monkeypatch.setattr(purdy_module, "Elo_regress", Mock(side_effect=lambda difference: difference / 100))

    simulation_module = ModuleType("predict.cython_mcss.mcss_ext2")
    simulation_module.simulations_result_vectorized = Mock(
        return_value=[[0.25, 20.5, 0.75, 0.125, 66.0] for _ in range(32)]
    )
    monkeypatch.setitem(sys.modules, "predict.cython_mcss.mcss_ext2", simulation_module)
    return {
        "queries": queries_module,
        "wins": wins_module,
        "elo_ratings": table.elo_ratings_list,
        "srs": srs_module,
        "purdy": purdy_module,
        "simulation": simulation_module.simulations_result_vectorized,
    }


@pytest.mark.parametrize(
    ("ratings_mode", "expected_first_rating"),
    [
        ("Elo", 100),
        ("SRS", 0.0),
    ],
)
def test_playoff_odds_calc_builds_simulation_inputs_and_converts_percentages(
    monkeypatch, ratings_mode, expected_first_rating
):
    teams = _team_rows()
    future_games = [[1, 2], [3, 4]]
    dependencies = _install_calc_dependencies(monkeypatch, teams, future_games)
    monkeypatch.setattr(table, "Teams", _teams(teams))
    start_datetime = datetime(2024, 9, 1)
    end_datetime = datetime(2025, 2, 1)

    results = table.playoff_odds_calc(
        start_datetime, end_datetime, 2025, ratings_mode=ratings_mode
    )

    assert results == [[25.0, 20.5, 75.0, 12.5, 66.0] for _ in range(32)]
    args = dependencies["simulation"].call_args.args
    assert args[0] == [[0] * 32 for _ in range(32)]
    assert args[1][0][:2] == [1, 2]
    if ratings_mode == "Elo":
        assert args[1][0][2] == pytest.approx(0.1)
        assert args[1][1][2] == pytest.approx(0.1)
    else:
        assert args[1][0][2] == pytest.approx(0.15)
        assert args[1][1][2] == pytest.approx(0.15)
    assert args[2][0] == [1, b"Team 1", b"T1", b"Division 1", b"E", expected_first_rating, 0]
    assert args[2][1][6] == 1
    assert args[3:] == (2025, list(range(32)))
    expected_games_query_calls = 2 if ratings_mode == "SRS" else 1
    assert dependencies["queries"].games_query.call_args_list == [
        call(start_datetime, end_datetime)
    ] * expected_games_query_calls
    dependencies["wins"].points_list.assert_called_once_with(2025, start_datetime, end_datetime)

    if ratings_mode == "SRS":
        dependencies["srs"].SRS.assert_called_once_with([[1, 2, 3, 4]])
        dependencies["purdy"].SRS_regress.assert_has_calls([call(1.5), call(1.5)])
        dependencies["elo_ratings"].assert_not_called()
    else:
        dependencies["srs"].SRS.assert_not_called()
        dependencies["purdy"].Elo_regress.assert_has_calls([call(10), call(10)])
        dependencies["elo_ratings"].assert_called_once_with(12345)


def test_playoff_odds_calc_rejects_reversed_date_range(monkeypatch, capsys):
    simulation_module = ModuleType("predict.cython_mcss.mcss_ext2")
    simulation_module.simulations_result_vectorized = Mock()
    monkeypatch.setitem(sys.modules, "predict.cython_mcss.mcss_ext2", simulation_module)

    result = table.playoff_odds_calc(
        datetime(2025, 2, 1), datetime(2024, 9, 1), 2025
    )

    assert result == 1
    assert "Start date is after end date" in capsys.readouterr().out


def test_playoff_odds_print_applies_historical_conferences_formats_and_sorts(monkeypatch):
    teams = [
        SimpleNamespace(abbreviation="DET", conference="E"),
        SimpleNamespace(abbreviation="CBJ", conference="E"),
        SimpleNamespace(abbreviation="WPG", conference="W"),
        SimpleNamespace(abbreviation="BOS", conference="E"),
    ]
    monkeypatch.setattr(table, "Teams", _teams(teams))
    results = [
        [12.34, 20.04, 1.23, 45.67, 80.04],
        [9.99, 18.56, 2.22, 30.04, 70.06],
        [88.88, 22.22, 3.33, 40.04, 90.06],
        [50.05, 25.55, 4.44, 55.55, 100.05],
    ]

    output = table.playoff_odds_print(results, 2011)

    assert "Conference" in output
    assert "Avg. Wins" in output
    assert "PF%" in output
    assert "WC%" in output
    assert "ATL" in output
    assert "WPG" not in output
    assert "DET" in output
    assert "W             DET" in output
    assert "12.3%" in output
    assert "45.7%" in output
    assert output.index("BOS") < output.index("ATL") < output.index("DET") < output.index("CBJ")
