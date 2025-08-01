import logging
import asyncio
import json
from datetime import datetime
from collections import deque
import threading

class SQLiteLogHandler(logging.Handler):
    def __init__(self, db_manager, batch_size: int = 50, flush_interval: float = 5.0):
        super().__init__()
        self.db_manager = db_manager
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Batch processing
        self.log_queue = deque()
        self.queue_lock = threading.Lock()

        # Start background flush task
        self._flush_task = None
        self._should_stop = False

        # Critical: Track loggers to prevent recursive logging
        self._logging_in_progress = False
        self._ignored_loggers = {
            'aiosqlite',
            'sqlite3',
            'asyncio',
            'watchfiles.main',          # Ignore watchfiles rust notify messages
            'watchfiles',               # Ignore all watchfiles messages
            'discord.gateway',          # Ignore verbose WebSocket messages
            self.__class__.__module__,  # Ignore this handler's own logs
            'util.database_utils',      # Ignore database utility logs
        }

    async def start_flush_task_async(self):
        """Async version of start_flush_task"""
        if not self._flush_task and not self._should_stop:
            try:
                self._flush_task = asyncio.create_task(self._flush_loop())
            except RuntimeError:
                # No event loop running yet, will be started later
                pass

    def start_flush_task(self):
        """Start the background flush task"""
        if not self._flush_task and not self._should_stop:
            try:
                self._flush_task = asyncio.create_task(self._flush_loop())
            except RuntimeError:
                # No event loop running yet, will be started later
                pass

    async def _flush_loop(self):
        """Background task to flush logs periodically"""
        while not self._should_stop:
            await asyncio.sleep(self.flush_interval)
            await self._flush_logs()

    def emit(self, record):
        """Add log record to batch queue"""
        # CRITICAL: Prevent recursive logging
        if self._logging_in_progress:
            return

        # Ignore logs from database-related modules to prevent recursion
        if record.name in self._ignored_loggers:
            return

        # Ignore logs from any logger that contains database-related keywords
        if any(keyword in record.name.lower() for keyword in ['sqlite', 'database', 'aiosqlite', 'watchfiles', 'gateway']):
            return

        # Filter out specific verbose messages even if they pass through
        if 'WebSocket Event:' in record.getMessage():
            return
        if 'executing functools.partial' in record.getMessage():
            return
        if 'operation functools.partial' in record.getMessage():
            return

        try:
            self._logging_in_progress = True
            log_entry = self._prepare_log_entry(record)

            with self.queue_lock:
                self.log_queue.append(log_entry)

                # Start flush task if not running and we're in an event loop
                if not self._flush_task:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            self._flush_task = loop.create_task(self._flush_loop())
                    except RuntimeError:
                        # No event loop running, we'll flush manually
                        pass

                # Flush if batch is full
                if len(self.log_queue) >= self.batch_size:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(self._flush_logs())
                    except RuntimeError:
                        # No event loop running, can't flush async
                        pass

        except Exception as e:
            # Don't call handleError as it might cause more logging
            print(f"Error in logging handler: {e}")
        finally:
            self._logging_in_progress = False

    def _prepare_log_entry(self, record):
        """Prepare log entry for database insertion"""
        extra_data = {}

        # Extract Discord-specific data if available
        guild_id = getattr(record, 'guild_id', None)
        channel_id = getattr(record, 'channel_id', None)
        user_id = getattr(record, 'user_id', None)

        # Store any extra attributes as JSON - but be very careful about recursion
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                           'filename', 'module', 'lineno', 'funcName', 'created',
                           'msecs', 'relativeCreated', 'thread', 'threadName',
                           'processName', 'process']:
                try:
                    json.dumps(value)  # Test if serializable
                    extra_data[key] = value
                except:
                    extra_data[key] = str(value)

        return (
            datetime.fromtimestamp(record.created).isoformat(),
            record.levelname,
            record.name,
            self.format(record),
            record.module,
            record.funcName,
            record.lineno,
            json.dumps(extra_data) if extra_data else None,
            guild_id,
            channel_id,
            user_id
        )

    async def _flush_logs(self):
        """Flush queued logs to database"""
        if self._logging_in_progress:
            return

        logs_to_insert = []

        with self.queue_lock:
            if self.log_queue:
                logs_to_insert = list(self.log_queue)
                self.log_queue.clear()

        if logs_to_insert:
            try:
                self._logging_in_progress = True
                await self.db_manager.execute_many(
                    """
                    INSERT INTO Logs (timestamp, level, logger_name, event_type, message, module,
                                     function_name, line_number, extra_data, server_id,
                                     channel_id, user_id)
                    VALUES (?, ?, ?, 'app_log', ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    logs_to_insert
                )
            except Exception as e:
                # Print to console for debugging, but don't log to prevent recursion
                print(f"Failed to insert logs: {e}")
            finally:
                self._logging_in_progress = False

    def close(self):
        """Synchronous close method for logging shutdown"""
        self._should_stop = True
        # Don't await here - this is called by the logging module during shutdown
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()

    async def async_close(self):
        """Async close method for proper cleanup"""
        self._should_stop = True
        if self._flush_task:
            await self._flush_logs()  # Final flush
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

def setup_logging(db_manager, level: int = logging.INFO):
    """Setup global logging configuration with SQLite handler"""

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler for development
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Create SQLite handler with recursion protection
    db_handler = SQLiteLogHandler(db_manager)
    db_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    db_handler.setFormatter(db_formatter)
    root_logger.addHandler(db_handler)

    # CRITICAL: Set logging levels for database-related loggers to prevent recursion and noise
    logging.getLogger('aiosqlite').setLevel(logging.WARNING)
    logging.getLogger('sqlite3').setLevel(logging.WARNING)
    logging.getLogger('util.database_utils').setLevel(logging.WARNING)

    # Suppress watchfiles DEBUG messages completely (rust notify timeout)
    logging.getLogger('watchfiles.main').setLevel(logging.WARNING)
    logging.getLogger('watchfiles').setLevel(logging.WARNING)
    
    # Suppress verbose Discord WebSocket messages
    logging.getLogger('discord.gateway').setLevel(logging.INFO)
    logging.getLogger('discord.client').setLevel(logging.INFO)
    
    # Keep cogwatch at INFO level for cog loading messages
    logging.getLogger('cogwatch').setLevel(logging.INFO)

    # Force all existing loggers to inherit root logger configuration
    for name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        # Don't override if we've specifically set a level above
        if name not in ['aiosqlite', 'sqlite3', 'util.database_utils', 'watchfiles.main', 
                       'watchfiles', 'discord.gateway', 'discord.client', 'cogwatch']:
            logger.setLevel(level)
        logger.handlers.clear()  # Remove any existing handlers
        logger.propagate = True  # Ensure they use root logger handlers

    # Store reference for cleanup
    set_db_handler(db_handler)

    # Start the database handler's flush task - FIXED: Use async version
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(db_handler.start_flush_task_async())
    except RuntimeError:
        # If no event loop is running, the task will start when first log is emitted
        pass

    return root_logger

# Global reference to the database handler for cleanup
_db_handler = None

def get_db_handler():
    """Get the database handler for cleanup purposes"""
    global _db_handler
    return _db_handler

def set_db_handler(handler):
    """Set the database handler reference"""
    global _db_handler
    _db_handler = handler