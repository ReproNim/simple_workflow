# This file provides a user-facing command-line interface (CLI) to your workflow

# A template workflow is provided in workflow.py
# If you change the name there, change the name here, as well.
from .workflow import init_workflow_wf
from nipype.pipeline import engine as pe
# The main function is what will be run when niflow-simple-workflow is called
# Command-line arguments are available via the sys.argv list, though you may find it easier
# to construct non-trivial command lines using either of the following libraries:
#  * argparse (https://docs.python.org/3/library/argparse.html)
#  * click (https://click.palletsprojects.com)
def main():
    import pandas as pd

    import os
    import sys
    import requests

    args = get_parser().parse_args()
    
    sink_dir = os.path.abspath(args.sink_dir)
    if args.work_dir:
        work_dir = os.path.abspath(args.work_dir)
    else:
        work_dir = sink_dir

    #key = '11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA'
    r = requests.get('https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}'.format(key=args.key))
    if sys.version_info < (3,):
        from StringIO import StringIO  # got moved to io in python3.
        data = StringIO(r.content)
    else:
        from io import StringIO
        data = StringIO(r.content.decode())

    df = pd.read_csv(data)
    max_subjects = df.shape[0]
    if args.num_subjects:
        max_subjects = args.num_subjects
    elif ('CIRCLECI' in os.environ and os.environ['CIRCLECI'] == 'true'):
        max_subjects = 1
    
    meta_wf = pe.Workflow('metaflow')
    count = 0
    for row in df.iterrows():
        wf = init_workflow_wf(row[1].Subject, sink_dir, row[1]['File Path'])
        meta_wf.add_nodes([wf])
        print('Added workflow for: {}'.format(row[1].Subject))
        count = count + 1
        # run this for only one person on CircleCI
        if count >= max_subjects:
            break

    meta_wf.base_dir = work_dir
    meta_wf.config['execution']['remove_unnecessary_files'] = False
    meta_wf.config['execution']['poll_sleep_duration'] = 2
    meta_wf.config['execution']['crashdump_dir'] = work_dir
    if args.plugin_args:
        meta_wf.run(args.plugin, plugin_args=eval(args.plugin_args))
    else:
        meta_wf.run(args.plugin)


def get_parser():
    from argparse import ArgumentParser, RawTextHelpFormatter
    defstr = ' (default %(default)s)'
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--key", dest="key",
                        help="google docs key")
    parser.add_argument("-o", "--output_dir", dest="sink_dir", default='output',
                        help="Sink directory base")
    parser.add_argument("-w", "--work_dir", dest="work_dir",
                        help="Output directory base")
    parser.add_argument("-p", "--plugin", dest="plugin",
                        default='MultiProc',
                        help="Plugin to use")
    parser.add_argument("--plugin_args", dest="plugin_args",
                        help="Plugin arguments")
    parser.add_argument("-n", dest="num_subjects", type=int,
                        help="Number of subjects")
    
    return parser