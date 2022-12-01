import multiprocessing
from datetime import datetime, timedelta
from typing import Optional, Union

import numpy as np
import pandas as pd
import requests

"""
historical_MAL_collector

The app will periodically collect statistics from currently airing shows for personal visualization and to observe trends
"""


class MALAPI:
    def __init__(self, client_id):
        self.client_id = client_id

    @staticmethod
    def convert_to_iso(timestamp: Optional[Union[datetime, str]] = None):
        if timestamp is None:
            return None
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, r"%Y-%m-%d")
        return timestamp.isoformat(timespec='milliseconds')[:-1] + 'Z'

    def get_anime_info(self, id):
        fields = [
            "start_date",
            "end_date",
            "mean",
            "num_list_users",
            "num_scoring_users",
            "status",
            "num_episodes",
            "average_episode_duration",
            "rating",
            "related_anime",
            "related_manga",
            "statistics",
            "genres",
            "media_type",
            "source",
            "studios",
        ]
        url = f"https://api.myanimelist.net/v2/anime/{id}?fields={','.join(fields)}"
        header = {'X-MAL-CLIENT-ID': self.client_id}
        return requests.get(url, headers=header).json()

    @staticmethod
    def get_seasons(timestamp: Optional[datetime] = None):
        if timestamp is None:
            timestamp = datetime.now()

        current_month = timestamp.month - 1
        current_year = timestamp.year
        seasons = ['winter', 'spring', 'summer', 'fall']
        current_season = [(seasons[current_month // 3], current_year)]
        if current_month % 4 == 0:
            current_season.append((seasons[current_month // 3 - 1], current_year - (current_month == 0)))
        elif current_month % 4 == 3:
            current_season.append(
                (seasons[(current_month // 3 + 1) % 4], current_year + (current_month == 11))
            )

        return current_season

    def get_current_season_shows(self, timestamp: Optional[datetime] = None):
        if timestamp is None:
            timestamp = datetime.now()

        # collect all shows that could be in season
        limit = 500
        data = []
        for season, year in self.get_seasons(timestamp):
            url = f'https://api.myanimelist.net/v2/anime/season/{year}/{season}?limit={limit}&fields=status,start_date,end_date'
            header = {'X-MAL-CLIENT-ID': self.client_id}
            while url:
                response = requests.get(url, headers=header).json()
                url = response['paging'].get('next')
                data.extend(response['data'])
        # print(data)
        # filter the shows that are airing and get their id
        id_set = set()
        for show in data:
            show = show['node']
            start_date = None
            end_date = None
            try:
                start_date = datetime.strptime(show['start_date'], r"%Y-%m-%d")
                end_date = datetime.strptime(show['end_date'], r"%Y-%m-%d")
            except (ValueError, KeyError):
                pass

            if show['status'] == 'currently_airing' or (
                (end_date and end_date + timedelta(days=7) > timestamp)
                and (start_date and start_date - timedelta(days=14) < timestamp)
            ):
                id_set.add(show['id'])

        return list(id_set)

    def task(self, id):
        response = self.get_anime_info(id)
        return {
            'title': response['title'],
            'score': response.get('mean'),
            'airing': response['status'] == 'currently_airing',
            'finished': response['status'] == 'finished_airing',
            'num_list_users': int(response['statistics']['num_list_users']),
            'num_scoring_users': response.get('num_scoring_users'),
            "num_episodes": response['num_episodes'] or None,
            "average_episode_duration": response['average_episode_duration'] or None,
            "rating": response.get('rating'),
            'num_watching': int(response['statistics']['status']['watching']),
            'num_completed': int(response['statistics']['status']['completed']),
            'num_dropped': int(response['statistics']['status']['dropped']),
            'num_plan_to_watch': int(response['statistics']['status']['completed']),
            'sequel': 'prequel' in [anime['relation_type'] for anime in response['related_anime']],
        }

    def get_all_anime_info(self, id_list):
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            data = pool.map(self.task, id_list)
        return data


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('client_id')
    args = parser.parse_args()

    filename = args.filename
    client_id = args.client_id

    api = MALAPI(client_id)
    timestamp = datetime.now()
    # print(api.get_current_season_shows())
    data = api.get_all_anime_info(api.get_current_season_shows())
    df = pd.DataFrame.from_records(data)
    # # columns = df.columns
    df['current_time'] = api.convert_to_iso(timestamp)
    # # df['table'] = 0
    # # df[''] = None
    # # df = df[['', 'table', 'current_time', *columns]]
    df = df.astype(
        {
            # 'table': 'Int64',
            'title': 'string',
            'score': 'float64',
            'airing': 'bool',
            'finished': 'bool',
            'num_list_users': 'Int64',
            'num_scoring_users': 'Int64',
            "num_episodes": 'Int64',
            "average_episode_duration": 'float64',
            "rating": 'string',
            'num_watching': 'Int64',
            'num_completed': 'Int64',
            'num_dropped': 'Int64',
            'num_plan_to_watch': 'Int64',
            'sequel': 'bool',
            'current_time': 'string',
        }
    )

    df.to_csv(filename, index=False)