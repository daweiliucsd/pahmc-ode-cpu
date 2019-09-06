# -*- coding: utf-8 -*-
"""
@author: Zheng Fang

This is a unit test. If you would like to further develop pahmc_ode_cpu, you 
should visit here frequently. You should also be familiar with the Python (3.7)
built-in module 'unittest'.

To run this unit test, copy this file into its parent directory and execute it.
"""


from datetime import date
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import time

from pahmc_ode_cpu.configure import Configure
from pahmc_ode_cpu.pahmc import Core
from pahmc_ode_cpu.data_preparation import Data
from pahmc_ode_cpu import lib_dynamics


#=========================type your code below=========================
"""A name for your dynamics."""
# it will be used to try to find a match in the built-ins
name = 'nakl'

"""Specs for the dynamics."""
# set the dimension of your dynamics
D = 4
# set the length of the observation window
M = 5000
# set the observed dimensions (list with smallest possible value 1)
obsdim = [1]
# set the discretization interval
dt = 0.02

"""Specs for precision annealing and HMC."""
# set the starting Rf value
Rf0 = 0.1
# set alpha
alpha = 1.7
# set the total number of beta values
betamax = 30
# set the number of HMC samples for each beta
n_iter = 1000
# set the HMC simulation stepsize for each beta
epsilon = 1e-5
# set the number of leapfrog steps for an HMC sample for each beta
S = 100
# set the HMC masses for each beta
mass = (1e0, 1e0, 1e0)
# set the HMC scaling parameter for each beta
scaling = 1e6
# set the "soft" dynamical range for initialization purpose
soft_dynrange = [(-120, 0), (0, 1), (0, 1), (0, 1)]
# set an initial guess for the parameters
par_start = (0.8,
             100, 80, 30, -60, 0.5, -55, 
             -50, 20, 0.2, 0.5,
             -50, -18, 2, 10,
             -60, 35, 2, 8)

"""Sepcs for the twin-experiment data"""
# set the length of the data (must be greater than M defined above)
length = int(1000/dt)
# set the noise levels (standard deviations) in the data for each dimension
noise = np.array([1, 0, 0, 0])
# set the true parameters (caution: order must be consistent)
par_true = (1, 
            120, 50, 20, -77, 0.3, -54.4, 
            -40, 15, 0.1, 0.4, 
            -60, -15, 1, 7, 
            -55, 30, 1, 5)
# set the initial condition for the data generation process
x0 = np.array([-70, 0.1, 0.9, 0.1])
#===============================end here===============================


"""Configure the inputs and the stimuli."""
config = Configure(name, 
                   D, M, obsdim, dt, 
                   Rf0, alpha, betamax, 
                   n_iter, epsilon, S, mass, scaling, 
                   soft_dynrange, par_start, 
                   length, noise, par_true, x0)

config.check_all()

name, \
D, M, obsdim, dt, \
Rf0, alpha, betamax, \
n_iter, epsilon, S, mass, scaling, \
soft_dynrange, par_start, \
length, noise, par_true, x0 = config.regulate()

stimuli = config.get_stimuli()


"""Get the dynamics object."""
try:
    dyn = getattr(lib_dynamics, f'Builtin_{name}')(name, stimuli)
except:
    import def_dynamics
    dyn = def_dynamics.Dynamics(name, stimuli)


"""Generate twin-experiment data."""
data_noisy, stimuli = Data().generate(dyn, D, length, dt, noise, par_true, x0)
Y = data_noisy[obsdim, 0:M]


"""Truncate stimuli to fit the observation window."""
dyn.stimuli = stimuli[:, 0:M]


"""Do the calculations."""
t0 = time.perf_counter()

job = Core(dyn, Y, dt, D, obsdim, M)

# cProfile.run('acceptance, action, action_meanpath, burn, ' \
#              + 'FE_meanpath, ME_meanpath, par_history, par_mean, ' \
#              + 'Rf, Rm, X_init, X_mean, Xfinal_history ' \
#              + '= job.pa(Rf0, alpha, betamax, n_iter, ' \
#              + 'epsilon, S, mass, scaling, soft_dynrange, par_start)')
acceptance, action, action_meanpath, burn, \
FE_meanpath, ME_meanpath, par_history, par_mean, \
Rf, Rm, X_init, X_mean, Xfinal_history \
  = job.pa(Rf0, alpha, betamax, n_iter,
           epsilon, S, mass, scaling, soft_dynrange, par_start)

print(f'Total time = {time.perf_counter()-t0:.2f} seconds.')


# # plot action vs. iteration
# fig, ax = plt.subplots(figsize=(6,5))
# textblue = (49/255, 99/255, 206/255)
# ax.loglog(action[0, :], color=textblue, lw=1.5)
# ax.set_xlim(1, n_iter+1)
# ax.set_xlabel('iteration')
# ax.set_ylabel('action')


# save variables
day = date.today().strftime('%Y-%m-%d')
i = 1
while (Path.cwd() / 'user_results' / f'{name}_{day}_{i}.npz').exists():
    i = i + 1

np.savez(Path.cwd()/'user_results'/f'{name}_{day}_{i}', 
         name=name, 
         D=D, M=M, obsdim=obsdim, dt=dt, 
         Rf0=Rf0, alpha=alpha, betamax=betamax, 
         n_iter=n_iter, epsilon=epsilon, S=S, mass=mass, scaling=scaling, 
         soft_dynrange=soft_dynrange, par_start=par_start, 
         length=length, noise=noise, par_true=par_true, x0=x0, 
         acceptance=acceptance, 
         action=action, 
         action_meanpath=action_meanpath, 
         burn=burn, 
         FE_meanpath=FE_meanpath, 
         ME_meanpath=ME_meanpath, 
         par_history=par_history, 
         par_mean=par_mean, 
         Rf=Rf, 
         Rm=Rm, 
         X_init=X_init, 
         X_mean=X_mean, 
         Xfinal_history=Xfinal_history)
