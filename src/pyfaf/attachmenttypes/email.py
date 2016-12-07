from pyfaf.attachmenttypes import AttachmentType
from pyfaf.common import FafError
from pyfaf.queries import get_contact_email, get_report_contact_email
from pyfaf.storage import ContactEmail, ReportContactEmail
from sqlalchemy.exc import IntegrityError


class Email(AttachmentType):
    name = 'email'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self):
        db_contact_email = get_contact_email(self.db, self.attachment["data"])
        if db_contact_email is None:
            db_contact_email = ContactEmail()
            db_contact_email.email_address = self.attachment["data"]
            self.db.session.add(db_contact_email)

            db_report_contact_email = ReportContactEmail()
            db_report_contact_email.contact_email = db_contact_email
            db_report_contact_email.report = self.report
            self.db.session.add(db_report_contact_email)
        else:
            db_report_contact_email = \
                get_report_contact_email(self.db, db_contact_email.id, self.report.id)
            if db_report_contact_email is None:
                db_report_contact_email = ReportContactEmail()
                db_report_contact_email.contact_email = db_contact_email
                db_report_contact_email.report = self.report
                self.db.session.add(db_report_contact_email)

        try:
            self.db.session.flush()
        except IntegrityError:
            raise FafError("Email address already assigned to the report")
