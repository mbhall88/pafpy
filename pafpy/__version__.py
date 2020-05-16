import re
import subprocess


def get_version() -> str:
    result = subprocess.run(["poetry", "version"], stdout=subprocess.PIPE)
    regex = re.compile(r"(?P<version>\d.\d.\d)")
    match = regex.search(result.stdout.decode())
    if match is None:
        return "Could not retrieve version number."
    return match.group("version")


__version__ = get_version()
