import os
import sys
from prefect import flow
from datetime import timedelta
from prefect.client.schemas.schedules import IntervalSchedule

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from src.complizen.fda_graph.crawler import Db510kCrawler



@flow(log_prints=True, flow_run_name="db 510k flow")
def run_db_510k_task():
    crawler = Db510kCrawler()
    crawler.crawl()


if __name__ == "__main__":
    run_db_510k_task.serve(
        schedule=IntervalSchedule(interval=timedelta(hours=3)),
    )
