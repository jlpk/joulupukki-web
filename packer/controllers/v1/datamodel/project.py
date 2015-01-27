import wsme
import wsme.types as wtypes

from packer.controllers.v1.datamodel import types


class Project(types.Base):
    name = wsme.wsattr(wtypes.text, mandatory=True)

    @classmethod
    def sample(cls):
        return cls(
            host_name="myproject",
        )
