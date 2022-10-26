__version__ = '0.1'

import sys, os
import argparse
import pandas as pd

import shutil


import importlib
import concurrent.futures
from .filelocker import FileLock

import burnish.util
import burnish.helpers

from subprocess import call
import glob
import time

DEFAULT_DB_FILE = os.path.join(os.getcwd(), 'burnish.db')
DEFAULT_LOG_DIRECTORY = os.path.join(os.getcwd(), 'burnish_log')

pd.options.mode.chained_assignment = None

sys.path.append(os.getcwd())

def create(args):
    if os.path.isfile(args.db_file):
        print("db file exists. Please remove it if you want to re-create the file.")
        exit(0)

    if args.func is not None:
        print(args.func)
        module, func = args.func.split('.', 1)
        module = importlib.import_module(module)
        func = getattr(module, func)

    elif args.yaml is not None:
        jobs_dict = burnish.helpers.import_yaml(args.yaml)
    # TODO: create --csv and --wandb functions
    else:
        print("Please set --func, --csv, or, --wandb to create the database tracker")

    df = pd.DataFrame.from_dict(jobs_dict)
    df.insert(0, 'STATE', 'NOT_RUNNING')
    df.insert(0, 'JOB_ID', range(len(df)))

    df.to_csv(args.db_file, index=False)
    print(df)


def clean(args):
    # removes the db file
    try:
        os.remove(args.db_file)
    except:
        pass
    try:
        shutil.rmtree(args.log_dir, ignore_errors=True)
    except:
        pass

def run(args):
    if args.func is None and args.python_file is not None:
        func = lambda runner_args, job_dict: burnish.util.default_runner(args.python_file, runner_args, job_dict)
    elif args.func is not None:
        module, func = args.func.split('.', 1)
        module = importlib.import_module(module)
        func = getattr(module, func)
    else:
        print("--func needs to be set.")
        exit()

    

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.num_workers)

    futures = {executor.submit(run_worker, args, func): i for i in range(args.num_jobs)}

def run_worker(args, func):
    job_idx = None

    with FileLock(args.db_file):
        df = pd.read_csv(args.db_file)

        # take the next num_jobs from df and then set them to RUNNING
        for idx, job_state in enumerate(df['STATE']):
            if job_state == "NOT_RUNNING":
                job_idx = idx
                df.at[idx, 'STATE'] = "RUNNING"
                break

        if job_idx == None:
            return True
        df.to_csv(args.db_file, index=False)


    job_dict = df.iloc[job_idx].to_dict()
    # Everythign must be a string, so let us iterate through all the keys and make sure of it
    for key in job_dict.keys():
        job_dict[key] = str(job_dict[key])

    runner_args = {'log_dir': args.log_dir, 'prefix': os.path.basename(args.db_file).split('.')[0]}

    # We now run the job by calling func
    try:
        final_state = func(runner_args, job_dict)
    except Exception as e:
        print(e)
        final_state = "ERROR"

    with FileLock(args.db_file):
        df = pd.read_csv(args.db_file)
        # take the next num_jobs from df and then set them to RUNNING
        df.at[job_idx, 'STATE'] = final_state
        df.to_csv(args.db_file, index=False)
    
def check(args):
    # load the db
    df = pd.read_csv(args.db_file)
    print(df) 

def reset(args):
    with FileLock(args.db_file):
        try:
            df = pd.read_csv(args.db_file)
        except:
            print('DB file does not exist. Run create first!')
            exit()

        if args.errors:
            df['STATE'][df['STATE']=='ERROR'] = 'NOT_RUNNING'
        elif args.job_id:
            df['STATE'][df['JOB_ID']==args.job_id] = 'NOT_RUNNING'
        else:  
            df['STATE'] = 'NOT_RUNNING'
        df.to_csv(args.db_file, index=False)
    print(df)

def view(args):


    
    with FileLock(args.db_file):
        try:
            df = pd.read_csv(args.db_file)
        except:
            print('DB file does not exist. Run create first!')
            exit()

    # print the whole df so user can see the whole progress
    print(df)
    if args.job_id == None:
        print()
        print("Please fill in the --job_id argument with the job_id you want to view")
        exit()

    print('Job {} is {}'.format(args.job_id, df.iloc[args.job_id]['STATE']))

    print('Opening the most recent log file in vim in read-only mode...')
    time.sleep(1)

    path = os.path.join(args.log_dir, os.path.basename(args.db_file).split('.')[0], '*job_{}.log'.format(args.job_id))

    # grab the most recent one and open it in vim
    path = sorted(glob.glob(path))[-1]
    call(['vim', '-R', path])

def cli():

    parser = argparse.ArgumentParser(description='Maintain and run jobs')

    parser.add_argument('action', help="create, run, status, view, reset, or clean", nargs='?')


    parser.add_argument('--python_file', action='store', type=str, help='If only python_file is set, it will use this script and the default way to run jobs without needing a separate runner func defined per-project', default=None)
    parser.add_argument('--func', action='store', type=str, help='If create, the function creates the relevant db file. If \'run\', then we sample each row as necessary', default=None)
    parser.add_argument('--yaml', action='store', help='Creates the db in a grid search according to the .yaml', type=str, default=None)

    parser.add_argument('--num_jobs', type=int, default=-1, help='The max number of jobs to run each time to complete before finishing. If -1, keep going until all are complete')
    parser.add_argument('--num_workers', type=int, default=1, help='The number of workers to run each time \'burnish run --func=...\' is called.')

    parser.add_argument('--db_file', action='store', help='The text to parse.', type=str, default=DEFAULT_DB_FILE)
    parser.add_argument('--log_dir', action='store', help='The text to parse.', type=str, default=DEFAULT_LOG_DIRECTORY)

    parser.add_argument('--job_id', type=int, default=None, help='When calling \'burnish view\', which job_id to open in vim')
    parser.add_argument('--errors', default=False, action='store_true', help='If set and reset is called, only jobs with errors are reset.')

    # parser.add_argument('--csv', action='store', type=str, help='The text to parse.', default=None)
    parser.add_argument('--version', action='store_true')

    args = parser.parse_args()
   
    args.db_file = os.path.abspath(args.db_file)

    if len(sys.argv) == 1:
        print("This package helps you maintain jobs")
        parser.print_help()
        exit()

    if args.version:
        exit(0)

    if args.action == 'create':
        create(args)
        print('create done')
    
    if args.action == 'run':
        if not os.path.exists(args.log_dir):
            os.mkdir(args.log_dir)

        if not os.path.exists(os.path.join(args.log_dir, os.path.basename(args.db_file).split('.')[0])):
            os.mkdir(os.path.join(args.log_dir, os.path.basename(args.db_file).split('.')[0]))


        if args.num_jobs == -1:
            df = pd.read_csv(args.db_file)
            args.num_jobs = len(df)
        run(args)

    if args.action == 'clean':
        clean(args)
        
    if args.action == 'status':
        check(args)

    if args.action == 'reset':
        reset(args)

    if args.action == 'view':
        view(args)
