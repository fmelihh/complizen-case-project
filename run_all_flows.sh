export PYTHONPATH=$(pwd) &&
prefect config set PREFECT_API_URL="http://0.0.0.0:4200/api" &&
python src/flows/db_510k.py &
python src/flows/openfda.py &
python src/flows/summary_parser.py &
wait
