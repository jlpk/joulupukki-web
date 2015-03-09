import wsme
import wsme.types as wtypes

from joulupukki.common.datamodel import types



class APIResult(types.Base):
    result = wsme.wsattr(wtypes.text, mandatory=False) 
