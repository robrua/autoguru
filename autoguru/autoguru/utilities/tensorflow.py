import os
from contextlib import contextmanager
from typing import Iterator

TF_LOG_LEVEL: str = "TF_CPP_MIN_LOG_LEVEL"
ERROR_LOG_LEVEL: str = "3"


@contextmanager
def surpress_verbose_logging() -> Iterator[None]:
    log_level = os.environ.get(TF_LOG_LEVEL)
    os.environ[TF_LOG_LEVEL] = "3"

    yield

    if log_level is not None:
        os.environ[TF_LOG_LEVEL] = log_level
    else:
        del os.environ[TF_LOG_LEVEL]
