import os
import re
import sys
import warnings

try:
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    class ImproperlyConfigured(Exception):
        pass

from fabric.api import local
from fabric.colors import yellow as _yellow


line_re = re.compile(r"""
    ^
    (?:export\s+)?      # optional export
    ([\w\.]+)           # key
    (?:\s*=\s*|:\s+?)   # separator
    (                   # optional value begin
        '(?:\'|[^'])*'  #   single quoted value
        |               #   or
        "(?:\"|[^"])*"  #   double quoted value
        |               #   or
        [^#\n]+         #   unquoted value
    )?                  # value end
    (?:\s*\#.*)?        # optional comment
    $
""", re.VERBOSE)

variable_re = re.compile(r"""
    (\\)?               # is it escaped with a backslash?
    (\$)                # literal $
    (                   # collect braces with var for sub
        \{?             #   allow brace wrapping
        ([A-Z0-9_]+)    #   match the variable
        \}?             #   closing brace
    )                   # braces end
""", re.IGNORECASE | re.VERBOSE)


def read_dotenv(dotenv=None, set_heroku=False):
    """
    Read a .env file into os.environ.

    If not given a path to a dotenv path, does filthy magic stack backtracking
    to find manage.py and then find the dotenv.
    """
    if dotenv is None:
        frame_filename = sys._getframe().f_back.f_code.co_filename
        dotenv = os.path.join(os.path.dirname(frame_filename), '.env')

    if os.path.isdir(dotenv) and os.path.isfile(os.path.join(dotenv, '.env')):
        dotenv = os.path.join(dotenv, '.env')

    if os.path.exists(dotenv):
        with open(dotenv) as f:
            for k, v in parse_dotenv(f.read()).items():
                try:
                    os.environ.setdefault(k, v)

                    if set_heroku and v:
                        print(_yellow('Setting {}...'.format(k)))
                        local("heroku config:set {0}='{1}'".format(k, v))
                except KeyError:
                    error_msg = "Set the {} environment variable".format(k)
                    raise ImproperlyConfigured(error_msg)
    else:
        warnings.warn("Not reading {} - it doesn't exist.".format(dotenv),
                      stacklevel=2)


def parse_dotenv(content):
    env = {}

    for line in content.splitlines():
        m1 = line_re.search(line)

        if m1:
            key, value = m1.groups()

            if value is None:
                value = ''

            # Remove leading/trailing whitespace
            value = value.strip()

            # Remove surrounding quotes
            m2 = re.match(r'^([\'"])(.*)\1$', value)

            if m2:
                quotemark, value = m2.groups()
            else:
                quotemark = None

            # Unescape all chars except $ so variables can be escaped properly
            if quotemark == '"':
                value = re.sub(r'\\([^$])', r'\1', value)

            if quotemark != "'":
                # Substitute variables in a value
                for parts in variable_re.findall(value):
                    if parts[0] == '\\':
                        # Variable is escaped, don't replace it
                        replace = ''.join(parts[1:-1])
                    else:
                        # Replace it with the value from the environment
                        replace = env.get(
                            parts[-1],
                            os.environ.get(parts[-1], '')
                        )

                    value = value.replace(''.join(parts[0:-1]), replace)

            env[key] = value

        elif not re.search(r'^\s*(?:#.*)?$', line):  # not comment or blank
            warnings.warn(
                "Line {} doesn't match format".format(repr(line)),
                SyntaxWarning
            )

    return env
