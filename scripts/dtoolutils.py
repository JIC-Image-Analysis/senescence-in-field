"""Helper functions for working with datasets."""

import shutil
import tempfile

from contextlib import contextmanager

TMPDIR_PREFIX = '/tmp'


@contextmanager
def temp_working_dir():
    working_dir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

    try:
        yield working_dir
    finally:
        shutil.rmtree(working_dir)
