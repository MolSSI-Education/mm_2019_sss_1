"""
Unit and regression test for the mm_2019_ss_1_package package.
"""

# Import package, test suite, and other packages as needed
import mm_2019_ss_1_package as mm
#from mm_2019_ss_1_package import Energy, Geom 
import pytest
import sys
import numpy as np
import glob
import shutil

@pytest.fixture()
def trial_sim():
    # Changed the fixture to so we can pass arguments
    def _get_trial_sim(method = 'random', num_particles = 1000, reduced_den = 1.0, reduced_temp = 1.0, max_displacement = 0.1, cutoff = 3.0):
        trial_sim = mm.MC(method = method, num_particles = num_particles, reduced_den = reduced_den, reduced_temp = reduced_temp, max_displacement = max_displacement, cutoff = cutoff)
        return trial_sim

    return _get_trial_sim

def test_mm_2019_ss_1_package_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mm_2019_ss_1_package" in sys.modules


def test_minimum_image_distance():
    """Test the method to calculate minimum image distance. Arguments for MC.py are set to be easy ones so that expected value is 2"""

    G = mm.geom.Geom(method = 'random', num_particles = 1000, reduced_den = 1.0)
    trial_point1 = np.array([1,0,0])
    trial_point2 = np.array([9,0,0])
    
    calculated_value = G.minimum_image_distance(trial_point1 , trial_point2)
    expected_value = 2.0 ** 2

    assert np.isclose(calculated_value , expected_value)

def test_energy():
	"""
	Check the total pair energy calculation matches reference LJ calculation in NIST
	"""
	samples = glob.glob('mm_2019_ss_1_package/tests/lj_sample_configurations/*.txt')
	samples.sort()

	# Test r_cut = 3.0
	r_cut = 3.0
	reference = np.array([-4.3515E+03,-6.9000E+02,-1.1467E+03,-1.6790E+01])
	calculation = np.zeros(len(samples))
	for i in range(len(samples)):
		sample = samples[i]
		geom = mm.geom.Geom(method='file',file_name=sample)
		energy = mm.energy.Energy(geom,r_cut)
		E_total = energy.calculate_total_pair_energy()
		calculation[i] = E_total
	assert np.allclose(np.around(reference,decimals=1),np.around(calculation,decimals=1))

	# Test r_cut = 4.0
	r_cut = 4.0
	reference = np.array([-4.4675E+03,-7.0460E+02,-1.1754E+03,-1.7060E+01])
	calculation = np.zeros(len(samples))
	for i in range(len(samples)):
		sample = samples[i]
		geom = mm.geom.Geom(method='file',file_name=sample)
		energy = mm.energy.Energy(geom,r_cut)
		E_total = energy.calculate_total_pair_energy()
		calculation[i] = E_total
	assert np.allclose(np.around(reference,decimals=1),np.around(calculation,decimals=1))

def test_individual_lj_potential():
    """
    Check if the basic calculation of LJ potential is working.
    """
    
    rij2 = 2.0
    
    test_E = mm.energy.Energy(None,3.0)
    calculated_result = test_E.lennard_jones_potential(rij2)
    expected_result = 4.0 * ( 1./64 - 1./8 )

    assert np.isclose( calculated_result , expected_result)



def test_get_particle_energy():
    """
    Check if the particle energy calculation works for a simple setup.
    """

    trial_coordinates = np.array( [ [4,5,5] , [6,5,5] , [5,5,5] , [5,4,5] , [5,6,5] ] )
    ith_particle = 2
    G = mm.geom.Geom(method = 'random', num_particles = 1, reduced_den = 0.001)
    E = mm.energy.Energy(G, cutoff = 3.0)
    calculated_result = E.get_particle_energy( i_particle = ith_particle , coordinates = trial_coordinates )
    expected_result = 0

    assert np.isclose( calculated_result , expected_result )


def test_wrap():
    """
    Check if the warp method works for periodic box.
    """

    vec_to_wrap = np.array([11 , 12 , 13])

    G = mm.geom.Geom(method = 'random', num_particles = 1000 , reduced_den = 1)

    calculated_result = G.wrap( v = vec_to_wrap)
    expected_result = np.array([1 , 2 , 3])

    assert np.allclose( calculated_result , expected_result )


def test_tail_correction():
    """
    Check if the tail correction works.
    """

    G = mm.geom.Geom(method = 'random', num_particles = 1000, reduced_den = 1)
    E = mm.energy.Energy(G, cutoff = 1.0)

    calculated_result = E.calculate_tail_correction()
    expected_result = (-2.0) * 8.0/9.0 * np.pi * 1000 / 1000 * 1000

    assert np.isclose( calculated_result , expected_result )

def test_run():
    sim = mm.MC(method = 'random', num_particles = 100, reduced_den = 0.9, reduced_temp = 0.9, max_displacement = 0.1, cutoff = 3.0)
    sim.run(n_steps = 5000, freq = 100, save_snaps= True)
    sim.plot(energy_plot = True)
    shutil.rmtree("./results", ignore_errors = True)    
