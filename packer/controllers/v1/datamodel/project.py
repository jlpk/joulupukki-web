import wsme
import wsme.types as wtypes

from packer.controllers.v1.datamodel import types


class Project(types.Base):
    name = wsme.wsattr(wtypes.text, mandatory=True)
    git_url = wsme.wsattr(wtypes.text, mandatory=False)
    use_packer_git = wsme.wsattr(bool, mandatory=False)

    @classmethod
    def sample(cls):
        return cls(
            host_name="myproject",
            git_url="git://localhost/myproject",
            use_packer_git=False,
        )
