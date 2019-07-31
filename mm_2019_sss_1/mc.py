import os
import numpy as np
import time
from .geom import Geom
from .energy import Energy
import matplotlib.pyplot as plt


class MC:
    """
    This is a class for the operations of a Monte Carlo simulation.

    Attributes
    ----------
        method : string
            Name of the coordinate file or "random" to generate random starting coordinates.
        reduced_temp : float
            Reduced temperature given the temperature of the system and its critical temperature. 
        max_displacement : float
            Magnitude of particle displacement for Monte Carlo steps.
        cutoff : float
            Distance limit for computation of LJ potential.
        num_particles : int
            Number of particles in the system.  
        file_name : string
            Name of the xyz coordinates file. File extension has to be included.
        tune_displacement : Boolean
            If True the magnitude of displacement is adjusted base on acceptance rate. 
        reduced_den : float
            Reduced density given system density and sigma value. 
        performance : float
            Performance of simulation in seconds / per step

    Methods
    -------
        run :
            Execute the MC simulation and trigger other output related functionality.
        save_snapshot :
            Obtain the current snapshot stored as a Geom object.
        plot : 
            Create an energy plot and optionally save it in png format.
    """
    def __init__(self,
                 method,
                 reduced_temp,
                 max_displacement,
                 cutoff,
                 num_particles=None,
                 file_name=None,
                 tune_displacement=True,
                 reduced_den=None):
        """
        Initialize a MC simulation object

        Parameters
        ----------
        method : string, either 'random' or 'file'
            Method to initialize system.
            random: Randomly create initial configuration.
            file: Initialize system by reading from a file.
        reduced_temp : float
            Reduced temperature at which the simulation will run.
        max_displacement : float
            Maximum trial move displacement in each dimension.
        cutoff : float
            Cutoff distance for energy calculation.
        tune_displacement : Boolean, default to True
            Whether to tune maximum displacement in trial move based on previous acceptance probability.
        num_particles : int, required if method is 'random'
            Number of particles in the system.
        reduced_den : float, required if method is 'random'
            Reduced density of the system.
        file_name : string, required if method is 'file'
            Name of file from which initial configuration will be read and generated.

        Returns
        -------
        None
        """

        self.beta = 1. / float(reduced_temp)
        self._n_trials = 0
        self._n_accept = 0
        self.max_displacement = max_displacement
        self.tune_displacement = tune_displacement
        self._energy_array = np.array([])
        self.current_step = 0

        if method == 'random':
            self._Geom = Geom(method, num_particles=num_particles, reduced_den=reduced_den)
        elif method == 'file':
            self._Geom = Geom(method, file_name=file_name)
        else:
            raise ValueError("Method must be either 'file' or 'random'")

        if reduced_den < 0.0 or reduced_temp < 0.0:
            raise ValueError("reduced temperature and density must be greater than zero.")

        self._Energy = Energy(self._Geom, cutoff)

    def _accept_or_reject(self, delta_e):
        """
        Test to decide if move is accepted or rejected given the energy differece between previous and current step

        Parameters
        ----------
        delta_e : float
            energy difference between previous and current steps.

        Return
        ------
        accept : Boolean data type
            If the delta_e passes the criteria, the move is accepted
        """

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
        """
        Adjust maximum trial move displacement in each dimension based on previous acceptance probability.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        acc_rate = float(self._n_accept) / float(self._n_trials)
        if (acc_rate < 0.38):
            self.max_displacement *= 0.8
        elif (acc_rate > 0.42):
            self.max_displacement *= 1.2
        self._n_trials = 0
        self._n_accept = 0

    def get_energy(self):
        """
        Get the current energy trace.

        Parameters
        ----------
        None

        Returns
        -------
        1d Numpy array of current energy trace.
        
        """

        if (len(self._energy_array) == 0):
            raise ValueError("Simulation has not started running!")
        return self._energy_array

    def get_snapshot(self):
        """
        Obtain the current snapshot stored as a Geom object.

        Parameters
        ----------
        None

        Returns
        -------
        self._Geom : object
            Geom object instance.
        """

        return self._Geom

    def save_snapshot(self, file_name):
        """
        Call save_state function from Geom class and generate current simulation state into a text file. First line is box dimension, second is number of particles, and the rest are particle coordinates.

        Parameters
        ----------
        file_name : string
          Name of output file for the snapshot

        Returns
        -------
        None
        """
        self._Geom.save_state(file_name)

    def run(self, n_steps, freq, save_dir='./results', save_snaps=False):
        """
        Execute the MC simulation and trigger other output related functionality.

        Parameters
        ----------
        n_steps : int
            The number of steps for this simulation.
        freq : int
            The frequency to update log file and generate in-screen check message.
        save_dir : str
            The file path to store the result. default = './results'
        save_snaps : bool
            Whether to output snapshot.

        Returns
        -------
        None
        """

        self.freq = freq
        if (not os.path.exists(save_dir)):
            os.mkdir(save_dir)

        if (not os.path.exists(save_dir + "/results.log")):
            log = open("./results/results.log", "w+")
            log.write('Starting MC!\n')
            log.write('Step' + '    |    ' + 'Energy\n')
            log.write('-------------------\n')
        else:
            log = open(save_dir + "/results.log", "a")
            log.write(f'\nStarting from step {self.current_step}\n')

        tail_correction = self._Energy.calculate_tail_correction()
        total_pair_energy = self._Energy.calculate_total_pair_energy()
        if self.current_step == 0:
            self._energy_array = np.append(self._energy_array, np.zeros(n_steps + 1))
            self._energy_array[0] = total_pair_energy
        else:
            self._energy_array = np.append(self._energy_array, np.zeros(n_steps))

        start = time.time()
        for i_step in range(1, n_steps + 1):
            self.current_step += 1
            self._n_trials += 1

            i_particle = np.random.randint(self._Geom.num_particles)
            random_displacement = (2.0 * np.random.rand(3) - 1.0) * self.max_displacement

            current_energy = self._Energy.get_particle_energy(i_particle, self._Geom.coordinates)
            old_coordinate = self._Geom.coordinates[i_particle, :].copy()
            proposed_coordinate = self._Geom.wrap(old_coordinate + random_displacement)
            self._Geom.coordinates[i_particle, :] = proposed_coordinate

            proposed_energy = self._Energy.get_particle_energy(i_particle, self._Geom.coordinates)
            delta_e = proposed_energy - current_energy
            accept = self._accept_or_reject(delta_e)

            if accept:
                total_pair_energy += delta_e
                self._n_accept += 1
            else:
                self._Geom.coordinates[i_particle, :] = old_coordinate

            total_energy = (total_pair_energy + tail_correction) / self._Geom.num_particles
            self._energy_array[self.current_step] = total_energy

            if np.mod(i_step + 1, freq) == 0:
                log.write(str(self.current_step + 1) + '    |    ' + str(self._energy_array[self.current_step]))
                log.write('\n')
                print(f"Step: {self.current_step + 1} | Energy: {round(self._energy_array[self.current_step],5)}")
                if save_snaps:
                    self.save_snapshot('%s/snap_%d.txt' % (save_dir, i_step + 1))
                if self.tune_displacement:
                    self._adjust_displacement()
        self.performance = (time.time() - start) / n_steps
        print(f"Performance: {round(1000*self.performance, 5)} seconds / 1000 steps")
        log.write('--------------------------------------------\n')
        log.write(f"Performance: {1000*self.performance} seconds / 1000 steps")
        log.close()

    def plot(self, energy_plot=True, save_plot=False):
        """
        Create an energy plot

        Parameters
        ----------
        energy_plot = Boolean
            If true plot is created
        save_plot = Boolean
            If true plot is saved to results folder

        Returns
        -------
        None
        """

        x_axis = np.array(np.arange(0, self.current_step, self.freq))
        if energy_plot:
            plt.figure(figsize=(10, 6), dpi=150)
            plt.title('LJ potential energy')
            plt.xlabel('Step')
            plt.ylabel('Potential Energy (reduced units)')
            y_axis = self._energy_array[self.freq::self.freq]
            offset = np.abs(np.percentile(y_axis, 50))
            plt.ylim(self._energy_array[-1] - offset, self._energy_array[-1] + offset)
            plt.plot(x_axis, y_axis)
            if save_plot:
                plt.savefig('./results/energy.png')