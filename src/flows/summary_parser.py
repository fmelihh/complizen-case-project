import os
import sys
from prefect import flow
from datetime import timedelta
from prefect.client.schemas.schedules import IntervalSchedule

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.complizen.fda_graph.services import SummaryParserService



@flow(log_prints=True, flow_run_name="summary parser")
def run_summary_parser_task():
    summary_parser = SummaryParserService()
    summary_parser.parse()


if __name__ == "__main__":
    run_summary_parser_task.serve(
        schedule=IntervalSchedule(interval=timedelta(hours=3)),
    )
