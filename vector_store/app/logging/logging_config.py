import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path

class LogConfig:
    def __init__(self):
        self.log_dir = os.getenv('LOG_DIR', 'logs')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        
        # Create separate loggers for different components
        self.loggers = {
            'app': self._setup_app_logger(),
            'access': self._setup_access_logger(),
            'error': self._setup_error_logger(),
            'security': self._setup_security_logger()
        }
        # Silence socketio and engineio logs
        logging.getLogger('socketio').setLevel(logging.ERROR)
        logging.getLogger('socketio').propagate = False

        logging.getLogger('engineio').setLevel(logging.ERROR)
        logging.getLogger('engineio').propagate = False

        logging.getLogger('engineio.server').setLevel(logging.ERROR)
        logging.getLogger('engineio.server').propagate = False

    def _ensure_log_dir(self):
        """Ensure log directory exists with proper permissions"""
        log_path = Path(self.log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_path.chmod(0o755)  # rwxr-xr-x

    def _create_formatter(self):
        """Create a formatter for the logs"""
        return logging.Formatter(self.log_format)

    def _setup_app_logger(self):
        """Setup the main application logger"""
        self._ensure_log_dir()
        logger = logging.getLogger('app')
        logger.setLevel(self.log_level)

        # File handler for general logs
        fh = RotatingFileHandler(
            os.path.join(self.log_dir, 'app.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        fh.setFormatter(self._create_formatter())
        logger.addHandler(fh)

        # Error handler with ERROR level
        eh = RotatingFileHandler(
            os.path.join(self.log_dir, 'app_error.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        eh.level = logging.ERROR
        eh.setFormatter(self._create_formatter())
        logger.addHandler(eh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(self._create_formatter())
        logger.addHandler(ch)

        return logger

    def _setup_access_logger(self):
        """Setup logger for access logs"""
        logger = logging.getLogger('access')
        logger.setLevel(self.log_level)

        # Daily rotating file handler for access logs
        fh = TimedRotatingFileHandler(
            os.path.join(self.log_dir, 'access.log'),
            when='midnight',
            interval=1,
            backupCount=30
        )
        fh.setFormatter(self._create_formatter())
        logger.addHandler(fh)

        return logger

    def _setup_error_logger(self):
        """Setup logger for error logs"""
        logger = logging.getLogger('error')
        logger.setLevel(logging.ERROR)

        # File handler for error logs
        fh = RotatingFileHandler(
            os.path.join(self.log_dir, 'error.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        fh.setFormatter(self._create_formatter())
        logger.addHandler(fh)

        return logger

    def _setup_security_logger(self):
        """Setup logger for security-related logs"""
        logger = logging.getLogger('security')
        logger.setLevel(logging.INFO)

        # File handler for security logs
        fh = RotatingFileHandler(
            os.path.join(self.log_dir, 'security.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        fh.setFormatter(self._create_formatter())
        logger.addHandler(fh)

        return logger

    def get_logger(self, name='app'):
        """Get a specific logger by name"""
        return self.loggers.get(name, self.loggers['app'])

# Create a global instance
log_config = LogConfig()

# Convenience function to get loggers
def get_logger(name='app'):
    return log_config.get_logger(name)