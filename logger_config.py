# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# logger_config.py
"""
Centralized logging configuration for the Dash Gemini Chatbot application.
This module provides structured logging with environment-based configuration,
rotating file handlers, and contextual logging for debugging function calling issues.
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContextualLogger:
    """Enhanced logger with context tracking for function calls and API interactions."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context information for subsequent log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context information."""
        self.context.clear()
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log message with current context."""
        if self.context:
            extra = kwargs.get('extra', {})
            extra.update(self.context)
            kwargs['extra'] = extra
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add context information if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'model_name'):
            log_entry['model_name'] = record.model_name
        if hasattr(record, 'function_call'):
            log_entry['function_call'] = record.function_call
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        if hasattr(record, 'token_usage'):
            log_entry['token_usage'] = record.token_usage
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'ENDC': '\033[0m'       # End color
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['ENDC']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build context string
        context_parts = []
        if hasattr(record, 'model_name'):
            context_parts.append(f"model={record.model_name}")
        if hasattr(record, 'function_call'):
            context_parts.append(f"func={record.function_call}")
        if hasattr(record, 'response_time'):
            context_parts.append(f"time={record.response_time:.2f}s")
        
        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""
        
        return f"{color}{timestamp} {record.levelname:8s}{reset} {record.name:15s} {record.getMessage()}{context_str}"


class LoggingConfig:
    """Main logging configuration class."""
    
    def __init__(self):
        # Environment variables for logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_to_console = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
        self.log_to_file = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
        self.log_format = os.getenv('LOG_FORMAT', 'colored').lower()  # 'colored', 'json', 'simple'
        self.log_dir = os.getenv('LOG_DIR', 'logs')
        self.max_log_files = int(os.getenv('MAX_LOG_FILES', '7'))  # Keep last 7 days
        self.max_log_size = int(os.getenv('MAX_LOG_SIZE_MB', '10')) * 1024 * 1024  # 10MB default
        
        # Create logs directory if needed
        if self.log_to_file:
            Path(self.log_dir).mkdir(exist_ok=True)
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging based on environment variables."""
        
        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level))
            
            if self.log_format == 'json':
                console_handler.setFormatter(JSONFormatter())
            elif self.log_format == 'colored':
                console_handler.setFormatter(ColoredConsoleFormatter())
            else:
                console_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                )
            
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.log_to_file:
            log_file = os.path.join(self.log_dir, 'gemini_chatbot.log')
            
            # Use TimedRotatingFileHandler for daily rotation
            file_handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=self.max_log_files,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self.log_level))
            
            # Always use JSON format for file logging for better parsing
            file_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(file_handler)
            
            # Also create a separate error log file
            error_file = os.path.join(self.log_dir, 'gemini_chatbot_errors.log')
            error_handler = logging.handlers.TimedRotatingFileHandler(
                error_file,
                when='midnight',
                interval=1,
                backupCount=self.max_log_files,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(error_handler)
        
        # Mute the late-shutdown library DEBUG logs during Python interpreter shutdown
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> ContextualLogger:
        """Get a contextual logger for a specific module."""
        return ContextualLogger(name)
    
    def get_function_call_logger(self) -> ContextualLogger:
        """Get a specialized logger for function calling operations."""
        logger = ContextualLogger('gemini_chatbot.function_calls')
        return logger
    
    def get_api_logger(self) -> ContextualLogger:
        """Get a specialized logger for API operations."""
        logger = ContextualLogger('gemini_chatbot.api')
        return logger
    
    def get_chart_logger(self) -> ContextualLogger:
        """Get a specialized logger for chart generation."""
        logger = ContextualLogger('gemini_chatbot.charts')
        return logger


# Context managers for tracking operations
class LoggedOperation:
    """Context manager for logging operations with timing."""
    
    def __init__(self, logger: ContextualLogger, operation_name: str, **context):
        self.logger = logger
        self.operation_name = operation_name
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.set_context(**self.context)
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.set_context(response_time=duration)
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} successfully", 
                           extra={'response_time': duration})
        else:
            self.logger.error(f"Failed {self.operation_name}: {exc_val}", 
                            exc_info=True, extra={'response_time': duration})
        
        self.logger.clear_context()
        
        # Re-raise the exception if one occurred
        return False


class FunctionCallTracker:
    """Context manager for tracking Gemini function calls."""
    
    def __init__(self, logger: ContextualLogger, function_name: str, args: dict):
        self.logger = logger
        self.function_name = function_name
        self.args = args
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.set_context(function_call=self.function_name)
        self.logger.info(f"Executing function call: {self.function_name}", 
                        extra={'function_args': self.args})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Function call {self.function_name} completed successfully", 
                           extra={'response_time': duration})
        else:
            self.logger.error(f"Function call {self.function_name} failed: {exc_val}", 
                            exc_info=True, extra={'response_time': duration})
        
        self.logger.clear_context()
        return False


# Global logging configuration instance
logging_config = LoggingConfig()

# Convenience functions for getting specialized loggers
def get_logger(name: str) -> ContextualLogger:
    """Get a contextual logger for any module."""
    return logging_config.get_logger(name)

def get_function_call_logger() -> ContextualLogger:
    """Get the function call logger."""
    return logging_config.get_function_call_logger()

def get_api_logger() -> ContextualLogger:
    """Get the API logger."""
    return logging_config.get_api_logger()

def get_chart_logger() -> ContextualLogger:
    """Get the chart generation logger."""
    return logging_config.get_chart_logger()

# Export key classes and functions
__all__ = [
    'get_logger',
    'get_function_call_logger', 
    'get_api_logger',
    'get_chart_logger',
    'LoggedOperation',
    'FunctionCallTracker',
    'ContextualLogger'
]