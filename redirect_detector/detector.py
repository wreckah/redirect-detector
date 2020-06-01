"""
Redirect detector

Using requests lib allows to make HTTP requests easily, but it's quite
outdated approach. It doesn't support HTTP/2 and non blocking I/O.
We should consider to use:
  - https://github.com/aio-libs/aiohttp (async)
  - https://github.com/python-hyper/hyper (http2)
  - https://github.com/encode/httpx (http2, async)
"""
from urllib.parse import urlparse, urlunparse
import logging
import requests

from .errors import (
    LoopedRedirectsError, MaxRedirectsSizeError,
    MaxResponseSizeError, NoLocationError
)
from .config import (
    LOG_LEVEL, MAX_BODY_SIZE, MAX_REDIRECTS, READ_CHUNK_SIZE
)


logging.basicConfig(level = getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)


def detect(url: str,
           max_redirects: int = MAX_REDIRECTS,
           max_body_size: int = MAX_BODY_SIZE,
           **requests_params) -> str:
    """
    Detect a final URL in redirects chain.

    Arguments:
        url {str} -- Initial URL to detect redirects from.

    Keyword Arguments:
        max_redirects {int} -- Max number of redirects allowed (default: 10)
        max_body_size {int} -- Max body size, helps to prevent a bandwith
                               attack and blocking of worker (default: 1024)

    Raises:
        Exception: [description]
        Exception: [description]

    Returns:
        str -- [description]
    """
    logger.debug('Start processing %s', url)
    requests_params['allow_redirects'] = False
    count = 1
    history = set()

    while True:
        resp = _read_url(url, max_body_size, **requests_params)
        if resp.status_code < 300 or resp.status_code > 400:
            logger.debug('Finished with %s', url)
            return resp.url

        url = _parse_location(resp.headers.get('location'), resp.url)
        logger.debug('Redirect found %s', url)
        if url in history:
            raise LoopedRedirectsError()
        history.add(url)

        count += 1
        if count > max_redirects:
            raise MaxRedirectsSizeError()


def _read_url(url: str, max_body_size: int, **requests_params) -> requests.models.Response:
    """
    Read URL by requests lib as a stream and try to read data
    for non redirecting responses.

    Arguments:
        url {str} --           URL to read from
        max_body_size {int} -- Max body size allowed to read

    Raises:
        MaxResponseSizeError: When response's body is to huge.

    Returns:
        requests.models.Response -- HTTP response
    """
    requests_params['stream'] = True

    # We can use HEAD request instead of GET to get HTTP status code
    # and Location header, but some HTTP servers do not support HEAD method.
    with requests.get(url, **requests_params) as resp:
        logger.debug('GET %s', url)
        if 300 <= resp.status_code < 400:
            # Do not try to read body of redirects.
            return resp

        read = 0
        while True:
            data = resp.raw.read(READ_CHUNK_SIZE)
            if not data:
                break
            logger.debug('Read %s bytes of response', len(data))
            read += len(data)
            if read > max_body_size:
                raise MaxResponseSizeError()
        return resp


def _parse_location(location: str, request_url: str) -> str:
    """
    Help to extract location from HTTP headers,
    add shema and host to relative URLs.

    Arguments:
        location {str}    -- Location HTTP header
        request_url {str} -- URL of original request

    Raises:
        NoLocationError: When no Location header found with
                         redirect HTTP status.

    Returns:
        str -- URL prepared for the next request.
    """
    if not location:
        raise NoLocationError()

    if not location.startswith('/'):
        return location

    parts = list(urlparse(request_url))[0:2]
    parts.append(location)
    return '%s://%s%s' % tuple(parts)
