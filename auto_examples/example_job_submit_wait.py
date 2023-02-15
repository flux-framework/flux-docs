# -*- coding: utf-8 -*-
"""
Introductory example - Job Submit and Wait
==========================================

To programatically create and check the status for a group
of jobs using the flux.job.FluxExecutor.
"""


import os
import concurrent.futures
from flux.job import JobspecV1
from flux.job import JobspecV1, FluxExecutor


#%%
# Instead of directly creating a flux handle by importing flux and doing flux.Flux(),
# this time we are going to use the flux.job.FluxExecutor. This will allow us to submit
# jobs and then asynchronously wait for them to finish. As we did before, let's start
# with a jobspec for a sleep job. We are fairly certain this will run with a return
# code of 0 to indicate success.

jobspec = JobspecV1.from_command(
    command=["sleep", "1"], num_tasks=2, num_nodes=1, cores_per_task=1
)

#%%
# Let's again set the working directory and current environment.
jobspec.cwd = os.getcwd()
jobspec.environment = dict(os.environ)

#%%
# To mix things up a bit, let's run a command that we know will fail. The false
# command always returns a value of 1. This is a "bad" jobspec that will fail!
bad_jobspec = JobspecV1.from_command(["/bin/false"])

#%%
# Now we will demonstrate using the FluxExecutor (via a context) to submit both good
# and bad jobs, and wait for them to finish. We call a job that is marked as completed
# a "future" and can inspect error code and exceptions to see details about the results!

# create an executor to submit jobs
with FluxExecutor() as executor:

    # we will capture and keep each job future
    futures = []

    # submit half successful jobs
    for _ in range(5):
        futures.append(executor.submit(jobspec))
        print(f"submit: {id(futures[-1])} (good) jobspec")

    # and half failure jobs!
    for _ in range(5):
        futures.append(executor.submit(bad_jobspec))
        print(f"submit: {id(futures[-1])} (bad) jobspec")

    # We can now check on our job futures
    for future in concurrent.futures.as_completed(futures):

        # There was an exception!
        if future.exception() is not None:
            print(f"⚠️ wait: {id(future)} Error: job raised error {future.exception()}")

        # Successful result, return code is zero
        elif future.result() == 0:
            print(f"🏆️ wait: {id(future)} Success")

        # Some other result
        else:
            print(f"❌️ wait: {id(future)} Error: job returned exit code {future.result()}")