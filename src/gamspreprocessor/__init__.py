from importlib.metadata import metadata

meta = metadata(__name__)
NAME = meta['name']
APP_NAME = "preprocessor"
VERSION = meta['version']

