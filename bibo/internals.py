# coding=utf-8

import collections
import itertools
import os
import shutil
import subprocess
import sys

import click


def header(entry):
    parts = [click.style(entry['key'], fg='green')]
    fields = entry['fields']
    if fields.get('tags'):
        parts.append(click.style(fields['tags'], fg='cyan'))
    if fields.get('file'):
        parts.append('📁')
    if fields.get('url'):
        parts.append('🔗')
    return ' '.join(parts)


def open_file(filepath):
    """
    Open file with the default system app.
    Copied from https://stackoverflow.com/a/435669/1224456
    """
    if sys.platform.startswith('darwin'):
        subprocess.Popen(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.Popen(('xdg-open', filepath))


def destination_heuristic(data):
    """
    A heuristic to get the folder with all other files from bib, using majority
    vote.
    """
    counter = collections.Counter()
    for entry in data:
        file_field = entry['fields'].get('file')
        if not file_field:
            continue
        path = os.path.dirname(file_field)
        counter[path] += 1

    if not counter:  # No paths found
        raise click.ClickException(
            'Path finding heuristics failed: no paths in the database'
        )

    # Find the paths that appears most often
    sorted_paths = sorted(counter, reverse=True)
    groupby = itertools.groupby(sorted_paths, key=len)
    _, group = next(groupby)

    # We know that there's at least one candidate. Make sure it's
    # the only one
    candidate = next(group)
    try:
        next(group)
    except StopIteration:
        return candidate
    else:
        raise click.ClickException(
            'Path finding heuristics failed: '
            'there are multiple equally valid paths in the database'
        )


def remove_entry(data, entry):
    '''
    Remove an entry in place.
    '''
    file_field = entry['fields'].get('file')
    if file_field:
        try:
            os.remove(file_field)
        except IOError:
            click.echo('This entry\'s file was missing')

    data.remove(entry)


def set_file(data, entry, file_, destination=None):
    if not destination:
        destination = destination_heuristic(data)
    _, file_extension = os.path.splitext(file_)
    path = os.path.join(destination, entry['key'] + file_extension)
    entry['fields']['file'] = path
    shutil.copy(file_, path)


def editor(*args, **kwargs):
    '''
    Wrapper for `click.edit` that raises an error when None is returned.
    '''
    result = click.edit(*args, **kwargs)
    if result is None:
        msg = 'Editor exited without saving, command aborted'
        raise click.ClickException(msg)
    return result
