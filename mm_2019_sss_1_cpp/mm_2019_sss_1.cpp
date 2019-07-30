#include <Eigen/Dense>

float get_particle_energy_cpp(Eigen::MatrixXd & coords, const int i_particle, const float box_length)
{
    Eigen::VectorXd r_i = coords.row(i_particle);
    return r_i.sum();
}