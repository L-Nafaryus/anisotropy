import logging
import config

class Logger():
    def __init__(self):
        logging.basicConfig(
            level = logging.INFO, 
            format = "%(levelname)s: %(message)s",
            handlers = [
                logging.StreamHandler(),
                logging.FileHandler(f"{config.LOG}/anisotrope.log")
            ]
        )

        self.logger = logging.getLogger("anisotrope")
        self.warnings = 0
        self.errors = 0
        self.criticals = 0
        self.exceptions = 0
        
    def info(self, *args):
        self.logger.info(*args)

    def warning(self, *args):
        self.warnings += 1
        self.logger.warning(*args)

    def error(self, *args):
        self.errors += 1
        self.logger.error(*args)

    def critical(self, *args):
        self.criticals += 1
        self.logger.critical(*args)

    def exception(self, *args):
        self.exceptions += 1
        self.logger.exception(*args)

    def fanctline(self):
        self.logger.info("-" * 80)
