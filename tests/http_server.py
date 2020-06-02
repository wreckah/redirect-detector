from contextlib import ContextDecorator
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


DEFAULT_URLS = {
    '/': {
        'status_code': 200,
        'body': 'OK',
    }
}

class HttpServerMixin(object):
    """
    Mixin class for test cases which set up HTTP server in a separate thread
    in setUp and turn it down on tearDown. Provides server's URL in self.base_url.
    """
    def setUp(self):
        self._http_server = HttpServer(
            ('127.0.0.1', 0),
            http_handler_factory(DEFAULT_URLS)
        )
        self._http_thread = Thread(None, self._http_server.run)
        self._http_thread.start()
        self.base_url = 'http://127.0.0.1:%d' % (
            self._http_server.server_address[1]
        )

    def tearDown(self):
        self._http_server.shutdown()
        self._http_thread.join()


class HttpServer(HTTPServer):
    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()


def http_handler_factory(urls: object):
    """Creates HttpHandler class used by HttpServer with new urls config."""
    class HttpHandler(BaseHTTPRequestHandler):

        def do_GET(self):
          """Handles HTTP GET requests according to urls config."""
          url = urls.get(self.path)
          if not url:
              self.send_response_only(404)
              self.end_headers()
              return self.wfile.write('Not found'.encode('utf-8'))

          self.send_response_only(url.get('status_code', 200))
          for header, value in url.get('headers', {}).items():
              self.send_header(header, value)
          self.end_headers()

          body = url.get('body', '')
          if callable(body):
              for chunk in body():
                  try:
                      self.wfile.write(chunk.encode('utf-8'))
                  except (ConnectionResetError, BrokenPipeError) as err:
                      return
          else:
              self.wfile.write(body.encode('utf-8'))

    return HttpHandler


def http_responses(urls: object):
    """
    Closure with urls config.

    Arguments:
        urls {object} -- Config of served URLs, looks like {
            'url': {
                'status_code': 200,
                'header': {'Content-type': 'text/html'},
                'body': '<html></html>',
            }
        }
    """
    def _wrapper(func):

      def wrapper(self, *args, **kwargs):
          """Patch TestCase with HttpServerMixin by new HttpHandler with urls config."""
          original_handler = self._http_server.RequestHandlerClass
          self._http_server.RequestHandlerClass = http_handler_factory(urls)
          try:
              return func(self, *args, **kwargs)
          finally:
              self._http_server.RequestHandlerClass = original_handler

      return wrapper

    return _wrapper
