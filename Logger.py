"""! @brief Defines the logger class."""
##
# @file Logger.py
#
# @brief Defines the logger class.
#
# @section description_logger Description
# Defines the logger class, which render the logger gui, and allows you to send messages to it
#
# @section libraries_logger Libraries/Modules
# - access to logger extension from gui library
# - access to logging module
#
# @section author_logger Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/26/2023.

from dearpygui.dearpygui import inspect
from dearpygui_ext import logger
import logging

class Logger:
    """ The logger base class."""

    def create_logger(self, logger_name):
        """ Render logger window in parent window."""

        # Create local logger
        self.logger_name = logger_name
        self.file_logger = logging.getLogger(self.logger_name)
        self.file_logger.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] -> %(message)s')

        file_handler = logging.FileHandler('logs.log')
        file_handler.setFormatter(formatter)

        self.file_logger.addHandler(file_handler)

        # Create window logger
        self.logz = logger.mvLogger(parent='logger')
    
    def info_log(self, address, text):
        """ Send a log message to the info level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.file_logger.info(f"[{self.logger_name}] {addr} | {text}")
        self.logz.log_info(f"{addr} | {text}\n")
    
    def all_info_log(self, text):
        """ Send a log message to the info level without address.

        @param text The text for log message
        """

        self.file_logger.info(f"[{self.logger_name}] {text}")
        self.logz.log_info(f"{text}\n")

    def warning_log(self, address, text):
        """ Send a log message to the warn level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.file_logger.warning(f"[{self.logger_name}] {addr} | {text}")
        self.logz.log_warning(f"{addr} | {text}\n")

    def error_log(self, address, text):
        """ Send a log message to the error level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.file_logger.error(f"[{self.logger_name}] {addr} | {text}")
        self.logz.log_error(f"{addr} | {text}\n")

    def all_error_log(self, text):
        """ Send a log message to the error level.

        @param text    The text for log message
        """

        self.file_logger.error(f"[{self.logger_name}] {text}")
        self.logz.log_error(f"{text}\n")