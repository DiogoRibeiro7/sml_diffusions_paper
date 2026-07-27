"""Investigate whether the endpoint simulated-likelihood argmax can fail.

The density-level collapse theorem in the manuscript concerns the simulated
transition density at a point.  It says nothing directly about the maximiser of
the simulated log likelihood, and this module is the numerical half of the
investigation into whether a direct argmax counterexample is available.

The model is the location family

    dY_t = theta dt + dW_t,     Y_t in R^K,

observed at unit intervals, for which the Euler scheme is exact and the exact
maximum likelihood estimator is the mean increment.  Under common random
numbers the simulated criterion collapses to a closed form; see
``simulated_criterion`` and ``notes/argmax_counterexample.md``.

Run directly to reproduce the tables quoted in the notes.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.optimize import minimize
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
SEED = 20260728


@dataclass(frozen=True)
class Design:
    """One (N, M, S) design for the location model."""

    observations: int
    substeps: int
    simulations: int
    dimension: int

    def __post_init__(self) -> None:
        if min(self.observations, self.substeps, self.simulations, self.dimension) <= 0:
            raise ValueError("all design sizes must be positive")
        if self.substeps < 2:
            raise ValueError("substeps must be at least 2")

    @property
    def step(self) -> float:
        return 1.0 / float(self.substeps)


def simulated_criterion(
    theta: NDArray[np.float64],
    increments: NDArray[np.float64],
    innovations: NDArray[np.float64],
    step: float,
) -> float:
    """Return the negative simulated log likelihood at ``theta``.

    Under common random numbers the preterminal Euler draw for observation n
    and simulation s is

        Z_{n,s}(theta) = Y_n + theta (1 - h) + sqrt(1 - h) xi_{n,s},

    so the endpoint summand depends on theta only through the centred
    increment u_n(theta) = DeltaY_n - theta:

        G_{n,s}(theta) = phi(u_n(theta) - sqrt(1 - h) xi_{n,s}; 0, h I).

    The simulated transition density is therefore exactly a Gaussian kernel
    density estimate with bandwidth sqrt(h), built from the theta-independent
    sample {sqrt(1 - h) xi_{n,s}} and evaluated at u_n(theta).
    """
    if theta.shape[0] != increments.shape[1]:
        raise ValueError("theta and increments have inconsistent dimension")
    dimension = increments.shape[1]
    centred = (increments - theta)[:, None, :] - math.sqrt(1.0 - step) * innovations
    log_kernel = -(dimension / 2.0) * math.log(2.0 * math.pi * step) - (
        centred * centred
    ).sum(-1) / (2.0 * step)
    log_density = logsumexp(log_kernel, axis=1) - math.log(innovations.shape[1])
    return -float(log_density.sum())


def nearest_atom_objective(
    theta: NDArray[np.float64],
    increments: NDArray[np.float64],
    innovations: NDArray[np.float64],
    step: float,
) -> float:
    """Return the nearest-atom objective that dominates the criterion.

    Writing a_{n,s} = DeltaY_n - sqrt(1 - h) xi_{n,s}, the sandwich bound in
    the notes gives

        2h * (negative criterion) = sum_n min_s |theta - a_{n,s}|^2 + O(h log S)

    uniformly in theta, so the maximiser is governed by this objective.
    """
    atoms = increments[:, None, :] - math.sqrt(1.0 - step) * innovations
    distances = ((atoms - theta) ** 2).sum(-1)
    return float(distances.min(axis=1).sum())


def fit(
    design: Design,
    rng: np.random.Generator,
    restarts: int = 8,
    theta_true: NDArray[np.float64] | None = None,
) -> dict[str, float]:
    """Simulate one data set and maximise the simulated criterion.

    Multiple restarts are used because the criterion is a sum of logs of
    kernel density estimates and is not guaranteed to be unimodal.
    """
    dimension = design.dimension
    truth = np.zeros(dimension) if theta_true is None else np.asarray(theta_true, float)
    increments = truth + rng.normal(size=(design.observations, dimension))
    innovations = rng.normal(size=(design.observations, design.simulations, dimension))
    exact_mle = increments.mean(axis=0)

    best_value = math.inf
    best_point = exact_mle
    for restart in range(restarts):
        start = exact_mle if restart == 0 else exact_mle + rng.normal(scale=0.3, size=dimension)
        result = minimize(
            simulated_criterion,
            start,
            args=(increments, innovations, design.step),
            method="Nelder-Mead",
            options={"xatol": 1e-9, "fatol": 1e-9, "maxiter": 40000, "maxfev": 40000},
        )
        if result.fun < best_value:
            best_value, best_point = float(result.fun), result.x

    # How far apart are the restart optima?  A large spread would mean the
    # reported maximiser is an artefact of local optimisation.
    spread = 0.0
    for restart in range(1, restarts):
        start = exact_mle + rng.normal(scale=0.3, size=dimension)
        result = minimize(
            simulated_criterion,
            start,
            args=(increments, innovations, design.step),
            method="Nelder-Mead",
            options={"xatol": 1e-9, "fatol": 1e-9, "maxiter": 40000, "maxfev": 40000},
        )
        spread = max(spread, abs(float(result.fun) - best_value))

    return {
        "N": design.observations,
        "M": design.substeps,
        "S": design.simulations,
        "K": dimension,
        "effective_size": design.simulations / design.substeps ** (dimension / 2.0),
        "mle_error": float(np.linalg.norm(exact_mle - truth)),
        "simulated_error": float(np.linalg.norm(best_point - truth)),
        "gap": float(np.linalg.norm(best_point - exact_mle)),
        "root_n_gap": math.sqrt(design.observations)
        * float(np.linalg.norm(best_point - exact_mle)),
        "restart_objective_spread": spread,
    }


def limiting_shape(v_norm: float, dimension: int) -> float:
    """Return the conjectured limit criterion shape exp(|v|^2 / (K - 2)).

    Derived in the notes from a nearest-neighbour heuristic: conditionally on
    the data innovation the atoms are iid Gaussian, the expected squared
    nearest-atom distance scales as (S f(v))^{-2/K}, and averaging the
    resulting f(v)^{-2/K} over the data innovation gives a finite answer only
    when K > 2, with value proportional to exp(|v|^2 / (K - 2)).
    """
    if dimension <= 2:
        raise ValueError("the limiting shape is finite only for K > 2")
    return math.exp(v_norm**2 / (dimension - 2.0))


def run_consistency_study(rng: np.random.Generator) -> pd.DataFrame:
    """Grow N with the simulation design fixed, and record both errors."""
    rows = [
        fit(Design(observations=n, substeps=32, simulations=32, dimension=4), rng)
        for n in (200, 400, 800, 1600, 3200)
    ]
    return pd.DataFrame(rows)


def run_joint_path_study(rng: np.random.Generator) -> pd.DataFrame:
    """Follow the collapse path M = S while N grows."""
    rows = [
        fit(Design(observations=n, substeps=m, simulations=m, dimension=4), rng)
        for n, m in ((200, 8), (400, 16), (800, 32), (1600, 64))
    ]
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=NOTES)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)
    consistency = run_consistency_study(rng)
    joint = run_joint_path_study(rng)

    consistency.to_csv(args.output_root / "argmax_consistency.csv", index=False)
    joint.to_csv(args.output_root / "argmax_joint_path.csv", index=False)

    pd.set_option("display.width", 160)
    print("Fixed design (M = S = 32), N growing:")
    print(consistency.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print()
    print("Collapse path (M = S), N growing:")
    print(joint.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
