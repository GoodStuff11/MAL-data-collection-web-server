source code/secrets.sh
token=${token//$'\r'}
python analysis.py $token
