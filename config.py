# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'joulupukki.controllers.root.RootController',
    'modules': ['joulupukki'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/joulupukki/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

logging = {
#    'root': {'level': 'INFO', 'handlers': ['console']},
    'root': {'level': 'DEBUG', 'handlers': ['console']},
    'loggers': {
        'joulupukki': {'level': 'DEBUG', 'handlers': ['console']},
        'pecan.commands.serve': {'level': 'DEBUG', 'handlers': ['console']},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s] '
                       '%(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s] '
                       '%(message)s'),
        '__force_dict__': True
        }
    }
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
workspace_path = '%(confdir)s/tmp'
distros = (
           ("ubuntu_12.04", "ubuntu:12.04", "deb"),
           ("ubuntu_14.04", "ubuntu:14.04", "deb"),
           ("debian_7", "debian:7", "deb"),
           ("debian_8", "debian:8", "deb"),
           ("centos_6", "centos:6", "rpm"),
           ("centos_7", "centos:7", "rpm"),
        )
docker_version = "1.15"
ccache_path = '%(confdir)s/ccache'
#
# All configurations are accessible at::
# pecan.conf
