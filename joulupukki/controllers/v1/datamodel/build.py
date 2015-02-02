import wsme
import wsme.types as wtypes

from joulupukki.controllers.v1.datamodel import types


class Build(types.Base):
    git_url = wsme.wsattr(wtypes.text, mandatory=False)
    uuid = wsme.wsattr(wtypes.text, mandatory=False)
    commit = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    branch = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    created = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    package_name = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    package_version = wsme.wsattr(wtypes.text, mandatory=False, default=None)
    package_release = wsme.wsattr(wtypes.text, mandatory=False, default=None)

    @classmethod
    def sample(cls):
        return cls(
            git_url="https://github.com/kaji-project/shinken.git",
            branch="master",
        )
