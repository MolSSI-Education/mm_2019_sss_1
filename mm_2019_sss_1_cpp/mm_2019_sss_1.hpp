#pragma once
#include <Eigen/Dense>

float get_particle_energy_cpp(Eigen::MatrixXd & coords, const int i_particle, const float box_length);