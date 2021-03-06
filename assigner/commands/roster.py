import logging

from assigner.config import config_context, DuplicateUserError
from prettytable import PrettyTable
from assigner.roster_util import get_filtered_roster, add_to_roster

help = "Manage class roster"

logger = logging.getLogger(__name__)

@config_context
def list_students(conf, args):
    """List students in the roster
    """
    output = PrettyTable(["#", "Name", "Username", "Section"])
    for idx,student in enumerate(get_filtered_roster(conf.roster, args.section, None)):
        output.add_row((idx+1, student["name"], student["username"], student["section"]))

    print(output)

@config_context
def add_student(conf, args):
    """Add a student to the roster
    """
    try:
        add_to_roster(conf, conf.roster, args.name, args.username, args.section, args.force)
    except DuplicateUserError:
        logger.error("Student already exists in roster!")

@config_context
def remove_student(conf, args):
    """Remove a student from the roster
    """
    previous_len = len(conf.roster)

    idxs = []
    for idx, student in enumerate(conf.roster):
        if student['username'] == args.username:
            idxs.append(idx)

    offset = 0
    for idx in idxs:
        del conf.roster[idx - offset]
        offset += 1

    logger.info("Removed {} entries from the roster".format(previous_len - len(conf.roster)))

def setup_parser(parser):
    subparsers = parser.add_subparsers(title='Canvas commands')

    list_parser = subparsers.add_parser('list', help='Print the roster')
    list_parser.add_argument("--section", help="Section to list")
    list_parser.set_defaults(run=list_students)

    add_parser = subparsers.add_parser('add', help='Add a student to the roster')
    add_parser.add_argument("name", help="Name of student")
    add_parser.add_argument("username", help="Username of student")
    add_parser.add_argument("section", help="Section of student")
    add_parser.add_argument("--force", action="store_true", help="Add duplicate student anyway")
    add_parser.set_defaults(run=add_student)


    remove_parser = subparsers.add_parser('remove', help='Remove a student from the roster')
    remove_parser.add_argument("username", help="Username of student to remove")
    remove_parser.set_defaults(run=remove_student)

    help_parser = subparsers.add_parser("help",
                                        help="Show this help screen and exit")
    help_parser.set_defaults(run=lambda x: parser.print_help())