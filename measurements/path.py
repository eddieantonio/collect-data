#!/usr/bin/env

import stat
import os.path

class Path:
    """
    An absolute path.
    """

    def __init__(self, path, *args):
        if isinstance(path, Path):
            # From path:
            self._components = path._components.copy()
        else:
            # From string:
            self._components = os.path.abspath(path).split(os.path.sep)

        assert all(isinstance(arg, str) for arg in args)
        self._components.extend(args)

    def __truediv__(self, other):
        """
        >>> Path('/home') / 'example'
        Path('/home/example')
        """
        return Path(self, other)

    def __str__(self):
        return os.path.sep + os.path.join(*self._components)

    def __repr__(self):
        return '{:}({!r})'.format(self.__class__.__name__, str(self))

    @property
    def basename(self):
        """
        >>> Path('/usr/bin/env').basename
        'env'
        """
        return os.path.basename(str(self))

    @property
    def parent(self):
        """
        >>> Path('/usr/bin/env').parent
        Path('/usr/bin')
        """
        return Path(os.path.dirname(str(self)))

    def __contains__(self, filename):
        """
        >>> 'etc' in Path('/')
        True
        >>> 'does-not-exist.txt' in Path(__file__).parent
        False
        """
        return filename in os.listdir(str(self))


def from_string(string):
    return Path(string)
