import sys
from .detector import detect
from .errors import UrlDetectorError


if len(sys.argv) > 1:
    try:
        sys.stdout.write(detect(sys.argv[-1]))
    except Exception as err:
        sys.stderr.write(str(err))
        exit(1)
else:
    sys.stdout.write('Usage: python3 -m redirect-detector http://w3c.org')
    exit(1)
