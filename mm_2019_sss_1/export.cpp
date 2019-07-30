#include "mm_2019_sss_1.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>


PYBIND11_MODULE(mm_2019_sss_1, m)
{
    m.doc() = "C++ functions used in MC code";
    m.def("get_particle_energy_cpp", get_particle_energy_cpp, "Calculates energy of a single particle");
}