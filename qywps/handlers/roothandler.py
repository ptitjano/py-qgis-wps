import tornado

from .basehandler import BaseHandler
from ..version import __version__
from ..configuration import config_to_dict

class RootHandler(BaseHandler):
    def get(self):
        try:
            from qgis.core import Qgis
            from processing.core.Processing import RenderingStyles
            QGIS_VERSION="{} ({})".format(Qgis.QGIS_VERSION_INT,Qgis.QGIS_RELEASE_NAME)
            styles = RenderingStyles.styles
        except ImportError:
            QGIS_VERSION="n/a"
            styles = {}
            pass

        response = dict(tornado_ver=tornado.version,
                        version = __version__,
                        author="3Liz",
                        author_url="http://3liz.com",
                        qgis_version=QGIS_VERSION,
                        styles=styles,
                        config=config_to_dict())

        self.write_json(response)
