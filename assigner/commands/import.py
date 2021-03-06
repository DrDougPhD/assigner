import csv
import logging
import re

from assigner.config import config_context, DuplicateUserError
from assigner.roster_util import add_to_roster

help="Import users from a csv"

logger = logging.getLogger(__name__)


@config_context
def import_students(conf, args):
    """Imports students from a CSV file to the roster.
    """
    section = args.section

    # TODO: This should probably move to another file
    email_re = re.compile(r"^(?P<user>[^@]+)")
    with open(args.file) as fh:
        reader = csv.reader(fh)

        if "roster" not in conf:
            conf["roster"] = []

        # Note: This is incredibly hardcoded.
        # However, peoplesoft never updates anything, so we're probably good.
        reader.__next__()  # Skip the header
        count = 0
        for row in reader:
            count += 1
            match = email_re.match(row[4])

            try:
                add_to_roster(conf, conf.roster, row[3], match.group("user"), section, args.force)
            except DuplicateUserError:
                logger.warning("User {} is already in the roster, skipping".format(match.group("user")))

    print("Imported {} students.".format(count))

def setup_parser(parser):
    parser.add_argument("file", help="CSV file to import from")
    parser.add_argument("section", help="Section being imported")
    parser.add_argument("--force", action="store_true", help="Import duplicate students anyway")
    parser.set_defaults(run=import_students)
