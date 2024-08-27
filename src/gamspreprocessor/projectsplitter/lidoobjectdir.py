"""Module to handle a directory for a LIDO object.
"""

from .objectdir import ObjectDirectory

class LIDOObjectDirectory(ObjectDirectory):
    """Class to handle a directory for a LIDO object.


    Provides as split method to create a object folder for the file given as argument.
    """


    def __str__(self):
        return f"LIDOObjectDirectory({self.path})"
