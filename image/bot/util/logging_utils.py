import asyncio
import logging
from datetime import datetime

from database_utils import execute

def setup_logging(
        db_pool,
        loop: asyncio.AbstractEventLoop,
        logger_name: str | None = None,
        level: int = logging.INFO,
        table_name: str = "logs",
        ):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    db_handler = DatabaseLogHandler(db_pool=db_pool, loop=loop, table_name=table_name)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    return logger
    
    
class DatabaseLogHandler(logging.Handler):
    """
    A custom logging handler that stores log records in the database via database_utils.
    Since Python's logging is synchronous by default but our DB functions are async,
    we use run_coroutine_threadsafe to push work into the event loop.
    """
    def __init__(self, db_pool, loop: asyncio.AbstractEventLoop, table_name: str = "logs"):
        super().__init__()
        self.db_pool = db_pool
        self.loop = loop
        self.table_name = table_name
    
    def emit(self, record: logging.LogRecord):
        """
        Called automatically when a log event occurs. Formats the log message
        and submits a database write through an async method.
        """
        print(self.format(record)) # Temp logging through console
        
    
    async def _write_log_to_db(self, log_time: datetime, logger_name:str, level: str, message: str):
        """
        An async helper method for writing a single log entry to the database.
        """
        insert_query = f"""
            INSERT INTO {self.table_name} (timestamp, logger, level, message)
        """
        await execute(
            self.db_pool,
            insert_query,
            log_time.isoformat(),
            logger_name,
            level,
            message
        )
        
        
        
    
    