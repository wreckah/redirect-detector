from unittest import TestCase
from redirect_detector.detector import detect
from redirect_detector.errors import (
  LoopedRedirectsError, MaxRedirectsSizeError, MaxResponseSizeError
)
from .http_server import HttpServerMixin, http_responses


def endless_body():
    """Generator of endless response body"""
    while True:
        yield 'a' * 1024


class DetectorTestCase(HttpServerMixin, TestCase):

    def test_no_redirects(self):
        url = self.base_url + '/'
        self.assertEqual(detect(url), url)

    @http_responses({
        '/redirect1': {
            'status_code': 301,
            'headers': {'location': '/redirect2'},
        },
        '/redirect2': {
            'status_code': 301,
            'headers': {'location': '/document'},
        },
        '/document': {
            'status_code': 200,
        },
    })
    def test_redirects(self):
        url = self.base_url + '/redirect1'
        self.assertEqual(detect(url), self.base_url + '/document')

    @http_responses({
        '/redirect1': {
            'status_code': 301,
            'headers': {'location': '/redirect2'},
        },
        '/redirect2': {
            'status_code': 301,
            'headers': {'location': '/redirect1'},
        },
    })
    def test_looped_redirects(self):
        with self.assertRaises(LoopedRedirectsError):
            detect(self.base_url + '/redirect1')

    @http_responses({
        '/redirect%d' % (i + 1): {
            'status_code': 301,
            'headers': {'location': '/redirect%d' % (i + 2)},
    } for i in range(10)})
    def test_max_redirects_exceeded(self):
        with self.assertRaises(MaxRedirectsSizeError):
            detect(self.base_url + '/redirect1')

    @http_responses({
        '/endless': {
            'status_code': 200,
            'body': endless_body,
        }
    })
    def test_endless_body(self):
        with self.assertRaises(MaxResponseSizeError):
            detect(self.base_url + '/endless')

    @http_responses({
        '/endless_redirect': {
            'status_code': 307,
            'headers': {'location': '/document'},
            'body': endless_body,
        },
        '/document': {
            'status_code': 200,
        },
    })
    def test_redirect_endless_body(self):
        url = self.base_url + '/endless_redirect'
        self.assertEqual(detect(url), self.base_url + '/document')
