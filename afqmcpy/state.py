import json
from json import encoder
import subprocess
import sys
import time
import json
import numpy
import afqmcpy.hubbard as hubbard
import afqmcpy.trial_wave_function as trial_wave_function
import afqmcpy.propagation
import afqmcpy.hs_transform

class State:

    def __init__(self, model, qmc_opts):

        # Generic method option
        self.method = qmc_opts['method']
        self.nwalkers = qmc_opts['nwalkers']
        self.dt = qmc_opts['dt']
        self.nsteps = qmc_opts['nsteps']
        self.nmeasure = qmc_opts['nmeasure']
        self.npop_control = qmc_opts['npop_control']
        self.temp = qmc_opts['temperature']
        self.importance_sampling = qmc_opts['importance_sampling']
        self.hubbard_stratonovich = qmc_opts.get('hubbard_stratonovich')
        if model['name'] == 'Hubbard':
            # sytem packages all generic information + model specific information.
            self.system = hubbard.Hubbard(model)
            self.gamma = numpy.arccosh(numpy.exp(0.5*self.dt*self.system.U))
            self.auxf = numpy.array([[numpy.exp(self.gamma), numpy.exp(-self.gamma)],
                                  [numpy.exp(-self.gamma), numpy.exp(self.gamma)]])
            # self.auxf = self.auxf * np.exp(-0.5*dt*self.system.U*self.system.ne)
            # Constant energy factor emerging from HS transformation.
            self.cfac = 0.5*self.system.U*self.system.ne
            if qmc_opts['hubbard_stratonovich'] == 'continuous':
                self.two_body = hs_transform.construct_generic_one_body(system.Hubbard.gamma)

        self.propagators = afqmcpy.propagation.Projectors(model['name'],
                                                         self.hubbard_stratonovich,
                                                         self.dt, self.system.T,
                                                         self.importance_sampling)
        cplx = 'continuous' in self.hubbard_stratonovich
        (self.psi_trial, self.sp_eigs) = trial_wave_function.free_electron(self.system,
                                                                           cplx)
        numpy.random.seed(qmc_opts['rng_seed'])
        # Handy to keep original dicts so they can be printed at run time.
        self.model = model
        self.qmc_opts = qmc_opts


    def write_json(self):

        # Combine some metadata in dicts so it can be easily printed/read.
        calc_info =  {
            'sha1': get_git_revision_hash(),
            'Run time': time.asctime()
        }
        derived = {
                'sp_eigv': self.sp_eigs.round(6).tolist()
        }
        # http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
        # ugh
        encoder.FLOAT_REPR = lambda o: format(o, '.6f')
        info = {
            'calculation': calc_info,
            'model': self.model,
            'qmc_options': self.qmc_opts,
            'derived': derived
        }
        # Note that we require python 3.6 to print dict in ordered fashion.
        print ("# Input options: ")
        print (json.dumps(info, sort_keys=False, indent=4))
        print ("# End of input options ")


def get_git_revision_hash():
    '''Return git revision.

    Adapted from: http://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script

Returns
-------
sha1 : string
    git hash with -dirty appended if uncommitted changes.
'''

    src = [s for s in sys.path if 'afqmcpy' in s][0]

    sha1 = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                   cwd=src).strip()
    suffix = subprocess.check_output(['git', 'status',
                                     '--porcelain',
                                     '.'],
                                     cwd=src).strip()
    if suffix:
        return sha1.decode('utf-8') + '-dirty'
    else:
        return sha1.decode('utf-8')
