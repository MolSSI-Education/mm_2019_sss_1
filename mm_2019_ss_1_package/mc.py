import os
import numpy as np
from .geom import Geom
from .energy import Energy
import matplotlib.pyplot as plt

class MC:

    def __init__(self, method, reduced_temp, max_displacement, cutoff, num_particles = None, file_name = None, tune_displacement = True, reduced_den = None):
        self.beta = 1./float(reduced_temp)
        self._n_trials = 0
        self._n_accept = 0
        self.max_displacement = max_displacement
        self.tune_displacement = tune_displacement
        self._energy_array = np.array([])
        self.current_step = 0

        if method == 'random':
            self._Geom = Geom(method, num_particles = num_particles, reduced_den = reduced_den)
        elif method == 'file':
            self._Geom = Geom(method, file_name = file_name)
        else:
            raise ValueError("Method must be either 'file' or 'random'")
        
        if reduced_den < 0.0 or reduced_temp < 0.0:
            raise ValueError("reduced temperature and density must be greater than zero.")

        self._Energy = Energy(self._Geom, cutoff)

    def _accept_or_reject(self,delta_e):
        if delta_e < 0.0:
            accept = True
        else:
            random_number = np.random.rand(1)
            p_acc = np.exp(-self.beta * delta_e)
            if random_number < p_acc:
                accept = True
            else:
                accept = False
        return accept

    def _adjust_displacement(self):
        acc_rate = float(self._n_accept) / float(self._n_trials)
        if (acc_rate < 0.38):
            self.max_displacement *= 0.8
        elif (acc_rate > 0.42):
            self.max_displacement *= 1.2
        self._n_trials = 0
        self._n_accept = 0

    def get_energy(self):
        if (self._energy_array is None):
            raise ValueError("Simulation has not started running!")
        return self._energy_array

    def get_snapshot(self):
        return self._Geom

    def save_snapshot(self,file_name):
        self._Geom.save_state(file_name)

    def run(self, n_steps, freq, save_dir = './results', save_snaps = False):
        self.freq = freq
        if (not os.path.exists(save_dir)):
            os.mkdir(save_dir)
        
        log = open("./results/results.log","w+")
        log.write('Step        Energy\n')

        tail_correction = self._Energy.calculate_tail_correction()
        total_pair_energy = self._Energy.calculate_total_pair_energy()
        if self.current_step == 0:
            self._energy_array = np.append(self._energy_array,np.zeros(n_steps+1))
            self._energy_array[0] = total_pair_energy
        else:
            self._energy_array = np.append(self._energy_array,np.zeros(n_steps))

        for i_step in range(1,n_steps+1):
            self.current_step += 1
            self._n_trials += 1

            i_particle = np.random.randint(self._Geom.num_particles)
            random_displacement = (2.0 * np.random.rand(3) - 1.0) * self.max_displacement

            current_energy = self._Energy.get_particle_energy(i_particle, self._Geom.coordinates)
            old_coordinate = self._Geom.coordinates[i_particle,:].copy()
            proposed_coordinate = self._Geom.wrap(old_coordinate + random_displacement)
            self._Geom.coordinates[i_particle,:] = proposed_coordinate

            proposed_energy = self._Energy.get_particle_energy(i_particle, self._Geom.coordinates)
            delta_e = proposed_energy - current_energy
            accept = self._accept_or_reject(delta_e)

            if accept:
                total_pair_energy += delta_e
                self._n_accept += 1
            else:
                self._Geom.coordinates[i_particle,:] = old_coordinate

            total_energy = (total_pair_energy + tail_correction) / self._Geom.num_particles
            self._energy_array[self.current_step] = total_energy


            if np.mod(i_step + 1, freq) == 0:
                log.write(str(i_step + 1)+'         '+str(self._energy_array[self.current_step]))
                log.write('\n')
                print(i_step + 1, self._energy_array[self.current_step])
                if save_snaps:
                    self.save_snapshot('%s/snap_%d.txt'%(save_dir,i_step+1))
                if self.tune_displacement:
                    self._adjust_displacement()
        log.close()
        

    def plot(self, energy_plot):
        ''' Create an energy plot

        Parameters
        ----------
        energy_plot = Boolean
            If true plot is created

        Returns
        -------
        None
        '''
        self.energy_plot = energy_plot
        x_axis = np.array(np.arange(0, self.current_step, self.freq))
        y_axis = []
        if energy_plot:
            plt.figure(figsize=(10,6), dpi=150)
            plt.title('LJ potential energy')
            plt.xlabel('Step')
            plt.ylabel('Potential Energy (reduced units)')
            y_axis = self._energy_array[self.freq::self.freq]
            plt.ylim(self._energy_array[-1]-20, self._energy_array[-1]+20)
            plt.plot(x_axis, y_axis)
            plt.savefig('./results/energy.png')


if __name__ == "__main__":
    import time
    start = time.time()
    sim = MC(method = 'random', num_particles = 100, reduced_den = 0.9, reduced_temp = 0.9, max_displacement = 0.1, cutoff = 3.0)
    sim.run(n_steps = 5000, freq = 100, save_snaps= True)
    sim.plot(energy_plot = True)
    end = time.time()
    print ("Sim takes %10.5f seconds"%(end-start))
