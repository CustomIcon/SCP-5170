# https://github.com/sivel/speedtest-cli but async
from io import TextIOWrapper, FileIO
import builtins
from io import StringIO, BytesIO
from hashlib import md5
from urllib.parse import parse_qs
from urllib.parse import urlparse
from http.client import HTTPConnection, BadStatusLine, HTTPSConnection
from urllib.request import (
    urlopen, Request, HTTPError, URLError,
    AbstractHTTPHandler, ProxyHandler,
    HTTPDefaultErrorHandler, HTTPRedirectHandler,
    HTTPErrorProcessor, OpenerDirector,
)
import ujson as json
import os
import re
import csv
import sys
import math
import socket
import timeit
import logging
import asyncio
import datetime
import platform
import threading
import xml.parsers.expat
from typing import Tuple
import gzip
GZIP_BASE = gzip.GzipFile
DEBUG = False
_GLOBAL_DEFAULT_TIMEOUT = object()
PY25PLUS = sys.version_info[:2] >= (2, 5)
PY26PLUS = sys.version_info[:2] >= (2, 6)
PY32PLUS = sys.version_info[:2] >= (3, 2)
logger = logging.getLogger()
try:
    import xml.etree.ElementTree as ET
    try:
        from xml.etree.ElementTree import _Element as ET_Element
    except ImportError:
        pass
except ImportError:
    from xml.dom import minidom as DOM
    from xml.parsers.expat import ExpatError
    ET = None


PARSER_TYPE_INT = int
PARSER_TYPE_STR = str
PARSER_TYPE_FLOAT = float


class _Py3Utf8Output(TextIOWrapper):
    """UTF-8 encoded wrapper around stdout for py3, to override
    ASCII stdout
    """

    def __init__(self, f, **kwargs):
        buf = FileIO(f.fileno(), 'w')
        super().__init__(
            buf,
            encoding='utf8',
            errors='strict',
        )

    def write(self, s):
        super().write(s)
        self.flush()


_py3_print = getattr(builtins, 'print')
try:
    _py3_utf8_stdout = _Py3Utf8Output(sys.stdout)
    _py3_utf8_stderr = _Py3Utf8Output(sys.stderr)
except OSError:
    # sys.stdout/sys.stderr is not a compatible stdout/stderr object
    # just use it and hope things go ok
    _py3_utf8_stdout = sys.stdout
    _py3_utf8_stderr = sys.stderr


def to_utf8(v):
    """No-op encode to utf-8 for py3"""
    return v


def print_(*args, **kwargs):
    """Wrapper function for py3 to print, with a utf-8 encoded stdout"""
    if kwargs.get('file') == sys.stderr:
        kwargs['file'] = _py3_utf8_stderr
    else:
        kwargs['file'] = kwargs.get('file', _py3_utf8_stdout)
    _py3_print(*args, **kwargs)


if PY32PLUS:
    etree_iter = ET.Element.iter
elif PY25PLUS:
    etree_iter = ET_Element.getiterator

if PY26PLUS:
    thread_is_alive = threading.Thread.is_alive
else:
    thread_is_alive = threading.Thread.isAlive


# Exception "constants" to support Python 2 through Python 3
try:
    import ssl
    try:
        CERT_ERROR = (ssl.CertificateError,)
    except AttributeError:
        CERT_ERROR = ()

    HTTP_ERRORS = (
        (HTTPError, URLError, socket.error, ssl.SSLError, BadStatusLine) +
        CERT_ERROR
    )
except ImportError:
    ssl = None
    HTTP_ERRORS = (HTTPError, URLError, socket.error, BadStatusLine)


class SpeedtestException(Exception):
    """Base exception for this module"""


class SpeedtestCLIError(SpeedtestException):
    """Generic exception for raising errors during CLI operation"""


class SpeedtestHTTPError(SpeedtestException):
    """Base HTTP exception for this module"""


class SpeedtestConfigError(SpeedtestException):
    """Configuration XML is invalid"""


class SpeedtestServersError(SpeedtestException):
    """Servers XML is invalid"""


class ConfigRetrievalError(SpeedtestHTTPError):
    """Could not retrieve config.php"""


class ServersRetrievalError(SpeedtestHTTPError):
    """Could not retrieve speedtest-servers.php"""


class InvalidServerIDType(SpeedtestException):
    """Server ID used for filtering was not an integer"""


class NoMatchedServers(SpeedtestException):
    """No servers matched when filtering"""


class SpeedtestMiniConnectFailure(SpeedtestException):
    """Could not connect to the provided speedtest mini server"""


class InvalidSpeedtestMiniServer(SpeedtestException):
    """Server provided as a speedtest mini server does not actually appear
    to be a speedtest mini server
    """


class ShareResultsConnectFailure(SpeedtestException):
    """Could not connect to speedtest.net API to POST results"""


class ShareResultsSubmitFailure(SpeedtestException):
    """Unable to successfully POST results to speedtest.net API after
    connection
    """


class SpeedtestUploadTimeout(SpeedtestException):
    """testlength configuration reached during upload
    Used to ensure the upload halts when no additional data should be sent
    """


class SpeedtestBestServerFailure(SpeedtestException):
    """Unable to determine best server"""


class SpeedtestMissingBestServer(SpeedtestException):
    """get_best_server not called or not able to determine best server"""


def debug(to_write: str, isdebug: bool = False) -> logger:
    if isdebug:
        print(to_write)
    logger.debug('%s' % to_write)


class aiobject:
    """Inheriting this class allows you to define an async __init__.
    So you can create objects by doing something like `await MyClass(params)`
    """
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass


async def aio_create_connection(
    address: Tuple[str, int], timeout: int = _GLOBAL_DEFAULT_TIMEOUT,
    source_address: str = None, loop: asyncio.get_event_loop = None
) -> socket.socket:
    """Connect to *address* and return the socket object.
    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    An host of '' or port 0 tells the OS to use the default.
    Largely vendored from Python 2.7, modified to work with Python 2.4
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    host, port = address
    err = None
    for res in await loop.getaddrinfo(
        host,
        port,
        family=0,
        type=socket.SOCK_STREAM,
    ):
        (
            af,  # family
            socktype,  # type
            proto,  # proto
            _,  # canonname
            sa,  # sockaddr, ('::1', 3333, 0, 0)
        ) = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(float(timeout))
            if source_address:
                sock.bind(source_address)
            await loop.sock_connect(sock, sa)
            return sock

        except OSError:
            err = get_exception()
            if sock is not None:
                sock.close()

    if err is not None:
        raise err
    else:
        raise OSError('getaddrinfo returns an empty list')


def create_connection(
    address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
    source_address=None,
):
    """Connect to *address* and return the socket object.
    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    An host of '' or port 0 tells the OS to use the default.
    Largely vendored from Python 2.7, modified to work with Python 2.4
    """

    host, port = address
    err = None
    for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(float(timeout))
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock

        except OSError:
            err = get_exception()
            if sock is not None:
                sock.close()

    if err is not None:
        raise err
    else:
        raise OSError('getaddrinfo returns an empty list')


class SpeedtestHTTPConnection(HTTPConnection):
    """Custom HTTPConnection to support source_address across
    Python 2.4 - Python 3
    """

    def __init__(self, *args, **kwargs):
        source_address = kwargs.pop('source_address', None)
        timeout = kwargs.pop('timeout', 10)

        self._tunnel_host = None

        HTTPConnection.__init__(self, *args, **kwargs)

        self.source_address = source_address
        self.timeout = timeout

    def connect(self):
        """Connect to the host and port specified in __init__.
        """
        try:
            self.sock = socket.create_connection(
                (self.host, self.port),
                self.timeout,
                self.source_address,
            )
        except (AttributeError, TypeError):
            self.sock = create_connection(
                (self.host, self.port),
                self.timeout,
                self.source_address,
            )

        if self._tunnel_host:
            self._tunnel()


if HTTPSConnection:
    class SpeedtestHTTPSConnection(HTTPSConnection):
        """Custom HTTPSConnection to support source_address across
        Python 2.4 - Python 3
        """
        default_port = 443

        def __init__(self, *args, **kwargs):
            source_address = kwargs.pop('source_address', None)
            timeout = kwargs.pop('timeout', 10)

            self._tunnel_host = None

            HTTPSConnection.__init__(self, *args, **kwargs)

            self.timeout = timeout
            self.source_address = source_address

        def connect(self):
            'Connect to a host on a given (SSL) port.'
            try:
                self.sock = socket.create_connection(
                    (self.host, self.port),
                    self.timeout,
                    self.source_address,
                )
            except (AttributeError, TypeError):
                self.sock = create_connection(
                    (self.host, self.port),
                    self.timeout,
                    self.source_address,
                )

            if self._tunnel_host:
                self._tunnel()

            if not ssl:
                raise SpeedtestException(
                    'This version of Python does not support HTTPS/SSL '
                    'functionality.',
                )

            try:
                kwargs = {}
                if hasattr(ssl, 'SSLContext'):
                    if self._tunnel_host:
                        kwargs['server_hostname'] = self._tunnel_host
                    else:
                        kwargs['server_hostname'] = self.host
                self.sock = self._context.wrap_socket(self.sock, **kwargs)
            except AttributeError:
                self.sock = ssl.wrap_socket(self.sock)
                try:
                    self.sock.server_hostname = self.host
                except AttributeError:
                    pass


def _build_connection(connection, source_address, timeout, context=None):
    """Cross Python 2.4 - Python 3 callable to build an ``HTTPConnection`` or
    ``HTTPSConnection`` with the args we need
    Called from ``http(s)_open`` methods of ``SpeedtestHTTPHandler`` or
    ``SpeedtestHTTPSHandler``
    """
    def inner(host, **kwargs):
        kwargs.update({
            'source_address': source_address,
            'timeout': timeout,
        })
        if context:
            kwargs['context'] = context
        return connection(host, **kwargs)
    return inner


class SpeedtestHTTPHandler(AbstractHTTPHandler):
    """Custom ``HTTPHandler`` that can build a ``HTTPConnection`` with the
    args we need for ``source_address`` and ``timeout``
    """

    def __init__(self, debuglevel=0, source_address=None, timeout=10):
        AbstractHTTPHandler.__init__(self, debuglevel)
        self.source_address = source_address
        self.timeout = timeout

    def http_open(self, req):
        return self.do_open(
            _build_connection(
                SpeedtestHTTPConnection,
                self.source_address,
                self.timeout,
            ),
            req,
        )

    http_request = AbstractHTTPHandler.do_request_


class SpeedtestHTTPSHandler(AbstractHTTPHandler):
    """Custom ``HTTPSHandler`` that can build a ``HTTPSConnection`` with the
    args we need for ``source_address`` and ``timeout``
    """

    def __init__(
        self, debuglevel=0, context=None, source_address=None,
        timeout=10,
    ):
        AbstractHTTPHandler.__init__(self, debuglevel)
        self._context = context
        self.source_address = source_address
        self.timeout = timeout

    def https_open(self, req):
        return self.do_open(
            _build_connection(
                SpeedtestHTTPSConnection,
                self.source_address,
                self.timeout,
                context=self._context,
            ),
            req,
        )

    https_request = AbstractHTTPHandler.do_request_


def build_opener(source_address=None, timeout=10):
    """Function similar to ``urllib2.build_opener`` that will build
    an ``OpenerDirector`` with the explicit handlers we want,
    ``source_address`` for binding, ``timeout`` and our custom
    `User-Agent`
    """

    # printer('Timeout set to %d' % timeout, debug=True)

    source_address_tuple = (source_address, 0) if source_address else None
    handlers = [
        ProxyHandler(),
        SpeedtestHTTPHandler(
            source_address=source_address_tuple,
            timeout=timeout,
        ),
        SpeedtestHTTPSHandler(
            source_address=source_address_tuple,
            timeout=timeout,
        ),
        HTTPDefaultErrorHandler(),
        HTTPRedirectHandler(),
        HTTPErrorProcessor(),
    ]

    opener = OpenerDirector()
    opener.addheaders = [('User-agent', build_user_agent())]

    for handler in handlers:
        opener.add_handler(handler)

    return opener


class GzipDecodedResponse(GZIP_BASE):
    """A file-like object to decode a response encoded with the gzip
    method, as described in RFC 1952.
    Largely copied from ``xmlrpclib``/``xmlrpc.client`` and modified
    to work for py2.4-py3
    """

    def __init__(self, response):
        # response doesn't support tell() and read(), required by
        # GzipFile
        if not gzip:
            raise SpeedtestHTTPError(
                'HTTP response body is gzip encoded, '
                'but gzip support is not available',
            )
        IO = BytesIO or StringIO
        self.io = IO()
        while 1:
            chunk = response.read(1024)
            if len(chunk) == 0:
                break
            self.io.write(chunk)

        self.io.seek(0)
        gzip.GzipFile.__init__(self, mode='rb', fileobj=self.io)

    def close(self):
        try:
            gzip.GzipFile.close(self)
        finally:
            self.io.close()


def get_exception():
    """Helper function to work with py2.4-py3 for getting the current
    exception in a try/except block
    """
    return sys.exc_info()[1]


def distance(origin, destination):
    """Determine distance between 2 sets of [lat,lon] in km"""

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) * math.sin(dlat / 2) +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) *
        math.sin(dlon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def build_user_agent():
    """Build a Mozilla/5.0 compatible User-Agent string"""

    ua_tuple = (
        'Mozilla/5.0',
        '({}; U; {}; en-us)'.format(
            platform.platform(),
            platform.architecture()[0],
        ),
        'Python/%s' % platform.python_version(),
        '(KHTML, like Gecko)',
        'speedtest-cli/%s' % '2.1.4b1',
    )
    # printer('User-Agent: %s' % user_agent, debug=True)
    return ' '.join(ua_tuple)


def build_request(url, data=None, headers=None, bump='0', secure=False):
    """Build a urllib2 request object
    This function automatically adds a User-Agent header to all requests
    """

    if not headers:
        headers = {}

    if url[0] == ':':
        scheme = ('http', 'https')[bool(secure)]
        schemed_url = f'{scheme}{url}'
    else:
        schemed_url = url

    delim = '&' if '?' in url else '?'
    # WHO YOU GONNA CALL? CACHE BUSTERS!
    final_url = '{}{}x={}.{}'.format(
        schemed_url, delim,
        int(timeit.time.time() * 1000),
        bump,
    )

    headers.update({
        'Cache-Control': 'no-cache',
    })

    # printer('%s %s' % (('GET', 'POST')[bool(data)], final_url), debug=True)

    return Request(final_url, data=data, headers=headers)


async def catch_request(request, opener=None):
    """Helper function to catch common exceptions encountered when
    establishing a connection with a HTTP/HTTPS request
    """

    _open = opener.open if opener else urlopen
    try:
        uh = _open(request)
        if request.get_full_url() != uh.geturl():
            pass
            # print('Redirected to %s' % uh.geturl())
        return uh, False
    except HTTP_ERRORS:
        e = get_exception()
        return None, e


def get_response_stream(response):
    """Helper function to return either a Gzip reader if
    ``Content-Encoding`` is ``gzip`` otherwise the response itself
    """

    try:
        getheader = response.headers.getheader
    except AttributeError:
        getheader = response.getheader

    if getheader('content-encoding') == 'gzip':
        return GzipDecodedResponse(response)

    return response


def get_attributes_by_tag_name(dom, tag_name):
    """Retrieve an attribute from an XML document and return it in a
    consistent format
    Only used with xml.dom.minidom, which is likely only to be used
    with python versions older than 2.5
    """
    elem = dom.getElementsByTagName(tag_name)[0]
    return dict(list(elem.attributes.items()))


def print_dots(shutdown_event):
    """Built in callback function used by Thread classes for printing
    status
    """
    def inner(current, total, start=False, end=False):
        if shutdown_event.isSet():
            return

        sys.stdout.write('.')
        if current + 1 == total and end is True:
            sys.stdout.write('\n')
        sys.stdout.flush()
    return inner


def do_nothing(*args, **kwargs):
    pass


class aioHTTPDownloader(aiobject):

    async def __init__(self, i, request, start, timeout, opener=None):
        self.request = request
        self.result = [0]
        self.starttime = start
        self.timeout = timeout
        self.i = i
        self._opener = opener.open if opener else urlopen
        await self.run()

    async def run(self):
        try:
            if (timeit.default_timer() - self.starttime) <= self.timeout:
                f = self._opener(self.request)
                while (
                    (timeit.default_timer() - self.starttime) <=
                    self.timeout
                ):
                    self.result.append(len(f.read(10240)))
                    if self.result[-1] == 0:
                        break
                f.close()
        except OSError:
            pass


class HTTPUploaderData:
    """File like object to improve cutting off the upload once the timeout
    has been reached.
    """

    def __init__(self, length, start, timeout):
        self.length = length
        self.start = start
        self.timeout = timeout

        self._data = None

        self.total = [0]

    def pre_allocate(self):
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        multiplier = int(round(int(self.length) / 36.0))
        IO = BytesIO or StringIO
        try:
            self._data = IO(
                (
                    'content1=%s' %
                    (chars * multiplier)[0:int(self.length) - 9]
                ).encode(),
            )
        except MemoryError:
            raise SpeedtestCLIError(
                'Insufficient memory to pre-allocate upload data. Please '
                'use --no-pre-allocate',
            )

    @property
    def data(self):
        if not self._data:
            self.pre_allocate()
        return self._data

    def read(self, n=10240):
        if (timeit.default_timer() - self.start) <= self.timeout:
            chunk = self.data.read(n)
            self.total.append(len(chunk))
            return chunk
        else:
            raise SpeedtestUploadTimeout()

    def __len__(self):
        return self.length


class aioHTTPUploader(aiobject):

    async def __init__(
        self,
        i,
        request,
        start,
        size,
        timeout,
        opener=None
    ) -> None:
        self.request = request
        self.request.data.start = self.starttime = start
        self.size = size
        self.result = None
        self.timeout = timeout
        self.i = i
        self._opener = opener.open if opener else urlopen
        await self.run()

    async def run(self):
        request = self.request
        try:
            if (timeit.default_timer() - self.starttime) <= self.timeout:
                try:
                    f = self._opener(request)
                except TypeError:
                    # PY24 expects a string or buffer
                    # This also causes issues with Ctrl-C, but we will concede
                    # for the moment that Ctrl-C on PY24 isn't immediate
                    request = build_request(
                        self.request.get_full_url(),
                        data=request.data.read(self.size),
                    )
                    f = self._opener(request)
                f.read(11)
                f.close()
                self.result = sum(self.request.data.total)
            else:
                self.result = 0
        except (OSError, SpeedtestUploadTimeout):
            self.result = sum(self.request.data.total)


class SpeedtestResults:
    """Class for holding the results of a speedtest, including:
    Download speed
    Upload speed
    Ping/Latency to test server
    Data about server that the test was run against
    Additionally this class can return a result data as a dictionary or CSV,
    as well as submit a POST of the result data to the speedtest.net API
    to get a share results image link.
    """

    def __init__(
        self, download=0, upload=0, ping=0, server=None, client=None,
        opener=None, secure=False,
    ):
        self.download = download
        self.upload = upload
        self.ping = ping
        self.server = {} if server is None else server
        self.client = client or {}

        self._share = None
        self.timestamp = '%sZ' % datetime.datetime.utcnow().isoformat()
        self.bytes_received = 0
        self.bytes_sent = 0

        self._opener = opener or build_opener()
        self._secure = secure

    def __repr__(self):
        return repr(self.dict())

    async def share(self):
        """POST data to the speedtest.net API to obtain a share results
        link
        """

        if self._share:
            return self._share

        download = int(round(self.download / 1000.0, 0))
        ping = int(round(self.ping, 0))
        upload = int(round(self.upload / 1000.0, 0))

        # Build the request to send results back to speedtest.net
        # We use a list instead of a dict because the API expects parameters
        # in a certain order
        api_data = [
            'recommendedserverid=%s' % self.server['id'],
            'ping=%s' % ping,
            'screenresolution=',
            'promo=',
            'download=%s' % download,
            'screendpi=',
            'upload=%s' % upload,
            'testmethod=http',
            'hash=%s' % md5((
                '%s-%s-%s-%s' %
                (ping, upload, download, '297aae72')
            )
                .encode()).hexdigest(),
            'touchscreen=none',
            'startmode=pingselect',
            'accuracy=1',
            'bytesreceived=%s' % self.bytes_received,
            'bytessent=%s' % self.bytes_sent,
            'serverid=%s' % self.server['id'],
        ]

        headers = {'Referer': 'http://c.speedtest.net/flash/speedtest.swf'}
        request = build_request(
            '://www.speedtest.net/api/api.php',
            data='&'.join(api_data).encode(),
            headers=headers, secure=self._secure,
        )
        f, e = await catch_request(request, opener=self._opener)
        if e:
            raise ShareResultsConnectFailure(e)

        response = f.read()
        code = f.code
        f.close()

        if int(code) != 200:
            raise ShareResultsSubmitFailure(
                'Could not submit results to '
                'speedtest.net',
            )

        qsargs = parse_qs(response.decode())
        resultid = qsargs.get('resultid')
        if not resultid or len(resultid) != 1:
            raise ShareResultsSubmitFailure(
                'Could not submit results to '
                'speedtest.net',
            )

        self._share = 'http://www.speedtest.net/result/%s.png' % resultid[0]

        return self._share

    def dict(self):
        """Return dictionary of result data"""

        return {
            'download': self.download,
            'upload': self.upload,
            'ping': self.ping,
            'server': self.server,
            'timestamp': self.timestamp,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'share': self._share,
            'client': self.client,
        }

    @staticmethod
    def csv_header(delimiter=','):
        """Return CSV Headers"""

        row = [
            'Server ID', 'Sponsor', 'Server Name', 'Timestamp', 'Distance',
            'Ping', 'Download', 'Upload', 'Share', 'IP Address',
        ]
        out = StringIO()
        writer = csv.writer(out, delimiter=delimiter, lineterminator='')
        writer.writerow([to_utf8(v) for v in row])
        return out.getvalue()

    def csv(self, delimiter=','):
        """Return data in CSV format"""

        data = self.dict()
        out = StringIO()
        writer = csv.writer(out, delimiter=delimiter, lineterminator='')
        row = [
            data['server']['id'], data['server']['sponsor'],
            data['server']['name'], data['timestamp'],
            data['server']['d'], data['ping'], data['download'],
            data['upload'], self._share or '', self.client['ip'],
        ]
        writer.writerow([to_utf8(v) for v in row])
        return out.getvalue()

    def json(self, pretty=False):
        """Return data in JSON format"""

        kwargs = {}
        if pretty:
            kwargs.update({
                'indent': 4,
                'sort_keys': True,
            })
        return json.dumps(self.dict(), **kwargs)


class Speedtest(aiobject):
    """Class for performing standard speedtest.net testing operations"""

    async def __init__(
        self,
        config=None,
        source_address=None,
        timeout=10,
        secure=False
    ):
        self.config = {}

        self._source_address = source_address
        self._timeout = timeout
        self._opener = build_opener(source_address, timeout)

        self._secure = secure

        await self.get_config()
        if config is not None:
            self.config.update(config)

        self.servers = {}
        self.closest = []
        self._best = {}

        self.results = SpeedtestResults(
            client=self.config['client'],
            opener=self._opener,
            secure=secure,
        )

    @property
    async def best(self) -> dict:
        if not self._best:
            await self.get_best_server()
        return self._best

    async def get_config(self) -> dict:
        """Download the speedtest.net configuration and return only the data
        we are interested in
        """

        headers = {}
        if gzip:
            headers['Accept-Encoding'] = 'gzip'

        request = build_request(
            '://www.speedtest.net/speedtest-config.php',
            headers=headers, secure=self._secure,
        )
        uh, e = await catch_request(request, opener=self._opener)
        if e:
            raise ConfigRetrievalError(e)
        configxml_list = []

        stream = get_response_stream(uh)

        while 1:
            try:
                configxml_list.append(stream.read(1024))
            except (OSError, EOFError):
                raise ConfigRetrievalError(get_exception())
            if len(configxml_list[-1]) == 0:
                break
        stream.close()
        uh.close()

        if int(uh.code) != 200:
            return None

        configxml = b''.join(configxml_list)

        debug('Config XML:\n%s' % configxml, isdebug=DEBUG)

        try:
            try:
                root = ET.fromstring(configxml)
            except ET.ParseError:
                e = get_exception()
                raise SpeedtestConfigError(
                    'Malformed speedtest.net configuration: %s' % e,
                )
            server_config = root.find('server-config').attrib
            download = root.find('download').attrib
            upload = root.find('upload').attrib
            client = root.find('client').attrib

        except AttributeError:
            try:
                root = DOM.parseString(configxml)
            except ExpatError:
                e = get_exception()
                raise SpeedtestConfigError(
                    'Malformed speedtest.net configuration: %s' % e,
                )
            server_config = get_attributes_by_tag_name(root, 'server-config')
            download = get_attributes_by_tag_name(root, 'download')
            upload = get_attributes_by_tag_name(root, 'upload')
            client = get_attributes_by_tag_name(root, 'client')

        ignore_servers = []

        ratio = int(upload['ratio'])
        upload_max = int(upload['maxchunkcount'])
        up_sizes = [32768, 65536, 131072, 262144, 524288, 1048576, 7340032]
        sizes = {
            'upload': up_sizes[ratio - 1:],
            'download': [
                350, 500, 750, 1000, 1500, 2000, 2500,
                3000, 3500, 4000,
            ],
        }

        size_count = len(sizes['upload'])

        upload_count = int(math.ceil(upload_max / size_count))

        counts = {
            'upload': upload_count,
            'download': int(download['threadsperurl']),
        }

        threads = {
            'upload': int(upload['threads']),
            'download': int(server_config['threadcount']) * 2,
        }

        length = {
            'upload': int(upload['testlength']),
            'download': int(download['testlength']),
        }

        self.config.update({
            'client': client,
            'ignore_servers': ignore_servers,
            'sizes': sizes,
            'counts': counts,
            'threads': threads,
            'length': length,
            'upload_max': upload_count * size_count,
        })

        try:
            self.lat_lon = (float(client['lat']), float(client['lon']))
        except ValueError:
            raise SpeedtestConfigError(
                'Unknown location: lat=%r lon=%r' %
                (client.get('lat'), client.get('lon')),
            )

        debug('Config:\n%r' % self.config, isdebug=DEBUG)

        return self.config

    async def get_servers(
        self,
        servers: list = None,
        exclude: list = None
    ) -> list:
        # sourcery no-metrics
        """Retrieve a the list of speedtest.net servers, optionally filtered
        to servers matching those specified in the ``servers`` argument
        """
        if servers is None:
            servers = []

        if exclude is None:
            exclude = []

        self.servers.clear()

        for server_list in (servers, exclude):
            for i, s in enumerate(server_list):
                try:
                    server_list[i] = int(s)
                except ValueError:
                    raise InvalidServerIDType(
                        '%s is an invalid server type, must be int' % s,
                    )

        urls = [
            '://www.speedtest.net/speedtest-servers-static.php',
            'http://c.speedtest.net/speedtest-servers-static.php',
            '://www.speedtest.net/speedtest-servers.php',
            'http://c.speedtest.net/speedtest-servers.php', ]

        headers = {}
        if gzip:
            headers['Accept-Encoding'] = 'gzip'

        async def __request_xmls(url, opener, secure, errors):
            request = build_request(url, headers=headers, secure=self._secure)
            uh, e = await catch_request(request, opener=opener)
            if e:
                errors.append('%s' % e)
                raise ServersRetrievalError()

            stream = get_response_stream(uh)

            serversxml_list = []
            while 1:
                try:
                    serversxml_list.append(stream.read(1024))
                except (OSError, EOFError):
                    raise ServersRetrievalError(get_exception())
                if len(serversxml_list[-1]) == 0:
                    break

            stream.close()
            uh.close()

            if int(uh.code) != 200:
                return None  # raise ServersRetrievalError()

            return serversxml_list

        errors = []
        coroutines = [
            __request_xmls(
                url, self._opener, False, errors,
            ) for url in urls
        ]
        completed, pending = await asyncio.wait(coroutines)

        servers_xml_list = list(
            filter(
                lambda task: task is not None,
                [
                    task.result() for task in completed
                ],
            ),
        )

        for serversxml_list in servers_xml_list:
            serversxml = b''.join(serversxml_list)

            # printer('Servers XML:\n%s' % serversxml, debug=True)

            try:
                try:
                    try:
                        root = ET.fromstring(serversxml)
                    except ET.ParseError:
                        e = get_exception()
                        raise SpeedtestServersError(
                            'Malformed speedtest.net server list: %s' % e,
                        )
                    elements = etree_iter(root, 'server')
                except AttributeError:
                    try:
                        root = DOM.parseString(serversxml)
                    except ExpatError:
                        e = get_exception()
                        raise SpeedtestServersError(
                            'Malformed speedtest.net server list: %s' % e,
                        )
                    elements = root.getElementsByTagName('server')
            except (SyntaxError, xml.parsers.expat.ExpatError):
                raise ServersRetrievalError()

            for server in elements:
                try:
                    attrib = server.attrib
                except AttributeError:
                    attrib = dict(list(server.attributes.items()))

                if servers and int(attrib.get('id')) not in servers:
                    continue

                if (
                    int(attrib.get('id')) in self.config['ignore_servers']
                    or int(attrib.get('id')) in exclude
                ):
                    continue

                try:
                    d = distance(
                        self.lat_lon,
                        (
                            float(attrib.get('lat')),
                            float(attrib.get('lon')),
                        ),
                    )
                except Exception:
                    continue

                attrib['d'] = d

                try:
                    self.servers[d].append(attrib)
                except KeyError:
                    self.servers[d] = [attrib]
            break

        if (servers or exclude) and not self.servers:
            raise NoMatchedServers()

        return self.servers

    async def set_mini_server(self, server: str) -> list:
        """Instead of querying for a list of servers, set a link to a
        speedtest mini server
        """

        urlparts = urlparse(server)
        _, ext = os.path.splitext(urlparts[2])
        url = os.path.dirname(server) if ext else server
        request = build_request(url)
        uh, e = await catch_request(request, opener=self._opener)
        if e:
            raise SpeedtestMiniConnectFailure(
                'Failed to connect to %s' % server,
            )
        text = uh.read()
        uh.close()

        extension = re.findall(
            'upload_?[Ee]xtension: "([^"]+)"', text.decode(),
        )
        if not extension:
            for ext in ['php', 'asp', 'aspx', 'jsp']:
                try:
                    f = self._opener.open(
                        f'{url}/speedtest/upload.{ext}',
                    )
                except Exception:
                    pass
                else:
                    data = f.read().strip().decode()
                    if (
                        f.code == 200 and
                        len(data.splitlines()) == 1 and
                        re.match('size=[0-9]', data)
                    ):
                        extension = [ext]
                        break

        if not urlparts or not extension:
            raise InvalidSpeedtestMiniServer(
                'Invalid Speedtest Mini Server: %s' % server,
            )

        self.servers = [{
            'sponsor': 'Speedtest Mini',
            'name': urlparts[1],
            'd': 0,
            'url': '{}/speedtest/upload.{}'.format(
                url.rstrip('/'),
                extension[0],
            ),
            'latency': 0,
            'id': 0,
        }]

        return self.servers

    async def get_closest_servers(self, limit: int = 5) -> None:
        """Limit servers to the closest speedtest.net servers based on
        geographic distance.
        """

        if not self.servers:
            await self.get_servers()

        for d in sorted(self.servers.keys()):
            for s in self.servers[d]:
                self.closest.append(s)
                if len(self.closest) == limit:
                    break
            else:
                continue
            break

        return self.closest

    async def get_best_server(self, servers=None) -> dict:
        """Perform a speedtest.net "ping" to determine which speedtest.net
        server has the lowest latency.
        Args:
            servers ([type], optional): [description]. Defaults to None.
        Raises:
            SpeedtestBestServerFailure: [description]
        Returns:
            dict: [description]
        """

        if not servers:
            if not self.closest:
                servers = await self.get_closest_servers()
            servers = self.closest

        if self._source_address:
            source_address_tuple = (self._source_address, 0)
        else:
            source_address_tuple = None

        user_agent = build_user_agent()

        results = {}
        for server in servers:
            cum = []
            url = os.path.dirname(server['url'])
            stamp = int(timeit.time.time() * 1000)
            latency_url = f'{url}/latency.txt?x={stamp}'
            for _ in range(3):
                # this_latency_url = f'{latency_url}.{i}'
                # printer('%s %s' % ('GET', this_latency_url), debug=True)
                urlparts = urlparse(latency_url)
                try:
                    if urlparts[0] == 'https':
                        h = SpeedtestHTTPSConnection(
                            urlparts[1],
                            source_address=source_address_tuple,
                        )
                    else:
                        h = SpeedtestHTTPConnection(
                            urlparts[1],
                            source_address=source_address_tuple,
                        )
                    headers = {'User-Agent': user_agent}
                    path = '{}?{}'.format(urlparts[2], urlparts[4])
                    start = timeit.default_timer()
                    h.request('GET', path, headers=headers)
                    r = h.getresponse()
                    total = (timeit.default_timer() - start)
                except HTTP_ERRORS:
                    e = get_exception()
                    print('ERROR: %r' % e, debug=True)
                    cum.append(3600)
                    continue

                text = r.read(9)
                if int(r.status) == 200 and text == b'test=test':
                    cum.append(total)
                else:
                    cum.append(3600)
                h.close()

            avg = round((sum(cum) / 6) * 1000.0, 3)
            results[avg] = server

        try:
            fastest = sorted(results.keys())[0]
        except IndexError:
            raise SpeedtestBestServerFailure(
                'Unable to connect to servers to test latency.',
            )

        best = results[fastest]
        best['latency'] = fastest

        self.results.ping = fastest
        self.results.server = best
        self._best.update(best)

        debug('Best Server:\n%r' % best, isdebug=DEBUG)

        return best

    async def download(self, callback=do_nothing) -> int:
        """Test download speed against speedtest.net
        Args:
            callback ([type], optional): [description]. Defaults to do_nothing.
        Returns:
            int: [description]
        """

        urls, finished = [], []
        for size in self.config['sizes']['download']:
            for _ in range(0, self.config['counts']['download']):
                best = await self.best
                urls.append(
                    '%s/random%sx%s.jpg' %
                    (os.path.dirname(best['url']), size, size),
                )

        requests = []
        for i, url in enumerate(urls):
            requests.append(
                build_request(url, bump=i, secure=self._secure),
            )

        async def __aio_http_download(i, request, start, timeout, opener):
            aiod = await aioHTTPDownloader(
                i,
                request,
                start,
                timeout,
                opener=opener,
            )
            return aiod.result

        start = timeit.default_timer()

        coroutines = [
            __aio_http_download(
                i,
                request,
                start,
                self.config['length']['download'],
                self._opener,
            ) for (
                i,
                request,
            ) in enumerate(requests)
        ]
        completed, _ = await asyncio.wait(coroutines)

        stop = timeit.default_timer()

        for task in completed:
            finished.append(sum(task.result()))

        self.results.bytes_received = sum(finished)
        self.results.download = (
            (self.results.bytes_received / (stop - start)) * 8.0
        )

        return self.results.download

    async def upload(
        self,
        callback=do_nothing,
        pre_allocate: bool = True
    ) -> int:
        """Test upload speed against speedtest.net
        Args:
            callback ([type], optional): [description]. Defaults to do_nothing.
            pre_allocate (bool, optional): [description]. Defaults to True.
        Returns:
            int: [description]
        """

        sizes, finished, requests = [], [], []

        for size in self.config['sizes']['upload']:
            for _ in range(0, self.config['counts']['upload']):
                sizes.append(size)
        request_count = self.config['upload_max']

        for _, size in enumerate(sizes):
            data = HTTPUploaderData(
                size,
                0,
                self.config['length']['upload'],
            )
            if pre_allocate:
                data.pre_allocate()
            headers = {'Content-length': size}
            best = await self.best
            requests.append(
                (
                    build_request(
                        best['url'], data, secure=self._secure,
                        headers=headers,
                    ),
                    size,
                ),
            )

        async def __aio_http_upload(i, request, start, size, timeout, opener):
            aiod = await aioHTTPUploader(
                i,
                request,
                start,
                size,
                timeout,
                opener=opener,
            )
            return aiod.result

        start = timeit.default_timer()

        coroutines = [
            __aio_http_upload(
                i,
                request[0],
                start,
                request[1],
                self.config['length']['upload'],
                self._opener,
            ) for (
                i,
                request,
            ) in enumerate(requests[:request_count])
        ]
        completed, _ = await asyncio.wait(coroutines)
        stop = timeit.default_timer()
        for task in completed:
            finished.append(task.result())
        stop = timeit.default_timer()
        self.results.bytes_sent = sum(finished)
        self.results.upload = (
            (self.results.bytes_sent / (stop - start)) * 8.0
        )
        return self.results.upload
