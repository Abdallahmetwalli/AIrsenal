"""
Test the optimization of transfers, generating a few simplified scenarios
and checking that the optimizer finds the expected outcome.
"""
import pytest
from unittest import mock

from ..optimization_utils import *


class DummyPlayer(object):
    """
    fake player that we can add to a team, giving a specified expected score.
    """
    def __init__(self,player_id,position,points_dict):
        """
        we generate team to avoid >3-players-per-team problem,
        and set price to 0 to avoid overrunning budget.
        """
        self.player_id = player_id
        self.name = "player_{}".format(player_id)
        self.position = position
        self.team = "DUMMY_TEAM_{}".format(player_id)
        self.current_price = 0
        self.is_starting = True
        self.is_captain = False
        self.is_vice_captain = False
        self.predicted_points = {"DUMMY": points_dict}

    def calc_predicted_points(self,dummy):
        pass

def generate_dummy_team(player_points_dict=None):
    """
    Fill a team up with dummy players.
    player_points_dict is a dictionary
    { player_id: { gw: points,...} ,...}
    """
    if not player_points_dict:  # make a simple one
        player_points_dict = {}
        for i in range(15):
            player_points_dict[i] = {1: 2} # 2 points per game
    t=Team()
    for i in range(15):
        if i<2:
            position="GK"
        elif i<7:
            position="DEF"
        elif i<12:
            position="MID"
        else:
            position="FWD"
        t.add_player(DummyPlayer(i,position,player_points_dict[i]))
    return t


def predicted_point_mock_generator(point_dict):
    """
    return a function that will mock the get_predicted_points function
    the point_dict it is given should be keyed by position, i.e.
    {"GK" : {player_id: points, ...}, "DEF": {}, ... }
    """

    def mock_get_predicted_points(gameweek, method, position, team=None):
        """
        return an ordered list in the same way as the real
        get_predicted_points func does
        """
        output_list = [(k,v) for k,v in point_dict[position].items()]
        output_list.sort(key=itemgetter(1), reverse=True)
        return output_list
    return mock_get_predicted_points



def test_subs():
    """
    mock squads with some players predicted some points, and
    some predicted to score zero, and check we get the right starting 11.
    """
    points_dict = { 0: {1:0},
                    1: {1:2},
                    2: {1:2},
                    3: {1:2},
                    4: {1:0},
                    5: {1:2},
                    6: {1:2},
                    7: {1:2},
                    8: {1:2},
                    9: {1:0},
                    10: {1:2},
                    11: {1:4},
                    12: {1:0},
                    13: {1:2},
                    14: {1:3}
                    }
    ## should get 4,4,2, with players 0,4,9,12 on the bench,
    ## captain player 11, vice-captain player 14
    ## should have 29 points (9*2 + 3 + (2*4) )
    t = generate_dummy_team(points_dict)
    ep = t.get_expected_points(1,"DUMMY")
    assert(ep==29)
    assert(t.players[0].is_starting==False)
    assert(t.players[4].is_starting==False)
    assert(t.players[9].is_starting==False)
    assert(t.players[12].is_starting==False)
    assert(t.players[11].is_captain==True)
    assert(t.players[14].is_vice_captain==True)



def test_single_transfer():
    """
    mock squad with all players predicted 2 points, and potential transfers
    with higher scores, check we get the best transfer.
    """
    t = generate_dummy_team()
    position_points_dict = {"GK": {0:2, 1:2,   # in the orig team
                                   100:0, 101: 0,
                                   200:3, 201:2},
                            "DEF": {3: 2, 4: 2, 5:2, 6:2, 7:2,# in the orig team
                                    103:0, 104:0, 105:5, 106:2, 107:2,
                                    203:0, 204:0, 205:1, 206:2, 207:2},
                            "MID": {8:2, 9:2, 10:2, 11:2, 12:2, # in the orig team
                                    108:2, 109:2, 110:3, 111:3, 112:0,
                                    208:2, 209:2, 210:3, 211:3, 212:0},
                            "FWD": {13:2, 14:2, 15:2, # in the orig team
                                    113: 6, 114:3, 115:7}
                            }
    mock_pred_points= predicted_point_mock_generator(position_points_dict)
#    with mock_pred_points as get_predicted_points:
#        make_optimimum_substitution(t,"DUMMY",1)
    return mock_pred_points


def test_double_transfer():
    """
    mock squad with two players predicted low score, see if we get better players
    transferred in.
    """
    pass
