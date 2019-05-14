from collections import namedtuple
from contextlib import closing
from io import BytesIO
from json import dumps as json_encode
import os
import sys
from onem2m import AE

if sys.version_info >= (3, 0):
	from http.server import BaseHTTPRequestHandler, HTTPServer
	from socketserver import ThreadingMixIn
	from urllib.parse import parse_qs
else:
	from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
	from SocketServer import ThreadingMixIn
	from urlparse import parse_qs

ResponseStatus = namedtuple("HTTPStatus", ["code", "message"])
ResponseData = namedtuple("ResponseData", ["status", "content_type", "data_stream"])
MimeType = namedtuple("MimeType", ["content_type"])

ROOT_PATH = "resources"
CHUNK_SIZE = 1024
HTTP_STATUS = {"OK": ResponseStatus(code=200, message="OK"),
		"BAD_REQUEST": ResponseStatus(code=400, message="Bad request"),
		"NOT_FOUND": ResponseStatus(code=404, message="Not found"),
		"INTERNAL_SERVER_ERROR": ResponseStatus(code=500, message="Internal server error")}

MIMETYPE = {"html": MimeType(content_type="text/html"),
		"js": MimeType(content_type="application/js"),
		"css": MimeType(content_type="text/css"),
		"gif": MimeType(content_type="image/gif"),
		"ico": MimeType(content_type="image/x-icon"),
		"jpg": MimeType(content_type="image/jpeg"),
		"jpeg": MimeType(content_type="image/jpeg"),
		"png": MimeType(content_type="image/png"),
		"svg": MimeType(content_type="image/svg+xml"),
		"woff": MimeType(content_type="application/font-woff"),
		"ttf": MimeType(content_type="application/font-ttf"),
		"eot": MimeType(content_type="application/vnd.ms-fontobject"),
		"json": MimeType(content_type="application/json"),
		"xml": MimeType(content_type="application/xml")}

port = int(os.getenv("PORT", 8000))

ROUTE_INDEX = "/index.html"

class HTTPStatusError(Exception):
	
	def __init__(self, status, description=None):
		super(HTTPStatusError, self).__init__()
		self.code = status.code
		self.message = status.message
		self.explain = description

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	daemon_threads = True

class ChunkedHTTPRequestHandler(BaseHTTPRequestHandler):
	protocol_version = "HTTP/1.1"

	def realpath(self, path):
		return os.path.join(sys.path[0], ROOT_PATH, path[1:])

	def query_get(self, queryData, key, default=""):
		return queryData.get(key, [default])[0]

	def send_headers(self, status, content_type):
		self.send_response(status.code, status.message)
		self.send_header('Content-type', content_type)
		self.send_header('Transfer-Encoding', 'chunked')
		self.end_headers()

	def stream_data(self, stream):
		if stream:
			with closing(stream) as managed_stream:
				while True:
					data = managed_stream.read(CHUNK_SIZE)
					self.wfile.write(b"%X\r\n%s\r\n" % (len(data), data))

					if not data:
						break

				self.wfile.flush()

	def do_GET(self):
		
		path, _, query_string = self.path.partition('?')
		query = parse_qs(query_string)

		response = None

		print(u"[START]: Received GET for %s with query: %s" % (path, query))
		
		try:
			if path == '/' or path == ROUTE_INDEX:
				response = self.route_index(path, query)
			else:
				response = self.route_file(path, query)

			self.send_headers(response.status, response.content_type)
			self.stream_data(response.data_stream)
		
		except HTTPStatusError as err:
			if sys.version_info >= (3, 0):
				self.send_error(err.code, err.message, err.explain)
			else:
				self.send_error(err.code, err.message)

	def route_not_found(self, path, query):
		raise HTTPStatusError(HTTP_STATUS["NOT_FOUND"], "Page not found")

	def route_index(self, path, query):
		try:
			return ResponseData(status=HTTP_STATUS["OK"], content_type=MIMETYPE["html"].content_type,
				data_stream=open(self.realpath(ROUTE_INDEX), "rb"))
		except IOError as err:
			raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"], str(err))

	def route_file(self, path, query):
		fname = self.realpath(path)
		if os.path.isfile(fname):
			ext = os.path.splitext(fname)[-1].lower()[1:]			
			try:
				mimetype = MIMETYPE[ext].content_type
				return ResponseData(status=HTTP_STATUS["OK"], content_type=mimetype,
					data_stream=open(fname, "rb"))
			except KeyError as err:
				raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"], "not supported file")
			
		else:
			self.route_not_found(path, query)


if __name__ == '__main__':
	server = ThreadedHTTPServer(('0.0.0.0', port), ChunkedHTTPRequestHandler)
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()
