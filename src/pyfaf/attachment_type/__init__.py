import os
from pyfaf.common import Plugin, import_dir, load_plugins


__all__ = ['AttachementType', 'attachementType']
attachementType = {}


class AttachementType(Plugin):
    def __init__(self):
        pass

import_dir(__name__, os.path.dirname(__file__))
load_plugins(AttachementType, attachementType, init=False)
