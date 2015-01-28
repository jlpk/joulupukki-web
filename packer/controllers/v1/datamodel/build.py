import wsme
import wsme.types as wtypes

from packer.controllers.v1.datamodel import types


class Build(types.Base):
    git_url = wsme.wsattr(wtypes.text, mandatory=False)
    commit = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    branch = wsme.wsattr(wtypes.text, mandatory=False, default=None)

    @classmethod
    def sample(cls):
        return cls(
            git_url="https://github.com/kaji-project/shinken.git",
            branch="master",
        )
