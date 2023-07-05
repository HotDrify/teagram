from logging import basicConfig, DEBUG

basicConfig(
    filename="logs/debug.log",
    filemode='w',
    level=DEBUG,
    format="(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
