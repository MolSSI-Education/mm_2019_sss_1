import numpy as np

class Energy:

    def __init__(self, Geom, cutoff):
        self.Geom = Geom 
        self.cutoff  = cutoff
        self.cutoff2 = self.cutoff**2

    def lennard_jones_potential(self,rij2):
        sig_by_r6 = np.power(1 / rij2, 3)
        sig_by_r12 = np.power(sig_by_r6, 2)
        return 4.0 * (sig_by_r12 - sig_by_r6)

    def get_particle_energy(self, i_particle, coordinates):
        r_i = coordinates[i_particle]
        rij2 = self.Geom.minimum_image_distance(r_i, coordinates)
        red = np.delete(rij2, i_particle)
        pot = self.lennard_jones_potential(red[red < self.cutoff2])
        e_total = pot.sum()
        return e_total

    def calculate_total_pair_energy(self):
        e_total = 0.0
        particle_count = len(self.Geom.coordinates)
        for i_particle in range(particle_count):
            e_total += self.get_particle_energy(i_particle,self.Geom.coordinates)
        return e_total/2
    
    def calculate_tail_correction(self):
        num_particles = self.Geom.num_particles
        sig_by_cutoff3 = np.power(1.0 / self.cutoff, 3)
        sig_by_cutoff9 = np.power(sig_by_cutoff3, 3)
        e_correction = sig_by_cutoff9 - 3.0 * sig_by_cutoff3
        e_correction *= 8.0 / 9.0 * np.pi * num_particles / self.Geom.volume * num_particles
        return e_correction