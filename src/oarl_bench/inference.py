import numpy as np
from numpy.polynomial.hermite import hermgauss

EPS = 1e-15

def normalize(logp: np.ndarray) -> np.ndarray:
    z = logp - np.max(logp)
    p = np.exp(z)
    return p / p.sum()

def update_posterior(posterior: np.ndarray, means_h: np.ndarray, sigma: float, y: float) -> np.ndarray:
    loglike = -0.5 * ((y - means_h) / sigma) ** 2 - np.log(sigma)
    logpost = np.log(np.clip(posterior, EPS, None)) + loglike
    return normalize(logpost)

def entropy(p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1.0)
    return float(-np.sum(p * np.log(p)))

def info_gain_proxy(posterior: np.ndarray, means_h: np.ndarray, sigma: float) -> float:
    m = float(np.sum(posterior * means_h))
    var = float(np.sum(posterior * (means_h - m) ** 2))
    return 0.5 * float(np.log1p(var / (sigma * sigma)))

def info_gain_quadrature(posterior: np.ndarray, means_h: np.ndarray, sigma: float, points: int = 12) -> float:
    x, w = hermgauss(points)
    w = w / np.sqrt(np.pi)
    posterior = np.clip(posterior, EPS, 1.0)
    posterior = posterior / posterior.sum()
    total = 0.0
    const = -0.5 * np.log(2.0 * np.pi * sigma * sigma)
    for h, ph in enumerate(posterior):
        if ph <= EPS:
            continue
        ys = means_h[h] + np.sqrt(2.0) * sigma * x
        log_cond = const - 0.5 * ((ys - means_h[h]) / sigma) ** 2
        diffs = (ys[:, None] - means_h[None, :]) / sigma
        log_components = np.log(posterior[None, :]) + const - 0.5 * diffs ** 2
        mx = np.max(log_components, axis=1, keepdims=True)
        log_mix = mx[:, 0] + np.log(np.sum(np.exp(log_components - mx), axis=1))
        total += ph * float(np.sum(w * (log_cond - log_mix)))
    return max(0.0, total)

def information_gain(posterior: np.ndarray, means_h: np.ndarray, sigma: float, mode: str = "proxy", quadrature_points: int = 12) -> float:
    if mode == "proxy":
        return info_gain_proxy(posterior, means_h, sigma)
    if mode == "quadrature":
        return info_gain_quadrature(posterior, means_h, sigma, points=quadrature_points)
    raise ValueError(f"Unknown IG mode: {mode}")
