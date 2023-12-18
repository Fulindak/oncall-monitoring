import json
import logging
from prometheus_client import start_http_server, Gauge, Counter
import requests
import time
from config import *


class CustomExporter:
    def __init__(self):
        self.service_availability = Gauge('service_availability',
                                          'Service availability (1 for up, 0 for down)',
                                          ['service'])
        self.correct_teams_format = Gauge('correct_teams_format',
                                          'Check for correct format teams(1 for correct, 0 for error)',
                                          ['service'])
        self.service_response_time = Gauge('service_response_time',
                                           'Check service response_time',
                                           ['service'])
        self.service_status = Counter('service_response',
                                      'Count service status code',
                                      ['method', 'endpoint', 'code'])

 
    def check_service_availability(self, url):
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            logger.error("Error checking service availability: %s", url)
            return False

    def response_data(self, url):
        try:
            response = requests.get(url)
            logger.info('Requesting data. URL: %s, Status Code: %s', url, response.status_code)
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            logger.error("Error response data from %s. Error: %s", url, str(e))
            return None

    def check_correct_teams(self, url):
        try:
            team_url = url + "/api/v0/teams/"
            teams = self.response_data(team_url)

            if not teams:
                return False

            for team in teams:
                team_users_url = url + f"/api/v0/teams/{team}/users"
                users = self.response_data(team_users_url)

                if not users or len(users) < 2:
                    logger.error('Failed to get users for team %s. URL: %s', team, team_users_url)
                    return False

            return True
        except requests.exceptions.RequestException as e:
            logger.error("Error checking correct teams format: %s. Error: %s",team_url,  str(e))
            return False

    def check_service(self, url):
        try:
            start_time = time.time()
            code = requests.get(url).status_code
            end_time = time.time()
            return {code: end_time - start_time}
        except requests.exceptions.RequestException:
            logger.error("Error checking service response time: %s", url)
            return {'Error': -1}

    def update_metrics(self, url):
        code_ex = ['200', '404', '500', 'Error']
        for code in code_ex:
            self.service_status.labels('GET', CHECK_LIVE_SERVICE_URL, code).inc(0)
        while True:
            service_availability_value = 1 if self.check_service_availability(url) else 0
            self.service_availability.labels(SERVICE_NAME).set(service_availability_value)
            logger.info("Service availability set to: %s", service_availability_value)

            correct_teams_value = 1 if self.check_correct_teams(url) else 0
            self.correct_teams_format.labels(SERVICE_NAME).set(correct_teams_value)
            logger.info("Correct teams format set to: %s", correct_teams_value)

            response = self.check_service(url)
            code = next(iter(response))
            self.service_response_time.labels(SERVICE_NAME).set(response[code])
            logger.info("Service response time set to: %s seconds", response[code])

            self.service_status.labels("GET", CHECK_LIVE_SERVICE_URL, code).inc()
            logger.info("Service status counter increased for code: %s", code)

            time.sleep(INTERVAL_GET_METRICS)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    start_http_server(SERVER_PORT)
    exporter = CustomExporter()
    exporter.update_metrics(SERVER_URL)
