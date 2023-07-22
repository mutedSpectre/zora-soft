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
#
# @section todo_logger TODO
# - copy from logger
#
# @section author_logger Author(s)
# - Created by mutedspectre.eth on 07/20/2023.
# - Modified by mutedspectre.eth on 07/21/2023.
#
# Copyright (c) 2023 mutedspectre.eth. All rights reserved.

from dearpygui_ext import logger

class Logger:
    """ The logger base class."""

    def create_logger(self):
        """! Render logger window in parent window."""

        self.logz = logger.mvLogger(parent='logger')
    
    def info_log(self, address, text):
        """! Send a log message to the info level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.logz.log_info(f"{addr} | {text}\n")
    
    def all_info_log(self, text):
        """! Send a log message to the info level without address.

        @param text The text for log message
        """

        self.logz.log_info(f"{text}\n")

    def warning_log(self, address, text):
        """! Send a log message to the warn level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.logz.log_warning(f"{addr} | {text}\n")

    def error_log(self, address, text):
        """! Send a log message to the error level.

        @param address The address of account
        @param text    The text for log message
        """

        addr = address[:6] + '...' + address[-4:]
        self.logz.log_error(f"{addr} | {text}\n")
