from __future__ import print_function

import glob
import inspect
import os
import random
import re
import shutil
import tempfile
# import pip
import time
from contextlib import contextmanager
import collections

try:
    collectionsAbc = collections.abc
except AttributeError:
    collectionsAbc = collections

try:
    from pathlib import Path
except:
    from pathlib2 import Path

from six.moves import input

from cloudmesh.common.console import Console


@contextmanager
def tempdir(*args, **kwargs):
    """A contextmanager to work in an auto-removed temporary directory

    Arguments are passed through to tempfile.mkdtemp

    example:

    >>> with tempdir() as path:
    ...    pass
    """

    d = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield d
    finally:
        shutil.rmtree(d)


def exponential_backoff(fn, sleeptime_s_max=30 * 60):
    """Calls `fn` until it returns True, with an exponentially increasing wait time between calls"""

    sleeptime_ms = 500
    while True:
        if fn():
            return True
        else:
            print('Sleeping {} ms'.format(sleeptime_ms))
            time.sleep(sleeptime_ms / 1000.0)
            sleeptime_ms *= 2

        if sleeptime_ms / 1000.0 > sleeptime_s_max:
            return False


def search(lines, pattern):
    """
    return all lines that match the pattern
    #TODO: we need an example
    
    :param lines: 
    :param pattern: 
    :return: 
    """
    p = pattern.replace("*", ".*")
    test = re.compile(p)
    result = []
    for l in lines:
        if test.search(l):
            result.append(l)
    return result


def grep(pattern, filename):
    """Very simple grep that returns the first matching line in a file.
    String matching only, does not do REs as currently implemented.
    """
    try:
        # for line in file
        # if line matches pattern:
        #    return line
        return next((L for L in open(filename) if L.find(pattern) >= 0))
    except StopIteration:
        return ''

def is_gitbash():
    try:
        exepath = os.environ['EXEPATH']
        return "Git" in exepath
    except:
        return False

def is_cmd_exe():
    if is_gitbash():
        return False
    else:
        try:
            return os.environ['OS'] == 'Windows_NT'
        except:
            return False

def path_expand(text):
    """ returns a string with expanded variable.

    :param text: the path to be expanded, which can include ~ and environment variables
    :param text: string

    """
    result = os.path.expandvars(os.path.expanduser(text))

    if result.startswith("."):
        result = result.replace(".", os.getcwd(), 1)

    if is_gitbash() or is_cmd_exe():
        result = result.replace("/", "\\")

    return result

def convert_from_unicode(data):
    """
    converts unicode data to a string
    :param data: the data to convert
    :return: 
    """
    # if isinstance(data, basestring):

    if isinstance(data, str):
        return str(data)
    elif isinstance(data, collectionsAbc.Mapping):
        return dict(map(convert_from_unicode, data.items()))
    elif isinstance(data, collectionsAbc.Iterable):
        return type(data)(map(convert_from_unicode, data))
    else:
        return data


def yn_choice(message, default='y', tries=None):
    """asks for a yes/no question.

    :param tries: the number of tries
    :param message: the message containing the question
    :param default: the default answer
    """
    # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input"""
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    if tries is None:
        choice = input("%s (%s) " % (message, choices))
        values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
        return True if choice.strip().lower() in values else False
    else:
        while tries > 0:
            choice = input(
                "%s (%s) (%s)" % (message, choices, "'q' to discard"))
            choice = choice.strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no', 'q']:
                return False
            else:
                print("Invalid input...")
                tries -= 1


def banner(txt=None, c="-", prefix="#", debug=True, label=None, color=None):
    """
    prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    :param color: prints in the given color
    :param label: adds a label
    :param debug: prints only if debug is true
    :param txt: a text message to be printed
    :type txt: string
    :param c: the character used instead of c
    :type c: character
    """
    output = ""
    if debug:
        output = "\n"
        output += prefix + " " + 70 * c + "\n"
        if label is not None:
            output += prefix + " " + label + "\n"
            output += prefix + " " + 70 * c + "\n"
        if txt is not None:
            for line in txt.split("\n"):
                output += prefix + " " + line + "\n"
            output += prefix + " " + 70 * c + "\n"
    if color is None:
        color = "BLUE"

    Console.cprint(color, "", output)


def str_banner(txt=None, c="-", prefix= "#", debug=True, label=None, color=None):
    """
    prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    :param color: prints in the given color
    :param label: adds a label
    :param debug: prints only if debug is true
    :param txt: a text message to be printed
    :type txt: string
    :param c: the character used instead of c
    :type c: character
    """
    output = ""
    if debug:
        output = "\n"
        output += prefix + " " + 70 * c + "\n"
        if label is not None:
            output += prefix + " " + label + "\n"
            output += prefix + " " + 70 * c + "\n"
        if txt is not None:
            for line in txt.split("\n"):
                output += prefix + " " + line + "\n"
            output += prefix + " " + 70 * c + "\n"
    if color is None:
        color = "BLUE"

    return output




# noinspection PyPep8Naming
def HEADING(txt=None, c="#", color="HEADER"):
    """
    Prints a message to stdout with #### surrounding it. This is useful for
    pytests to better distinguish them.

    :param c: uses the given char to wrap the header
    :param txt: a text message to be printed
    :type txt: string
    """
    frame = inspect.getouterframes(inspect.currentframe())

    filename = frame[1][1].replace(os.getcwd(), "")
    line = frame[1][2] - 1
    method = frame[1][3]
    if txt is None:
        msg = "{} {} {}".format(method, filename, line)
    else:
        msg = "{}\n {} {} {}".format(txt, method, filename, line)


    print()
    banner(msg, c=c, color=color)


def backup_name(filename):
    """
    :param filename: given a filename creates a backup name of the form
                     filename.bak.1. If the filename already exists
                     the number will be increased as  much as needed so
                     the file does not exist in the given location.
                     The filename can consists a path and is expanded
                     with ~ and environment variables.
    :type filename: string
    :rtype: string
    """
    location = path_expand(filename)
    n = 0
    found = True
    backup = None
    while found:
        n += 1
        backup = "{0}.bak.{1}".format(location, n)
        found = os.path.isfile(backup)
    return backup


def auto_create_version(class_name, version, filename="__init__.py"):
    """
    creates a version number in the __init__.py file.
    it can be accessed with __version__
    :param class_name: 
    :param version: 
    :param filename: 
    :return: 
    """
    version_filename = Path(
        "{classname}/{filename}".format(classname=class_name,
                                        filename=filename))
    with open(version_filename, "r") as f:
        content = f.read()

    if content != '__version__ = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open(version_filename, "w") as text_file:
            text_file.write('__version__ = "{0:s}"'.format(version))


def auto_create_requirements(requirements):
    """

    creates a requirement.txt file form the requirements in the list. If the file
    exists, it get changed only if the
    requirements in the list are different from the existing file

    :param requirements: the requirements in a list
    """
    banner("Creating requirements.txt file")
    try:
        with open("requirements.txt", "r") as f:
            file_content = f.read()
    except:
        file_content = ""

    setup_requirements = '\n'.join(requirements)

    if setup_requirements != file_content:
        with open("requirements.txt", "w") as text_file:
            text_file.write(setup_requirements)


def copy_files(files_glob, source_dir, dest_dir):
    """
    copies the files to the destination

    :param files_glob: \*.yaml
    :param source_dir: source directory
    :param dest_dir: destination directory

    """

    files = glob.iglob(os.path.join(source_dir, files_glob))
    for filename in files:
        if os.path.isfile(filename):
            shutil.copy2(filename, dest_dir)


def readfile(filename):
    """
    returns the content of a file
    :param filename: the filename
    :return: 
    """
    with open(path_expand(filename), 'r') as f:
        content = f.read()
    return content


def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return: 
    """
    with open(path_expand(filename), 'w') as outfile:
        outfile.write(content)


# Reference: http://interactivepython.org/runestone/static/everyday/2013/01/3_password.html
def generate_password(length=8, lower=True, upper=True, number=True):
    """
    generates a simple password. We should not really use this in production.
    :param length: the length of the password
    :param lower: True of lower case characters are allowed
    :param upper: True if upper case characters are allowed
    :param number: True if numbers are allowed
    :return: 
    """
    lletters = "abcdefghijklmnopqrstuvwxyz"
    uletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # This doesn't guarantee both lower and upper cases will show up
    alphabet = lletters + uletters
    digit = "0123456789"
    mypw = ""

    def _random_character(texts):
        return texts[random.randrange(len(texts))]

    if not lower:
        alphabet = uletters
    elif not upper:
        alphabet = lletters

    for i in range(length):
        # last half length will be filled with numbers
        if number and i >= int(length / 2):
            mypw = mypw + _random_character(digit)
        else:
            mypw = mypw + _random_character(alphabet)
    return mypw
