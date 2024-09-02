"""
This module's intention is to aggregate larger (>3) or inconvenient-to-be-placed-in-code logging or
print statements into functions
"""
from logging import Logger
from os import sep as ossep


def log_exit_messages(logger: Logger, log_path: str, db_path: str) -> None:
    """Log info about logfile and db at the end of exec"""
    exe_id = log_path.rsplit(ossep, 2)[1]
    logger.info(f"This execution received ID: {exe_id}")
    logger.info("More information on this execution can be acquired in:")
    logger.info(f"logfile: {log_path}")
    logger.info(f"database: {db_path}")
