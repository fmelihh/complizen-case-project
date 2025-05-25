import os
import sys
from prefect import flow
from datetime import timedelta
from prefect.client.schemas.schedules import IntervalSchedule

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from src.complizen.fda_graph.crawler.openfda import OpenFDACrawler



@flow(log_prints=True, flow_run_name="openfda flow")
def run_openfda_task():
    crawler = OpenFDACrawler()
    crawler.crawl()


if __name__ == "__main__":
    run_openfda_task.serve(
        schedule=IntervalSchedule(interval=timedelta(hours=3)),
    )
