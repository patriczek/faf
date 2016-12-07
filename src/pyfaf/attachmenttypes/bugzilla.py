from pyfaf.attachmenttypes import AttachmentType
from pyfaf.storage import ReportBz
from pyfaf.queries import get_bz_bug
from pyfaf.bugtrackers import bugtrackers
from pyfaf.common import FafError, log

log = log.getChildLogger(__name__)


class Bugzilla(AttachmentType):
    name = 'bugzilla'
    alias = ["rhbz", "fedora-bugzilla", "rhel-bugzilla"]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self):
        bug_id = int(self.attachment["data"])

        reportbug = (self.db.session.query(ReportBz)
                     .filter(
            (ReportBz.report_id == self.report.id) &
            (ReportBz.bzbug_id == bug_id)
        )
                     .first())

        if reportbug:
            log.debug("Skipping existing attachment")
            return

        bug = get_bz_bug(self.db, bug_id)
        if not bug:
            if self.atype in bugtrackers:
                # download from bugtracker identified by atype
                tracker = bugtrackers[self.atype]

                if not tracker.installed(self.db):
                    raise FafError("Bugtracker used in this attachment"
                                   " is not installed")

                bug = tracker.download_bug_to_storage(self.db, bug_id)
            elif self.atype == "rhbz":
                # legacy value
                # - we need to guess the bugtracker:
                # either fedora-bugzilla or rhel-bugzilla,
                # former is more probable
                for possible_tracker in ["fedora-bugzilla", "rhel-bugzilla"]:
                    if possible_tracker not in bugtrackers:
                        continue

                    tracker = bugtrackers[possible_tracker]
                    if not tracker.installed(self.db):
                        continue

                    bug = tracker.download_bug_to_storage(self.db, bug_id)
                    if bug:
                        break

        if bug:
            new = ReportBz()
            new.report = self.report
            new.bzbug = bug
            self.db.session.add(new)
            self.db.session.flush()
        else:
            log.error("Failed to fetch bug #{0} from '{1}'"
                      .format(bug_id, self.atype))
