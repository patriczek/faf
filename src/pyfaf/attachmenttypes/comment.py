from pyfaf.attachmenttypes import AttachmentType
from pyfaf.storage import ReportComment
import datetime


class Comment(AttachmentType):
    name = 'comment'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self):
        comment = ReportComment()
        comment.report = self.report
        comment.text = self.attachment["data"]
        comment.saved = datetime.datetime.utcnow()
        self.db.session.add(comment)
        self.db.session.flush()
