import inspect

import wsme
from wsme import types as wtypes


class Base(wtypes.Base):
    """Base class for all API types."""

    def as_dict(self):
        keys = [
            member[0] for member
            in inspect.getmembers(self.__class__)
            if member[0][0] is not '_' and type(member[1]) is wtypes.wsattr
        ]
        return self.as_dict_from_keys(keys)

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)
