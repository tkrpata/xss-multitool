import logging
import colorlog
from termcolor import cprint, colored

def config_logger():
  log_colors = {
		'DEBUG':    'light_black',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	}
  handler = colorlog.StreamHandler()
  handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    log_colors=log_colors))
  logger = colorlog.getLogger('xss-multitool')

  logger.addHandler(handler)
  return logger

def set_log_level(logger, loglevel):
  numeric_level = getattr(logging, loglevel, None)
  try: 
    logger.setLevel(numeric_level)
  except TypeError:
    logger.error(f"Can't set loglevel to {loglevel}")

def display_message(title, content=None, options=None):
  defaults = {  
    "text": "dark_grey", 
    "background": None, 
    "attrs": ["underline"], 
    "pad": False 
  }
  if options is None:
    options = {}
  options = {**defaults, **options}

  if options["pad"]:
    print()
  cprint(f"{title}", options["text"], options["background"], options["attrs"])
  if content:
    cprint(f"{content}")

logger = config_logger()


