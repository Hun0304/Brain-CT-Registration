"""
my project logger class
"""

import logging
from logging import Logger


class AppLayerLogger:
    """
    Logger in the application layer.
    """
    def __init__(self, name: str, level=logging.NOTSET):
        """
        Init the logger.
        """
        self.__logger = Logger(name=name, level=level)
        prefix_handler = logging.StreamHandler()
        prefix_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        prefix_handler.setFormatter(prefix_formatter)
        self.__logger.addHandler(prefix_handler)

    def get_logger(self) -> Logger:
        """
        :return: the logger.
        """
        return self.__logger

