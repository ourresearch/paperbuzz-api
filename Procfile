web: gunicorn views:app --worker-class gevent --workers 3 --timeout 20 --reload
run_dates: bash run_dates_worker.sh
run: bash run_worker.sh