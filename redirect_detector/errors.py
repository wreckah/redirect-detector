class UrlDetectorError(Exception):
    pass


class NoLocationError(UrlDetectorError):
    def __init__(self):
        self.message = 'No Location header with redirect status'


class MaxResponseSizeError(UrlDetectorError):
    def __init__(self):
        self.message = 'Max response size exceeded'


class MaxRedirectsSizeError(UrlDetectorError):
    def __init__(self):
        self.message = 'Max redirects exceeded'


class LoopedRedirectsError(UrlDetectorError):
    def __init__(self):
        self.message = 'Looped redirects detected'
