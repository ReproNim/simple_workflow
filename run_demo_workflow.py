#/usr/bin/env python
"""Run a demo workflow that retrieves brain images and processes them

"""
import os

from nipype import config
config.enable_provenance()

from nipype import Workflow, Node, MapNode, Function
from nipype.interfaces.fsl import BET, FAST, FIRST, Reorient2Std
from nipype.interfaces.io import DataSink

def download_file(url):
    import requests
    import os
    URL = 'http://www.nitrc.org/ir/'
    session = requests.session()
    r = session.get(URL) #, data=payload)
    local_filename = url.split('/')[-1]
    r = session.get(url, stream=True, cookies=r.cookies) #, auth=('satra', os.getenv('password')))
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)    
    return os.path.abspath(local_filename)

def get_stats(seg_file):
    import os
    import nibabel as nb
    import numpy as np
    img = nb.load(seg_file)
    data = img.get_data()
    idx = np.unique(data)
    values = zip(idx, np.bincount(data.flatten())[idx])
    filename = 'segstats.txt'
    with open(filename, 'wt') as fp:
        fp.writelines(['%d,%d\n' % val for val in values ])
    return os.path.abspath(filename)

def create_workflow(subject_id, outdir, file_url):
    sink_directory = os.path.join(outdir, subject_id)
    
    wf = Workflow(name=subject_id)

    getter = Node(Function(input_names=['url'], output_names=['localfile'],
                          function=download_file), name="download_url")
    getter.inputs.url = file_url
    orienter = Node(Reorient2Std(), name='reorient_brain')
    better = Node(BET(), name='extract_brain')
    faster = Node(FAST(), name='segment_brain')
    firster = Node(FIRST(), name='parcellate_brain')
    statser = Node(Function(input_names=['seg_file'], output_names=['stats_file'],
                          function=get_stats), name="get_stats")
    sinker = Node(DataSink(), name='store_results')

    firster.inputs.list_of_specific_structures = ['L_Hipp', 'R_Hipp',
                                                  'L_Accu', 'R_Accu',
                                                  'L_Amyg', 'R_Amyg',
                                                  'L_Caud', 'R_Caud',
                                                  'L_Pall', 'R_Pall',
                                                  'L_Puta', 'R_Puta',
                                                  'L_Thal', 'R_Thal']

    wf.connect(getter, 'localfile', orienter, 'in_file')
    wf.connect(orienter, 'out_file', better, 'in_file')
    wf.connect(orienter, 'out_file', firster, 'in_file')

    wf.connect(better, 'out_file', faster, 'in_files')
    wf.connect(firster, 'segmentation_file', statser, 'seg_file')
    
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
    wf.connect(statser, 'stats_file', sinker, '@stats')

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
                        default='Linear',
                        help="Plugin to use")
    parser.add_argument("--plugin_args", dest="plugin_args",
                        help="Plugin arguments")
    args = parser.parse_args()

    if args.work_dir:
        work_dir = os.path.abspath(args.work_dir)
    else:
        work_dir = os.getcwd()

    sink_dir = os.path.abspath(args.sink_dir)

    from StringIO import StringIO  # got moved to io in python3.

    import requests
    import pandas as pd

    #key = '11an55u9t2TAf0EV2pHN0vOd8Ww2Gie-tHp9xGULh_dA'
    r = requests.get('https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}'.format(key=args.key))
    data = r.content

    df = pd.read_csv(StringIO(data))
    
    meta_wf = Workflow('metaflow')
    for row in df.ix[:1, :].iterrows():
        wf = create_workflow(row[1].Subject, sink_dir, row[1]['File Path'])
        meta_wf.add_nodes([wf])
        print('Added workflow for: {}'.format(row[1].Subject))

    meta_wf.base_dir = work_dir
    if args.plugin_args:
        meta_wf.run(args.plugin, plugin_args=eval(args.plugin_args))
    else:
        meta_wf.run(args.plugin)