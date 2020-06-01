from collections import ChainMap
from os import environ

config = ChainMap(environ, {
  'READ_CHUNK_SIZE': 64 * 1024,  # Chunk size for reading request's body.
  'MAX_REDIRECTS': 10,
  'MAX_BODY_SIZE': 1024 * 1024 * 1024,  # 1 Megabyte
  'LOG_LEVEL': 'ERROR',
})

READ_CHUNK_SIZE = config['READ_CHUNK_SIZE']
MAX_REDIRECTS = config['MAX_REDIRECTS']
MAX_BODY_SIZE = config['MAX_BODY_SIZE']
LOG_LEVEL = config['LOG_LEVEL']
