from io import StringIO

import pandas as pd
import pytz
import requests

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('token')
    args = parser.parse_args()

    token = args.token

    url = 'http://localhost:8086/api/v2/query?org=personal'
    header = {
        "Authorization": f"Token {token}",
        'Accept': 'application/csv',
        'Content-type': 'application/vnd.flux',
    }
    data = """
            from(bucket: "currently-airing-anime")
                |> range(start: -7d)
                |> filter(fn: (r) => r["title"] == "JoJo no Kimyou na Bouken Part 6: Stone Ocean Part 3")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> drop (columns: ["_start","_stop"])
                |> yield(name: "last")
            """
            
    response = requests.post(url, headers=header, data=data).text
    # process multiple yield statements
    for table in response.split('\r\n\r\n')[:-1]:
        df = pd.read_csv(StringIO(table))
        df = df.dropna(how='all', axis='columns')
        df = df.drop(columns=['table', 'result', '_measurement'])
        df["_time"] = pd.to_datetime(df["_time"], infer_datetime_format=True, utc=True).dt.tz_convert(pytz.timezone('US/Eastern'))
        df = df.rename(columns={'_time': 'time'})
        print(df.columns)
