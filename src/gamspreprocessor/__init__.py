from importlib.metadata import metadata

meta = metadata(__name__)
NAME = meta['name']
VERSION = meta['version']

