import logging
import os


class Logger:
    log_directory = "logs"
    log_file = "logs.log"

    @staticmethod
    def setup_logging():
        # Check the logs file, if not exist then create a new one
        if not os.path.exists(Logger.log_directory):
            os.makedirs(Logger.log_directory)

        # Set log config
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.path.join('logs', 'logs.log'),
            filemode='a'
        )

        # For showing logs on console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

        logging.info("Logging setup complete.")