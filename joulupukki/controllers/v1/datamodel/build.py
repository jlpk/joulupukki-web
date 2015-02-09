import wsme
import wsme.types as wtypes

from joulupukki.controllers.v1.datamodel import types

source_types = wtypes.Enum(str, 'local', 'git')

class Build(types.Base):
    source_url = wsme.wsattr(wtypes.text, mandatory=True)
    source_type = wsme.wsattr(source_types, mandatory=True, default="git")
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
            source_url="https://github.com/kaji-project/shinken.git",
            source_type="git",
            branch="master",
        )
