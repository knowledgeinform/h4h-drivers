"""
DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
Ave, Panama City, FL 32407.

POC:

Bradley Marchand
NSWC Panama City Division, Code X24 (850)-230-7385
bradley.marchand@navy.mil

Derek Kolacinski
NSWC Panama City Division, Code X23 (850)-230-7218
derek.kolacinski@navy.mil
"""
import os.path as osp
from timeit import default_timer as timer
import mats
import mats.gt
import mats.core
import mats.log
import mats.atr
import mats.uuid


def processor(atrcfg, reader, datafolder, outfolder, gt=None):
    mats.pkg.scan()
    files = []

    mats.log.info('Loading AtrConfig')
    if type(atrcfg) == str:
        tmp = mats.AtrConfig()
        tmp.load(atrcfg)
        atrcfg = tmp
    elif not type(atrcfg) == mats.AtrConfig:
        raise ValueError('atrcfg must be an AtrConfig or a path to one.')
    
    mats.log.info('Configuring ATR.')
    mats.atr.configure(atrcfg)

    mats.log.info('Creating data reader')
    if mats.pkg.find(reader):
        rdr = mats.pkg.create(reader)
    else:
        raise ValueError('Reader module not found.')
    rdr.configure(mats.Struct())

    if osp.exists(datafolder):
        mats.log.info('Scanning data folder for files.')
        files = rdr.scan(datafolder)
        mats.log.info('  Found {} files for processing.'.format(len(files)))
    else:
        raise ValueError('Data folder does not exist.')

    if not osp.exists(outfolder):
        raise ValueError('Output folder does not exist.')

    if not gt is None:
        mats.log.info('Loading GT')
        gt = mats.gt.read_txt(gt)
    
    print('setting up archiver...')
    arc_mng = mats.Archiver()
    arc_mng.location(outfolder)
    arc = mats.Archive()
    arc.location(outfolder)
    arcr_cfg = mats.Struct()
    arcr_cfg['filename_format'] = 'filename'
    arc_mng.options(arcr_cfg)

    arc_cfg = {
        'Uuid': mats.uuid.uuid_generator(),
        'SourceConfigId': '00000000-0000-0000-0000-000000000000',
        'Name': 'Test',
        'Sensor': atrcfg['sensor'],
        'Description': '',
        'Version': '',
        'Location': [],
        'Environment': [],
        'Date': 0.0,
        'Threshold': 0.5,
        'RoCs': [],
        'Dependency': '',
        'Active': True,
        'Disabled': False,
        'ThreadSafe': False
    }

    files_completed = 0
    for ii, source_file in enumerate(files):
        print('----------------------------------------------------------')
        print(f'Input {ii+1}/{len(files)}')
        print(f'Source File: {source_file}')
        total_start = timer()

        print('reading input structure...')
        start_read = timer()
        data = rdr.read(source_file)
        end_read = timer()
        read_time = end_read - start_read
        print(f'read time: {read_time}s')

        for ins in data:
            start_process = timer()
            con, ecd = mats.atr.process(ins, gt)
            end_process = timer()
            process_time = end_process - start_process
            print(f'process time: {process_time}s')

            start_archive = timer()
            print(ins)
            idty = arc_mng.create(arc_cfg, ins)
            print(f'Arc Name: |{idty}|')
            arc.load(idty)
            arc.add_contacts(con)
            arc.add_ecdata(ecd)
            arc.add_gt(gt)
            end_archive = timer()
            archive_time = end_archive - start_archive
            print(f'archive time: {archive_time}s')

        total_end = timer()
        total_time = total_end - total_start
        print(f'total time for image: {total_time}s')

        files_completed += 1

    # generate json perf report for this dataset
    # start_perf = timer()
    # command = f'$XATR_ROOT/bin/mats_perf_report -t {thresh} {outdir}'
    # os.system(command)
    # end_perf = timer()
    # perf_time = end_perf - start_perf
    # print(f'total time to generate perf report: {perf_time}')