"""Mesos file/logging functionality.

This file is copied almost entirely from dcoscli here:
https://github.com/mesosphere/dcos-cli/blob/3e53965b7ff5573f0cc6726e08c048382cd911e5/cli/dcoscli/log.py

This is the only part of the dcoscli library that shpkpr depends on and so
it's easier to copy it all and drop the dcoscli dependency. This module also
swaps dcoscli's emmitter pattern in favour of using click's logger (via a
context object).
"""
# stdlib imports
import functools
import itertools
import os
import sys
import time

# third-party imports
from dcos import util
from dcos.errors import DCOSException


def _no_file_exception():
    return DCOSException('No files exist. Exiting.')


def log_files(logger, mesos_files, follow, lines):
    """Print the contents of the given `mesos_files`.  Behaves like unix
    tail.
    """
    line_prefixes = _line_prefixes(mesos_files)
    fn = functools.partial(_read_last_lines, lines)
    mesos_files = _stream_files(logger, fn, mesos_files, line_prefixes)
    if not mesos_files:
        raise _no_file_exception()

    while follow:
        # This flush is needed only for testing, since stdout is fully
        # buffered (as opposed to line-buffered) when redirected to a
        # pipe.  So if we don't flush, our --follow tests, which use a
        # pipe, never see the data
        sys.stdout.flush()

        mesos_files = _stream_files(logger,
                                    _read_rest,
                                    mesos_files,
                                    line_prefixes)
        if not mesos_files:
            raise _no_file_exception()
        time.sleep(1)


def _line_prefixes(mesos_files):
    """Generate the shortest possible line prefixes to prepend to log lines.
    """
    file_ids = [str(y) for y in mesos_files]
    common_prefix = os.path.commonprefix(file_ids)
    common_suffix = os.path.commonprefix([x[::-1] for x in file_ids])[::-1]

    prefixes = {}
    colours = itertools.cycle(["red", "green", "yellow", "blue", "magenta", "cyan"])
    for f, colour in zip(mesos_files, colours):
        prefixes[str(f)] = (
            str(f).replace(common_prefix, "").replace(common_suffix, ""),
            colour,
        )

    return prefixes


def _stream_files(logger, fn, mesos_files, line_prefixes):
    """Apply `fn` in parallel to each file in `mesos_files`.  `fn` must
    return a list of strings, and these strings are then printed
    serially as separate lines.
    """
    reachable_files = list(mesos_files)

    # TODO switch to map
    for job, mesos_file in util.stream(fn, mesos_files):
        try:
            lines = job.result()
        except DCOSException:
            # The read function might throw an exception if read.json
            # is unavailable, or if the file doesn't exist in the
            # sandbox.  In any case, we silently remove the file and
            # continue.
            reachable_files.remove(mesos_file)
            continue

        if lines:
            _output(logger,
                    str(mesos_file),
                    lines,
                    line_prefixes)

    return reachable_files


def _output(logger, file_id, lines, prefixes):
    """Prints a sequence of lines.
    """
    if lines:
        for line in lines:
            if not prefixes.get(file_id, [None])[0]:
                logger.log(line)
            else:
                logger.log(
                    '%s %s',
                    logger.style('[{}]'.format(prefixes[file_id][0]), fg=prefixes[file_id][1]),
                    line,
                )


# A liberal estimate of a line size.  Used to estimate how much data
# we need to fetch from a file when we want to read N lines.
LINE_SIZE = 200


def _read_last_lines(num_lines, mesos_file):
    """Returns the last `num_lines` of a file, or less if the file is
    smaller.  Seeks to EOF.
    """
    file_size = mesos_file.size()

    # estimate how much data we need to fetch to read `num_lines`.
    fetch_size = LINE_SIZE * num_lines

    end = file_size
    start = max(end - fetch_size, 0)
    data = ''
    while True:
        # fetch data
        mesos_file.seek(start)
        data = mesos_file.read(end - start) + data

        # break if we have enough lines
        data_tmp = _strip_trailing_newline(data)
        lines = data_tmp.split('\n')
        if len(lines) > num_lines:
            ret = lines[-num_lines:]
            break
        elif start == 0:
            ret = lines
            break

        # otherwise shift our read window and repeat
        end = start
        start = max(end - fetch_size, 0)

    mesos_file.seek(file_size)
    return ret


def _read_rest(mesos_file):
    """ Reads the rest of the file, and returns the lines.
    """
    data = mesos_file.read()
    if data == '':
        return []
    else:
        data_tmp = _strip_trailing_newline(data)
        return data_tmp.split('\n')


def _strip_trailing_newline(s):
    """Returns a modified version of the string with the last character
    truncated if it's a newline.
    """

    if s == "":
        return s
    else:
        return s[:-1] if s[-1] == '\n' else s
