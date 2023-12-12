import logging

from ..utils.env_vars import PWD

class Logger:
    LOG_PATH = f"{PWD}/autoscaler.log"

    logging.basicConfig(filename=LOG_PATH,
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


    @staticmethod
    def warning(message):
        logging.warning(message)

    
    @staticmethod
    def debug(message):
        logging.debug(message)

    
    @staticmethod
    def info(message):
        logging.info(message)

    
    @staticmethod
    def error(message):
        logging.error(message)