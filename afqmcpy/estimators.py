import numpy as np

def header():

    print ("%9s %14s %15s"%('iteration', 'Weight', 'E_num'))

def local_energy(system, walker):

    ke = np.sum(system.T * (walker.G[0] + walker.G[1]))
    pe = sum(system.U*walker.G[0][i][i]*walker.G[1][i][i] for i in range(0, system.nbasis))

    return ke + pe