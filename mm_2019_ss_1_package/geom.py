import numpy as np

class Geom:
    def __init__(self, method, **kwargs):
        self.generate_initial_state(method,**kwargs)

    def generate_initial_state(self,method,**kwargs):
        """Generate initial coordinates of particles in a box either randomly or based on a file.

        Parameters
        ----------
        method : string, either 'random' or 'file'
            Method of generating initial state.
        file_name : string
            Name of file used to generate initial state.
        num_particles : integer
            Number of particles to generate.
        box_length : integer or float
            Length of box to generate.

        Returns
        -------
        coordinates : array
            Array of particle coordinates generated for an initial state
        """

        if method is 'random':
            if (kwargs['num_particles'] == None or kwargs['reduced_den'] == None):
                raise ValueError(' "num_particles" and "reduced_den" arguments must be set for method=random!')
            self.num_particles = kwargs['num_particles']
            self.box_length = np.cbrt(self.num_particles / kwargs['reduced_den'])
            self.volume = self.box_length**3
            self.coordinates = (0.5 - np.random.rand(self.num_particles, 3)) * self.box_length

        elif method is 'file':
            if (kwargs['file_name'] == None):
                raise ValueError('"filename" argument must be set for method = file!')
            file_name = kwargs['file_name']
            with open(file_name) as f:
                lines = f.readlines()
                self.box_length = np.fromstring(lines[0], dtype=float, sep=',')[0]
                self.volume = self.box_length**3
                self.num_particles = np.fromstring(lines[1], dtype=float, sep=',')[0]
            self.coordinates = np.loadtxt(file_name, skiprows=2, usecols=(1,2,3))
            if (self.num_particles != self.coordinates.shape[0]):
                raise ValueError('Inconsistent value of number of particles in file!')

        else:
            raise TypeError('Method type not recognized.')

    def minimum_image_distance(self,r_i, coords):
        """Calculate minimum image distance between two particles, i and j.

        Parameters
        ---------
        box_length : integer or float
            Length of box to generate.
        r_i : array
            Coordinates of particle i.
        coords : array
            Coordintes of particle j or array of positions

        Returns
        -------
        rij2 : square of the distance between particles i and j, or particle i and all the coords.

        """
        rij = r_i - coords
        rij = rij - self.box_length * np.round(rij / self.box_length)
        rij2 = np.sum(rij**2,axis=-1)
        return rij2

    def wrap(self,v):
        """ Wrap a vector back to periodic box

        Parameters
        ----------
        v : the vector to be wrapped

        Returns
        -------
        wrapped_v : the vector wrapped back to simulation box
        """
        wrapped_v = v - self.box_length*np.round(v/self.box_length)
        return wrapped_v

    def get_particle_coordinates(self):
        """Get the coordinates of all particles in the system

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        return self.coordinates

    def save_state(self, file_name):
        """Save current simulation state into a txt file. First line is box dimension, second line is number of particles, and the rest are particle coordinates

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        import os.path
        if (os.path.exists(file_name)):
            raise ValueError("File already exists!")
        f = open(file_name,"w+")
        f.write("%.18e   %.18e   %.18e\n" %(self.box_length,self.box_length,self.box_length))
        f.write("%d\n"%(self.num_particles))
        f.close()
        f = open(file_name,'ab')
        np.savetxt(f,self.coordinates)
        f.close()




