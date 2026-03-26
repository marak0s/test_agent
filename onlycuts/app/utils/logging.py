import logging

import structlog


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
