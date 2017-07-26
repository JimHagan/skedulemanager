"""
Author: Jake Lipson
Copyright 2017 Gentlemen's Bet Inc. All rights reserved.
"""
import pytz
import requests
import sys

from config import ENV
from game_base import GameInfo, GameInfoAPI
from datetime import datetime, timedelta

from slugify import slugify
from team_info import MLB_TEAM_DICT

requests.adapters.DEFAULT_RETRIES = 3

MLB_FANTASY_DATA_REQUEST_HEADERS = {
     ENV['MLB_FANTASY_DATA_SUBSCRIPTION_KEY']: ENV['MLB_FANTASY_DATA_API_KEY']
}


FORMAT = 'JSON'
MLB_GAME_BASE_URL = 'https://api.fantasydata.net/mlb/v2/'
VALID_QUERY_TYPES = ['GamesByDate']

DATE_CUTOFF = datetime(2017, 5, 15, 10)  # so we do not conflict with games we created manually


class MLBFantasyDataGameAPI(GameInfoAPI):
    """
    MLB FantasyData API Wrapper

    """
    # 14 days * 24 hours * 60 minutes * 60 seconds
    pitcher_cache_timeout = 1209600

    def __init__(self, query_type='GamesByDate', date='2017-JUL-24', season=None):
        # Date comes in the format: '2016-JAN-01'
        if query_type not in VALID_QUERY_TYPES:
            raise Exception("Query type {0} is not valid.  Valid types are: {1}".format(
                query_type,
                VALID_QUERY_TYPES,
            ))
        if query_type == 'GamesByDate':
            self._url = \
                "{0}{1}/{2}/{3}".format(MLB_GAME_BASE_URL, FORMAT, query_type, date)
        else:
            raise Exception('Unknown query type {0}'.format(query_type))

        self.game_info_list = []

    def _game_request(self):
        try:
            response = requests.get(self._url, headers=MLB_FANTASY_DATA_REQUEST_HEADERS)
        except Exception as e:
            print "Error connecting to api. {0}".format(e)
            return
        self.game_dump = response.json()

    def games(self):
        self._game_request()
        for game in self.game_dump:
            if True: # game["HomeTeamID"] in FOLLOWED_TEAMS or game["AwayTeamID"] in FOLLOWED_TEAMS:
                game_info = GameInfo(
                    home_team="MLB{0}".format(game["HomeTeamID"]),
                    away_team="MLB{0}".format(game["AwayTeamID"]),
                    stadium=game["StadiumID"],  # only provides a StadiumID
                    home_score=game["HomeTeamRuns"],
                    away_score=game["AwayTeamRuns"],
                    spread=game['PointSpread'],
                    over_under=game["OverUnder"],
                    scheduled_start_datetime=game["DateTime"] if game["DateTime"] else game["Day"],
                    actual_start_datetime=None,
                    last_known_period=game["Inning"] or game["Status"],
                    end_datetime=None,
                    is_final=game["Status"] == 'Final',
                    channel=game["Channel"],
                    season_type=game["SeasonType"],
                    season=game["Season"],
                    week=None,  # game["Week"],  No week in this API
                    has_started=game["Status"] not in ["Scheduled", "Postponed", "Canceled"],
                    possession="",  # game["Possession"],
                    is_in_progress=game["Status"] not in ["Final", "Scheduled", "Postponed", "Canceled", "Suspended"],
                    is_overtime='Inning' in game and game["Inning"] > 9,
                    time_remaining="", # 9 - game["Inning"] if game["Inning"] else None,
                    quarter_description="Inning: {0}".format(game["Inning"]) if ('Inning' in game and game['Inning']) else '',
                    ext_game_key="MLB{0}{1}".format(game["Season"], game["GameID"]),
                    league="MLB",
                    pre_game_summary=None# self.build_pre_game_summary(game),
                )
                game_info.datetime_from_string()
                if game_info.scheduled_start_datetime < DATE_CUTOFF:  # dont add games before cutoff
                    continue
                eastern_tz = pytz.timezone('US/Eastern')
                game_info.scrub(default_tz=eastern_tz, league='MLB')
                self.game_info_list.append(game_info)
        return self.game_info_list


    def mlb_get_scheduled_game_info(self, _stdout=sys.stdout, days_to_fetch=5):
        now = datetime.now(pytz.utc)  # + timedelta(days=1)
        end_date = now + timedelta(days=days_to_fetch)
        diff = end_date - now
        games = []
        for i in range(diff.days + 1):
            current_date = (now + timedelta(i)).strftime("%Y-%b-%d").upper()
            _games = MLBFantasyDataGameAPI(query_type='GamesByDate', date=current_date).games()
            _stdout.write("Received: {0}\n".format(len(_games)))
            games.extend(_games)
        _stdout.write("Total scheduled games retrieved: {0}\n".format(len(games)))
	return games

    def mlb_get_scheduled_game_info_as_skedules(self, _stdout=sys.stdout, days_to_fetch=5):
        games = self.mlb_get_scheduled_game_info(_stdout, days_to_fetch)
        skedules = {}
        for g in games:
            home_team_info = MLB_TEAM_DICT[g.home_team]
            home_team = slugify(home_team_info['fullname'])
            away_team_info = MLB_TEAM_DICT[g.away_team]
	    away_team = slugify(away_team_info['fullname'])
            print home_team
            event = {}
	    event['starts_on'] = str(g.scheduled_start_datetime)
            event['ends_on'] = str(g.scheduled_start_datetime + timedelta(hours=5))
	    event['all_day'] = False
            event['title'] = '{0} vs. {1}'.format(home_team_info['fullname'],away_team_info['fullname'])
            event['tz'] = 'US/Eastern'
            event['images'] = {'home_team_logo_path': home_team_info['logo_image_url'], 'away_team_logo_path': away_team_info['logo_image_url']}
	    event['tags'] = ["Major League Baseball", '{0}'.format(home_team_info['fullname']), g.ext_game_key]	
            event['notes'] = "" 
	    stadium = home_team_info['stadium']
	    event['location'] = stadium['name']
            event['address'] = {
		'formatted': stadium['addr'],
                'lat': stadium['lat'],
                'lng': stadium['lng'],
	    }
	    if home_team in skedules:
                skedules[home_team].append(event)
            else:
		skedules[home_team] = [event]
            
	return skedules
