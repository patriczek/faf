from pyfaf.common import Plugin, import_dir, load_plugins
from abc import ABCMeta, abstractmethod
import os

__all__ = ['AttachmentType', 'attachmentType']
attachmentType = {}


class AttachmentType(Plugin):
    __metaclass__ = ABCMeta
    alias = []

    @abstractmethod
    def process(self):
        pass


import_dir(__name__, os.path.dirname(__file__))
load_plugins(AttachmentType, attachmentType, init=False)

for at_type in attachmentType.values():
    if at_type.alias:
        for alias in at_type.alias:
            attachmentType[alias] = at_type
