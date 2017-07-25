"""
Authors: Jim Hagan and Joe Pasquantonio
Copyright 2016 Gentlemen's Bet Inc. All rights reserved.
"""
import pytz
from datetime import datetime
from abc import ABCMeta, abstractmethod

STADIUM_CORRECTIONS = {
    'LP Field': 'Nissan Stadium',
    'Reliant Stadium': 'NRG Stadium',
}

def _aware_datetime_from_naive_datetime(naive_datetime, default_tz):
    """
    Convert Naive datetime to Timezone Aware
    :param naive_datetime: datetime object with no timezone
    :param default_tz: example pytz.timezone("US/Eastern")
    :return: nothing
    """
    if naive_datetime.tzinfo is not None:
        raise Exception("Timezone already set for {0}".format(naive_datetime))
    if default_tz is None:
        raise Exception("Function requires a timezone for argument default_tz")
    try:
        return default_tz.normalize(default_tz.localize(naive_datetime))
    except Exception as e:
        print e
        return naive_datetime

class GameInfoAPI(object):
    """ Base Class """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def _game_request(self):
        """ Get request to specified URL and return json. """
        pass

    @abstractmethod
    def games(self, datetime1=None, datetime2=None, completed_only=False, in_progress_only=False, team_list=[]):
        """ Parse the json return games information"""
        pass


class GameInfo(object):
    """ Lightweight class to store game information """

    def __init__(
            self, home_team, away_team, stadium, home_score, away_score, spread, over_under,
            scheduled_start_datetime, actual_start_datetime, end_datetime, last_known_period,
            is_final, channel, season_type, season, week,
            has_started=False, possession=None, is_in_progress=False, is_overtime=False,
            time_remaining=None, quarter_description=None, ext_game_key=None, league=None, pre_game_summary=''):
        self.ext_game_key = ext_game_key
        self.home_team = home_team
        self.away_team = away_team
        self.stadium = stadium
        self.home_score = home_score
        self.away_score = away_score
        self.spread = spread
        self.over_under = over_under
        self.scheduled_start_datetime = scheduled_start_datetime
        self.actual_start_datetime = actual_start_datetime
        self.end_datetime = end_datetime
        self.last_known_period = last_known_period
        self.is_final = is_final
        self.channel = channel
        self.season_type = season_type,
        self.season = season,
        self.week = week,
        self.has_started = has_started,
        self.possession = possession,
        self.is_in_progress = is_in_progress,
        self.is_overtime = is_overtime,
        self.time_remaining = time_remaining,
        self.quarter_description = quarter_description
        self.league=league
        self.pre_game_summary = pre_game_summary

    def __str__(self):
        return "{0}: ({1}) at {2}: ({3}) on channel:{4}".format(self.away_team, self.away_score,
                                                                self.home_team, self.home_score,
                                                                self.channel)

    def nice_score(self):
        """
        Returns a string of the score of the game.
        e.g., "NE (32) vs. NYG (0)".
        """
        return '%s (%d) at %s (%d)' \
               % (self.away_team, self.away_score, self.home_team, self.home_score)

    def datetime_from_string(self):
        fmt = '%Y-%m-%dT%H:%M:%S'
        self.scheduled_start_datetime = datetime.strptime(self.scheduled_start_datetime, fmt)

    def scrub(self, default_tz=None, league=None):
        """
        Correction lookup and replace
        :param default_tz: example pytz.timezone("US/Eastern")
        :param league:
        :return:
        """
        QUARTER_NAME_CONVERSTIONS = {
            'Scheduled': 0,
            'Canceled': 0,
            'Postponed': 0,
            '': 0,
            '1st': 1,
            '2nd': 2,
            '3rd': 3,
            '4th': 4,
            'First': 1,
            'Second': 2,
            'Half': 2,
            'Third': 3,
            'Fourth': 4,
            'Final': 4,
            'F': 4,
            'F/OT': 5,
            'Final/OT': 5,
            'OT': 5,
        }

        self.last_known_period = QUARTER_NAME_CONVERSTIONS.get(self.last_known_period, self.last_known_period)
        self.stadium = STADIUM_CORRECTIONS.get(self.stadium, self.stadium)

        if self.scheduled_start_datetime.tzinfo is None or self.scheduled_start_datetime.tzinfo.utcoffset(self.scheduled_start_datetime) is None:
            self.scheduled_start_datetime = _aware_datetime_from_naive_datetime(self.scheduled_start_datetime, default_tz)


        # Some fields were coming in as as tuples.  This is a workaround to deal with this.
        # I've put an email into FantasyData to address
        new_fields = ['season_type', 'season', 'week', 'has_started',
                      'possession', 'is_in_progress', 'is_overtime', 'time_remaining',
                      'quarter_description', 'quarter_description']
        for f in new_fields:
            obj = getattr(self, f)
            if isinstance(obj, tuple):
                setattr(self, f, obj[0]) 


