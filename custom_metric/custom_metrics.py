import requests
import time
import logging
from config  import SERVER_URL
from config import METRICS_FILE_NAME
from config import POLL_INTERVAL


prometheus_api_url = SERVER_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
metrics_file = METRICS_FILE_NAME

def api_response_time(url):
    try:
        start_time = time.time()
        logging.info(f"start response : {start_time}")
        response = requests.get(url)
        end_time = time.time()
        logging.info(f"end response : {end_time}")

        # Измеряем время отклика в секундах
        response_time_ms = (end_time - start_time)

        return response_time_ms
    except requests.exceptions.RequestException:
        return -1
    
def main():
    while True:
        response_time = "{:.6f}".format(api_response_time(prometheus_api_url))
        metric_name = 'prometheus_http_metrics_response_time'
        help_text = 'time that the metrics server is response.'
        metric_type = 'gauge'
        labels = 'handler="/metrics"'

        # Записываем метрики в файл
        with open(metrics_file, 'w+') as f:
            value = str(response_time).replace(',', '.')
            logging.info("Write metrics in file")
            metric_string = f'# HELP {metric_name} {help_text}\n'
            metric_string += f'# TYPE {metric_name} {metric_type}\n'
            metric_string += f'{metric_name}{{{labels}}} {value}'
            f.write(metric_string)
        time.sleep(POLL_INTERVAL)

    
if __name__ == '__main__':
    main()

