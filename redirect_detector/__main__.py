from sys import argv
from .detector import detect


if len(argv) > 1:
    print(detect(argv[-1]))
else:
    print('Usage: python3 -m redirect-detector http://w3c.org')
