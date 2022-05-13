"""
Module where the version is written.

'a' or 'alpha' means alpha version (internal testing)

'b' or 'beta' means beta version (external testing)

Append with .postN for post-release updates.  This may be necessary for changes
in packaging or documentation, as PyPI does not allow uploads of files with the
same filename (which corresponds to the version number).

References:
https://en.wikipedia.org/wiki/Software_versioning
https://peps.python.org/pep-0440/#version-scheme
"""
__version__ = '0.2'
