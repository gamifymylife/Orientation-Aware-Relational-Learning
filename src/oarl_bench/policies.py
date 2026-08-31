from dataclasses import dataclass
import numpy as np
from .inference import information_gain
from .config import BenchmarkConfig
from .world import RelationalWorld

@dataclass
class Choice:
    orientation: int
    intervention: int
    score: float
    score_evals: int
    use_transport: bool = False


def _ig(world, posterior, o, a, cfg):
    return information_gain(
        posterior,
        world.means[:, o, a],
        float(world.nominal_sigma[o, a]),
        mode=cfg.ig_mode,
        quadrature_points=cfg.quadrature_points,
    )


def _ig_matrix(world: RelationalWorld, posterior: np.ndarray, cfg: BenchmarkConfig) -> np.ndarray:
    O, A = world.n_orientations, world.n_interventions
    if cfg.ig_mode == "proxy":
        m = np.tensordot(posterior, world.means, axes=(0, 0))
        centered = world.means - m[None, :, :]
        var = np.tensordot(posterior, centered * centered, axes=(0, 0))
        return 0.5 * np.log1p(var / (world.nominal_sigma * world.nominal_sigma))
    out = np.empty((O, A), dtype=float)
    for o in range(O):
        for a in range(A):
            out[o, a] = _ig(world, posterior, o, a, cfg)
    return out


def _ig_subset(world: RelationalWorld, posterior: np.ndarray, orientations: np.ndarray, cfg: BenchmarkConfig) -> np.ndarray:
    means = world.means[:, orientations, :]
    sigma = world.nominal_sigma[orientations, :]
    if cfg.ig_mode == "proxy":
        m = np.tensordot(posterior, means, axes=(0, 0))
        centered = means - m[None, :, :]
        var = np.tensordot(posterior, centered * centered, axes=(0, 0))
        return 0.5 * np.log1p(var / (sigma * sigma))
    out = np.empty((len(orientations), world.n_interventions), dtype=float)
    for i, o in enumerate(orientations):
        for a in range(world.n_interventions):
            out[i, a] = _ig(world, posterior, int(o), a, cfg)
    return out


def _choice_from_scores(scores: np.ndarray) -> Choice:
    flat = int(np.argmax(scores))
    o, a = np.unravel_index(flat, scores.shape)
    return Choice(int(o), int(a), float(scores[o, a]), int(scores.size))


def _cost_tiebreak_choice(world: RelationalWorld, scores: np.ndarray, valid_mask: np.ndarray | None = None) -> Choice:
    scores = np.array(scores, copy=True)
    if valid_mask is not None:
        scores[~valid_mask, :] = -np.inf
    max_score = float(np.max(scores))
    tied = np.isclose(scores, max_score, rtol=1e-10, atol=1e-12)
    candidate_cost = np.where(tied, world.cost, np.inf)
    flat = int(np.argmin(candidate_cost))
    o, a = np.unravel_index(flat, scores.shape)
    evals = int(np.sum(valid_mask) * world.n_interventions) if valid_mask is not None else int(scores.size)
    return Choice(int(o), int(a), float(scores[o, a]), evals)


def _structured_choice(world: RelationalWorld, posterior: np.ndarray, cfg: BenchmarkConfig, cheapest_equivalent: bool) -> Choice:
    active_classes = []
    reps = []
    for c, rep in enumerate(world.class_representative):
        members = np.where((world.orientation_class == c) & world.admissible)[0]
        if len(members) == 0:
            continue
        active_classes.append(c)
        reps.append(int(rep))
    reps = np.asarray(reps, dtype=int)
    if len(reps) == 0:
        raise RuntimeError("No admissible orientation classes")

    ig = _ig_subset(world, posterior, reps, cfg)
    flat = int(np.argmax(ig))
    row, canonical_a = np.unravel_index(flat, ig.shape)
    cls = int(active_classes[row])
    rep = int(reps[row])

    if not cheapest_equivalent:
        return Choice(rep, int(canonical_a), float(ig[row, canonical_a]), int(ig.size), False)

    members = np.where((world.orientation_class == cls) & world.admissible)[0]
    best_o, best_a, best_cost = rep, int(canonical_a), np.inf
    for o in members:
        local = np.where(world.to_canonical_intervention[o] == canonical_a)[0]
        if len(local) != 1:
            continue
        a = int(local[0])
        c = float(world.cost[o, a])
        if c < best_cost:
            best_o, best_a, best_cost = int(o), a, c
    return Choice(best_o, best_a, float(ig[row, canonical_a]), int(ig.size), True)


def choose_experiment(policy: str, world: RelationalWorld, posterior: np.ndarray, cfg: BenchmarkConfig, rng: np.random.Generator) -> Choice:
    O, A = world.n_orientations, world.n_interventions
    if policy == "passive":
        return Choice(0, int(rng.integers(A)), 0.0, 0)
    if policy == "random_orientation":
        return Choice(int(rng.integers(O)), int(rng.integers(A)), 0.0, 0)
    if policy == "fixed_oed":
        ig = _ig_matrix(world, posterior, cfg)[0:1, :]
        c = _choice_from_scores(ig)
        return Choice(0, c.intervention, c.score, A)
    if policy == "generic_oed":
        return _choice_from_scores(_ig_matrix(world, posterior, cfg))
    if policy == "generic_gated_oed":
        ig = _ig_matrix(world, posterior, cfg); ig[~world.admissible, :] = -np.inf
        c = _choice_from_scores(ig)
        return Choice(c.orientation, c.intervention, c.score, int(np.sum(world.admissible) * A))
    if policy == "generic_true_gated_oed":
        ig = _ig_matrix(world, posterior, cfg); ig[~world.true_admissible, :] = -np.inf
        c = _choice_from_scores(ig)
        return Choice(c.orientation, c.intervention, c.score, int(np.sum(world.true_admissible) * A))
    if policy == "generic_true_cost_tiebreak":
        return _cost_tiebreak_choice(world, _ig_matrix(world, posterior, cfg), world.true_admissible)
    if policy == "generic_cost_tiebreak":
        return _cost_tiebreak_choice(world, _ig_matrix(world, posterior, cfg), world.admissible)
    if policy == "structured_rep_oed":
        return _structured_choice(world, posterior, cfg, cheapest_equivalent=False)
    if policy == "structured_oarl":
        return _structured_choice(world, posterior, cfg, cheapest_equivalent=True)
    if policy in {"oarl_no_stability", "full_oarl"}:
        ig = _ig_matrix(world, posterior, cfg)
        if policy == "oarl_no_stability":
            scores = ig - cfg.gamma_cost * world.cost
        else:
            scores = ig - cfg.lambda_stability * np.log1p(world.stability)[:, None] - cfg.gamma_cost * world.cost
        return _choice_from_scores(scores)
    if policy == "oracle":
        hstar = world.true_h
        mu_true = world.means[hstar]
        sigma2 = world.nominal_sigma * world.nominal_sigma
        sq = (world.means - mu_true[None, :, :]) ** 2 / (2.0 * sigma2[None, :, :])
        alt_p = posterior.copy(); alt_p[hstar] = 0.0
        if alt_p.sum() <= 1e-15:
            sep = np.zeros((O, A), dtype=float)
        else:
            alt_p /= alt_p.sum(); sep = np.tensordot(alt_p, sq, axes=(0, 0))
        sep[~world.admissible, :] = -np.inf
        return _choice_from_scores(sep)
    raise ValueError(f"Unknown policy: {policy}")
