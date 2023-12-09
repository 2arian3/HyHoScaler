import logging

class Logger:
    LOG_PATH = './app.log'

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