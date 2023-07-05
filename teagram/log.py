import logging

logging.basicConfig(
  filename = "logs/debug.log",
  filemode = 'w',
  level = logging.DEBUG,
  format = "(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)