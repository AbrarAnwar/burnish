import burnish

EXCLUDE_DICT_KEYS = ['STATE', 'JOB_ID']

def creator():

    params_dict = {'--env': ['env1', 'env2', 'env3', 'env4'], 
                    '--model': ['model1', 'model2'], 
                    '--seed': ['1', '2'], 
                    '--lr': ['.001']}

    return_dict = burnish.util.create_grid_search(params_dict)

    return return_dict

PYTHON_SCRIPT = 'test_dir/train.py'
def runner(runner_args, job_dict):

    args = []
    for k, v in job_dict.items():
        if k in EXCLUDE_DICT_KEYS:
            continue
        args.append(k)
        args.append(v)
    cmd = ['python', PYTHON_SCRIPT] + args

    ret = burnish.util.run_subprocess_job(runner_args, job_dict, cmd)
    return ret
