# burnish

This is a very simple tool to create and run jobs easily in parallel. 


## `burnish create`
To use burnish, first you need to create a `burnish.db` file. There are several ways to do so using `burnish create`. You can do so via a yaml file, a csv file (in progress), or by using your own creator function in python that outputs a dictionary. A yaml file is the easiest to create grid searches.

`burnish create --yaml test.yaml` is the easiest way to create a grid search. Simply put the argument you want to search over as the key and the value must be a list of keys to grid search over

`burnish create --func script_name.creator_func_name` will create a db file consisting of jobs according to a dictionary you define. 

Once the `burnish.db` file is created, you can edit the file in a text editor. You should not edit the file if any script is running, otherwise race conditions will occur during writing! I acknowledge implementing burnish like this is risky, but the convenience of simply editing the .db file makes it very convenient compared to using something like MongoDB as the backend. 

If you wish to have multiple .db files, set the `--db_file` argument each time you run `burnish`, otherwise the default will be `burnish.db`.

For simplicity, we recommend during the create process, to define the keys for your arguments as how you would exactly spawn a python script in the terminal. For example, rather than creating a key called `seed`, you would call it `--seed`. An example .yaml file is shown in `test_dir/test.yaml`

## `burnish run`
The key use of this script is `burnish run`, which will run the jobs in your .db file in order. It uses a python subprocess to launch new scripts according to some runner function. A runner function, defined by `--func script_name.runner_func_name`, determines how to compose the information in each job entry so that you can set command-line arguments for a script of your choosing.

Therefore, you would run the script using `burnish run --func script_name.runner_func_name`

For example, say you have a `train.py` that takes in a seed argument `--seed 42`. The function defined by `--func` will recieve a dict consisting of the the job argument names and values. The user can choose to compose these arguments into a command, which is directly passed into a util function that spawns the job. An example is provided in the `test_dir/example.py` directory. 

If you expect your arguments to be directly followed one after another (e.g. `--seed`, `42`, `--lr .0001`, etc.) and do not expect any odd combinations, you can call:

```burnish run --python_file train.py```, where the specified python file is called with all the argument keys and values in order.

You can also set `--num_workers #` so that multiple jobs can run in parallel. It will keep running until all the jobs in the list are complete. If you have a cluster with shared storage, or can only fit a certain number of jobs in a GPU, you can set the number of workers accordingly to each GPU. You can call `burnish run` multiple times if necessary. 


Note, the outputs of each job is put into the folder `burnish_log` labeled by time and job ID. Currently, there is no saving of the std_err output, and if there is anything in std_err, the output upon completion is ERROR. This is not ideal, especially since we cannot store error logs. THIS IS CURRENTLY A WORK IN PROGRESS. I highly recommend testing your code extensively before running it through this script, as it becomes hard to find where jobs have failed.

Additionally, since this code is still a work in progress, sometimes perfectly running code states ERROR. I am currently looking for better solutions. 

## `burnish status`
If you wish to view the status of all of your jobs, simply type `burnish status`, and it will print a table of your jobs, including their status of RUNNING, NOT_RUNNING, and ERROR.

## `burnish reset`

If you wish to clear all jobs from saying RUNNING, NOT_RUNNING, or ERROR, simply run `burnish reset`. This will set all jobs to NOT_RUNNING. This command DOES NOT KILL RUNNING JOBS, it only resets the database.

If you wish to remove only the jobs that say ERROR, run `burnish reset --errors`

If you wish to remove only a specific job, call `burnish reset --job_id #`. This currently may not work, and I do not recommend using it for the time being.

## `burnish view`

If you wish to view the output of a specific job, simply call `burnish view --job_id #`. This will open up the log file for the most recent output log with that job ID in vim.

## `burnish clean`

If you want to remove all burnish logs and the current .db file, run `burnish clean`.