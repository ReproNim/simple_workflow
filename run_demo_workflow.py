#/usr/bin/env python
"""Run a demo workflow that retrieves brain images and processes them

"""
import os

from nipype import config
config.enable_provenance()

from nipype import Workflow, Node, MapNode, Function
from nipype.interfaces.fsl import BET, FAST, FIRST, Reorient2Std, ImageMaths, ImageStats
from nipype.interfaces.io import DataSink

def download_file(url):
    """Download file for a given participant"""
    import requests
    import os
    from time import sleep
    num_retries = 5
    URL = 'http://www.nitrc.org/ir/'
    count = 0
    while count < num_retries:
        count += 1
        session = requests.session()
        r = session.get(URL)
        if r.ok:
            break
        else:
            sleep(10)
            if count == num_retries:
                raise IOError('Could not create a session for {}'.format(URL))
    count = 0
    while count < num_retries:
        count += 1
        local_filename = url.split('/')[-1]
        r = session.get(url, stream=True, cookies=r.cookies)
        if not r.ok:
            if count == num_retries:
                raise IOError('Could not GET {}'.format(url))
            else:
                sleep(5)
                continue
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        # verify that we can load the file
        out_file = os.path.abspath(local_filename)
        try:
            import nibabel as nb
            img = nb.load(out_file)
        except Exception as e:
            os.unlink(out_file)
            if count == num_retries:
                raise
            sleep(5)
        else:
            break
    return out_file

def toJSON(stats, seg_file, structure_map):
    """Combine stats files to a single JSON file"""
    import json
    import os
    import nibabel as nb
    import numpy as np
    img = nb.load(seg_file)
    data = img.get_data()
    voxel2vol = np.prod(img.header.get_zooms())
    idx = np.unique(data)
    reverse_map = {k:v for v, k in structure_map}
    out_dict = dict(zip([reverse_map[val] for val in idx], np.bincount(data.flatten())[idx]))
    for key in out_dict.keys():
        out_dict[key] = [out_dict[key], voxel2vol * out_dict[key]]
    mapper = dict([(0, 'csf'), (1, 'gray'), (2, 'white')])
    out_dict.update(**{mapper[idx]: val for idx, val in enumerate(stats)})
    out_file = 'segstats.json'
    with open(out_file, 'wt') as fp:
        json.dump(out_dict, fp, sort_keys=True, indent=4, separators=(',', ': '))
    return os.path.abspath(out_file)


def create_workflow(subject_id, outdir, file_url):
    """Create a workflow for a single participant"""

    sink_directory = os.path.join(outdir, subject_id)
    
    wf = Workflow(name=subject_id)

    getter = Node(Function(input_names=['url'], output_names=['localfile'],
                           function=download_file), name="download_url")
    getter.inputs.url = file_url

    orienter = Node(Reorient2Std(), name='reorient_brain')
    wf.connect(getter, 'localfile', orienter, 'in_file')

    better = Node(BET(), name='extract_brain')
    wf.connect(orienter, 'out_file', better, 'in_file')

    faster = Node(FAST(), name='segment_brain')
    wf.connect(better, 'out_file', faster, 'in_files')

    firster = Node(FIRST(), name='parcellate_brain')
    structures = ['L_Hipp', 'R_Hipp',
                  'L_Accu', 'R_Accu',
                  'L_Amyg', 'R_Amyg',
                  'L_Caud', 'R_Caud',
                  'L_Pall', 'R_Pall',
                  'L_Puta', 'R_Puta',
                  'L_Thal', 'R_Thal']
    firster.inputs.list_of_specific_structures = structures
    wf.connect(orienter, 'out_file', firster, 'in_file')

    fslstatser = MapNode(ImageStats(), iterfield=['op_string'], name="compute_segment_stats")
    fslstatser.inputs.op_string = ['-l {thr1} -u {thr2} -v'.format(thr1=val + 0.5, thr2=val + 1.5) for val in range(3)]
    wf.connect(faster, 'partial_volume_map', fslstatser, 'in_file')

    jsonfiler = Node(Function(input_names=['stats', 'seg_file', 'structure_map', 'struct_file'], 
                              output_names=['out_file'],
                              function=toJSON), name='save_json')
    structure_map = [('Background', 0),
                     ('Left-Thalamus-Proper', 10),
                     ('Left-Caudate', 11),
                     ('Left-Putamen', 12),
                     ('Left-Pallidum', 13),
                     ('Left-Hippocampus', 17),
                     ('Left-Amygdala', 18),
                     ('Left-Accumbens-area', 26),
                     ('Right-Thalamus-Proper', 49),
                     ('Right-Caudate', 50),
                     ('Right-Putamen', 51),
                     ('Right-Pallidum', 52),
                     ('Right-Hippocampus', 53),
                     ('Right-Amygdala', 54),
                     ('Right-Accumbens-area', 58)]
    jsonfiler.inputs.structure_map = structure_map
    wf.connect(fslstatser, 'out_stat', jsonfiler, 'stats')
    wf.connect(firster, 'segmentation_file', jsonfiler, 'seg_file')

    sinker = Node(DataSink(), name='store_results')
    sinker.inputs.base_directory = sink_directory
    wf.connect(better, 'out_file', sinker, 'brain')
    wf.connect(faster, 'bias_field', sinker, 'segs.@bias_field')
    wf.connect(faster, 'partial_volume_files', sinker, 'segs.@partial_files')
    wf.connect(faster, 'partial_volume_map', sinker, 'segs.@partial_map')
    wf.connect(faster, 'probability_maps', sinker, 'segs.@prob_maps')
    wf.connect(faster, 'restored_image', sinker, 'segs.@restored')
    wf.connect(faster, 'tissue_class_files', sinker, 'segs.@tissue_files')
    wf.connect(faster, 'tissue_class_map', sinker, 'segs.@tissue_map')
    wf.connect(firster, 'bvars', sinker, 'parcels.@bvars')
    wf.connect(firster, 'original_segmentations', sinker, 'parcels.@origsegs')
    wf.connect(firster, 'segmentation_file', sinker, 'parcels.@segfile')
    wf.connect(firster, 'vtk_surfaces', sinker, 'parcels.@vtk')
    wf.connect(jsonfiler, 'out_file', sinker, '@stats')

    return wf

if  __name__ == '__main__':
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
    args = parser.parse_args()

    sink_dir = os.path.abspath(args.sink_dir)
    if args.work_dir:
        work_dir = os.path.abspath(args.work_dir)
    else:
        work_dir = sink_dir

    from StringIO import StringIO  # got moved to io in python3.

    import requests
    import pandas as pd

    #key = '11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA'
    r = requests.get('https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}'.format(key=args.key))
    data = r.content

    df = pd.read_csv(StringIO(data))
    max_subjects = df.shape[0]
    if args.num_subjects:
        max_subjects = args.num_subjects
    elif ('CIRCLECI' in os.environ and os.environ['CIRCLECI'] == 'true'):
        max_subjects = 1
    
    meta_wf = Workflow('metaflow')
    count = 0
    for row in df.iterrows():
        wf = create_workflow(row[1].Subject, sink_dir, row[1]['File Path'])
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
