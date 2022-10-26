import subprocess
import os, sys
import time
import itertools

def run_subprocess_job(args, job_dict, cmd):
    job_id = job_dict['JOB_ID']

    # Create output directory if it does not exist

    # time for the file we are creating
    timestr = time.strftime("%Y%m%d-%H%M%S")

    with open(os.path.join(args['log_dir'], args['prefix'], timestr + '_job_' + job_id + ".log"), "wb") as f:

        # Launch the job
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)

        # Now we have to poll it to ensure tha tthe job actually completes and so we can store outputs in real time
        os.environ['PYTHONUNBUFFERED'] = '1'

        while True:
            output = popen.stdout.readline()
            if popen.poll() is not None:
                break
            if output:
                f.write(output)
                f.flush()
        rc = popen.poll()

    # Read the error outputs to ensure that the program is error free
    stderr_v = popen.stderr.read()
    popen.stderr.close()

    if stderr_v:
        return "ERROR"
    else:
        return "COMPLETE"

def create_grid_search(params_dict):
    return_dict = {}
    for key in params_dict.keys():
        return_dict[key] = []

    keys, values = zip(*params_dict.items())
    permutations_dicts = [v for v in itertools.product(*values)]

    # list comprehension to append everything correctly
    [return_dict[k].append(tup[i]) for i, k in enumerate(keys) for tup in permutations_dicts]

    return return_dict

EXCLUDE_DICT_KEYS = ['STATE', 'JOB_ID']
def default_runner(python_file, runner_args, job_dict):
    args = []
    for k, v in job_dict.items():
        if k in EXCLUDE_DICT_KEYS:  
            continue
        args.append(k)
        args.append(v)

    cmd = ['python', python_file] + args

    ret = run_subprocess_job(runner_args, job_dict, cmd)
    return ret

