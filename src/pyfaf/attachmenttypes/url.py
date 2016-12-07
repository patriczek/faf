from pyfaf.attachmenttypes import AttachmentType
from pyfaf.common import FafError, log
from pyfaf.storage import ReportURL
from sqlalchemy.exc import IntegrityError
import datetime

log = log.getChildLogger(__name__)


class Url(AttachmentType):
    name = 'url'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self):
        url = self.attachment["data"]

        # 0ne URL can be attached to many Reports, but every reports must
        # have unique url's
        db_url = (self.db.session.query(ReportURL)
                  .filter(ReportURL.url == url)
                  .filter(ReportURL.report_id == self.report.id)
                  .first())

        if db_url:
            log.debug("Skipping existing URL")
            return

        db_url = ReportURL()
        db_url.report = self.report
        db_url.url = url
        db_url.saved = datetime.datetime.utcnow()

        try:
            self.db.session.flush()
        except IntegrityError:
            raise FafError("Unable to save URL")
