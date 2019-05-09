#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.vasp import prep_vasp
from os import chdir
from time import sleep
import subprocess


def is_inqueue(job_id):
    p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
    que_res = p.stdout.readlines()
    p.stdout.close()
    for ii in que_res:
        if str(job_id) in ii.decode('utf-8'):
            return True
    return False

def submit_job():
    res = subprocess.Popen(['sbatch', './job.sh'],stdout=subprocess.PIPE)
    std = res.stdout.readlines()
    res.stdout.close()
    return std[0].decode('utf-8').split()[-1]

# def job_status(job_id):
#     res = run('squeue','grep '+str(job_id)).std_out_err
#     stdout = res[0].split()
#     if stdout == [] :
#         print('Not found job_id in queue')
#         return  None
#     return dict(zip(['job_id','part','name','user','status','time','node','nodelist'],stdout))

def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw

# def _submit_job(wd,jobs_dict):
#     res = subprocess.Popen(['sbatch', './job.sh'],stdout=subprocess.PIPE)
#     std = res.stdout.readlines()
#     res.stdout.close()
#     jobs_dict[wd] = std[0].decode('utf-8').split()[-1]

def run_single_vasp(job_name):
    chdir(job_name)
    job_id = submit_job()
    while True:
        if not is_inqueue(job_id):
            break
        sleep(5)
    chdir('..')


def run_multi_vasp(job_name,end_job_num,start_job_num=0,par_job_num=4):
    job_inqueue_num = lambda id_pool:[is_inqueue(i) for i in id_pool].count(True)
    jobs = []
    end_job_num,start_job_num,par_job_num = int(end_job_num),int(start_job_num),int(par_job_num)
    jobid_pool = []
    idx = start_job_num
    for ii in range(min(par_job_num,end_job_num-start_job_num)):
        chdir(job_name+str(ii+start_job_num))
        jobid_pool.append(submit_job())
        chdir('..')
        idx += 1
    if idx == end_job_num+1:
        return
    while True:
        inqueue_num = job_inqueue_num(jobid_pool)
        if inqueue_num < par_job_num and idx < end_job_num+1:
            chdir(job_name + str(idx))
            jobid_pool.append(submit_job())
            chdir('..')
            idx += 1
        sleep(5)
        if idx == end_job_num+1 and job_inqueue_num(jobid_pool) == 0:
            break
