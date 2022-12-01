source secrets.sh
curl --request POST http://localhost:8086/api/v2/query?org=personal \
    --header "Authorization: Token $token" \
    --header 'Accept: application/csv' \
    --header 'Content-type: application/vnd.flux' \
    --data 'from(bucket: "currently-airing-anime")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_field"] == "score")
                |> filter(fn: (r) => r["title"] == "Mob Psycho 100 III" or r["title"] == "Mob Psycho 100 III")'
