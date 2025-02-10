import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(threadName)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Print to console
    ]
)

logger = logging.getLogger(__name__)
