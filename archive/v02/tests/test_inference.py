import numpy as np
from oarl_bench.inference import update_posterior, information_gain

def test_posterior_moves_toward_matching_hypothesis():
    p = np.array([0.5, 0.5])
    means = np.array([0.0, 5.0])
    post = update_posterior(p, means, sigma=1.0, y=0.1)
    assert post[0] > p[0]

def test_zero_separation_zero_proxy_information():
    p = np.array([0.5, 0.5])
    means = np.array([2.0, 2.0])
    ig = information_gain(p, means, sigma=1.0, mode="proxy")
    assert abs(ig) < 1e-12

def test_quadrature_positive_when_separated():
    p = np.array([0.5, 0.5])
    means = np.array([-2.0, 2.0])
    ig = information_gain(p, means, sigma=1.0, mode="quadrature", quadrature_points=16)
    assert ig > 0.2
