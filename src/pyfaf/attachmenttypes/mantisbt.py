from pyfaf.attachmenttypes import AttachmentType
from pprint import pprint
from pyfaf.storage import ReportMantis
from pyfaf.queries import get_mantis_bug, get_bugtracker_by_name
from pyfaf.bugtrackers import bugtrackers
from pyfaf.common import FafError, log

log = log.getChildLogger(__name__)

class Mantisbt(AttachmentType):
    name = 'mantisbt'
    alias = ['centos-mantisbt']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self):

        atype = self.attachment["type"].lower()

        bug_id = int(self.attachment["data"])

        reportbug = (self.db.session.query(ReportMantis)
                     .filter(
                         (ReportMantis.report_id == self.report.id) &
                         (ReportMantis.mantisbug_id == bug_id))
                     .first())

        if reportbug:
            log.debug("Skipping existing attachment")
            return

        bt = get_bugtracker_by_name(self.db, self.name)
        if not bt:
            log.error("Bugtracker for centos mantis doesn't exists")
            return

        bug = get_mantis_bug(self.db, bug_id, bt.id)
        if not bug:
            if atype in bugtrackers:
                # download from bugtracker identified by atype
                tracker = bugtrackers[atype]

                if not tracker.installed(self.db):
                    raise FafError("Bugtracker used in this attachment"
                                   " is not installed")

                bug = tracker.download_bug_to_storage(self.db, bug_id)

        if bug:
            new = ReportMantis()
            new.report = self.report
            new.mantisbug = bug
            self.db.session.add(new)
            self.db.session.flush()
        else:
            log.error("Failed to fetch bug #{0} from '{1}'"
                      .format(bug_id, atype))
