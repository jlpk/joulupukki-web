import pecan

from joulupukki.common.carrier import Carrier

carrier = Carrier(pecan.conf.rabbit_server, pecan.conf.rabbit_port, pecan.conf.rabbit_db)
