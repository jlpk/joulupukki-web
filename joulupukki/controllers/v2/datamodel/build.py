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


    @staticmethod
    def get_folder_path(username, project_name, uuid):
        """ Return project folder path"""
        return os.path.join(pecan.conf.workspace_path, username, project_name, "builds", uuid)


    def create(self):
        pass


    def save(self):
        Build.get_folder_path(username, project_name, uuid)
        build_file = os.path.join(self.folder, "build.cfg")
        data = json.dumps({"source_url": self.source_url,
                           "source_type": self.source_type,
                           "branch": self.branch,
                           "commit": self.commit,
                           "uuid": self.uuid,
                           "created": self.created,
                           "package_name": self.package_name,
                           "package_version": self.package_version,
                           "package_release": self.package_release,
                           })

        with open(build_file, 'w') as f:
            try:
                f.write(data)
            except Exception as exp:
                # TODO handle error
                raise Exception("Error saving build data")
        return True


