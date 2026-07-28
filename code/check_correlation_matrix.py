"""Audit the four-dimensional Brownian correlation matrix of the application.

Equation (32) of Brandt and Santa-Clara (2002) specifies the instantaneous
correlation matrix of ``(W, W*, X, Y)``, where ``W`` and ``W*`` drive the two
interest rates, ``X`` drives the log exchange rate and ``Y`` drives the
incompleteness state.  Three of its entries are free parameters and three are
implied by the decomposition of the exchange-rate diffusion, so the matrix is
partly state dependent.

A valid Brownian system requires the matrix to be positive semidefinite at
every state and parameter value that the model can reach.  Constraining each
entry to ``[-1, 1]`` is necessary but not sufficient.  This module reconstructs
the matrix, checks it, and reports the minimum eigenvalue and the Schur
complement of the block that contains the free entries.

Nothing here silently repairs an invalid matrix.  ``nearest_correlation`` is
available for diagnosis but must be called explicitly.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "paper" / "tables"

# Symmetry and unit-diagonal tolerance.  Entries are built from reported
# estimates quoted to three decimals, so this is far tighter than the data.
TOLERANCE = 1e-12


@dataclass(frozen=True)
class SystemParameters:
    """Reported estimates for one currency pair, from Table 3.

    Attributes
    ----------
    name:
        Currency pair label.
    phi, phi_star:
        Market prices of domestic and foreign interest-rate risk, entering as
        ``phi_t = phi * sqrt(r_t)``.
    rho_ww_star:
        Correlation between the two interest-rate Brownian motions.
    rho_wy, rho_w_star_y, rho_xy:
        The three free correlations with the incompleteness Brownian motion.
    theta, theta_star:
        Long-run interest-rate means, used as the reference state.
    mean_volatility:
        Sample mean of the observed exchange-rate volatility.
    """

    name: str
    phi: float
    phi_star: float
    rho_ww_star: float
    rho_wy: float
    rho_w_star_y: float
    rho_xy: float
    theta: float
    theta_star: float
    mean_volatility: float


# Table 3 of Brandt and Santa-Clara (2002); mean volatilities from their
# Section 4.3.3 discussion (10.3 per cent and 10.7 per cent annualised).
US_UK = SystemParameters(
    name="U.S. vs. U.K.",
    phi=-0.138,
    phi_star=0.027,
    rho_ww_star=0.057,
    rho_wy=0.048,
    rho_w_star_y=0.034,
    rho_xy=-0.012,
    theta=0.053,
    theta_star=0.074,
    mean_volatility=0.103,
)

US_DE = SystemParameters(
    name="U.S. vs. Germany",
    phi=-0.125,
    phi_star=-0.036,
    rho_ww_star=0.213,
    rho_wy=0.058,
    rho_w_star_y=-0.034,
    rho_xy=0.006,
    theta=0.058,
    theta_star=0.064,
    mean_volatility=0.107,
)


def implied_correlations(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
    volatility: float,
) -> tuple[float, float]:
    """Return the state-dependent correlations of ``X`` with ``W`` and ``W*``.

    From equation (28), ``v dX = phi dW - phi* dW* + psi dZ - psi* dZ* + eps dU``,
    so that ``corr(W, X) = (phi_t - rho_ww* phi*_t) / v_t`` and
    ``corr(W*, X) = (rho_ww* phi_t - phi*_t) / v_t``.
    """
    if rate < 0.0 or rate_star < 0.0:
        raise ValueError("interest rates must be nonnegative")
    if volatility <= 0.0:
        raise ValueError("volatility must be strictly positive")
    phi_t = parameters.phi * math.sqrt(rate)
    phi_star_t = parameters.phi_star * math.sqrt(rate_star)
    rho = parameters.rho_ww_star
    return (
        (phi_t - rho * phi_star_t) / volatility,
        (rho * phi_t - phi_star_t) / volatility,
    )


def minimum_feasible_volatility(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
) -> float:
    """Return the smallest volatility consistent with the variance identity.

    Equation (29) decomposes ``v_t^2`` into an interest-rate quadratic form, a
    currency quadratic form and ``eps_t^2``.  The last two are nonnegative, so

        v_t^2 >= phi_t^2 + phi*_t^2 - 2 rho_ww* phi_t phi*_t =: Q_t,

    and states with ``v_t < sqrt(Q_t)`` are not reachable by the model.  This
    matters for the audit: such states produce implied correlations outside
    ``[-1, 1]``, but they are excluded by the model rather than evidence
    against it.
    """
    phi_t = parameters.phi * math.sqrt(rate)
    phi_star_t = parameters.phi_star * math.sqrt(rate_star)
    quadratic = phi_t**2 + phi_star_t**2 - 2.0 * parameters.rho_ww_star * phi_t * phi_star_t
    return math.sqrt(max(quadratic, 0.0))


def induced_xy_correlation(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
) -> float:
    """Return the correlation of ``X`` with ``Y`` forced at the volatility floor.

    At ``v_t = sqrt(Q_t)`` the currency quadratic form and ``eps_t^2`` both
    vanish, so equation (28) reduces to ``v dX = phi_t dW - phi*_t dW*`` and
    ``X`` is a deterministic combination of ``W`` and ``W*``.  Its correlation
    with ``Y`` is then no longer free but equal to

        (phi_t rho_wy - phi*_t rho_w*y) / v_t.

    The model estimates ``rho_xy`` as a free parameter, so a mismatch between
    the estimate and this induced value makes the 4x4 matrix indefinite even
    though every entry lies in ``[-1, 1]``.
    """
    floor = minimum_feasible_volatility(parameters, rate, rate_star)
    if floor <= 0.0:
        raise ValueError("the volatility floor is zero, so X is not determined")
    phi_t = parameters.phi * math.sqrt(rate)
    phi_star_t = parameters.phi_star * math.sqrt(rate_star)
    return (phi_t * parameters.rho_wy - phi_star_t * parameters.rho_w_star_y) / floor


def build_matrix(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
    volatility: float,
) -> NDArray[np.float64]:
    """Reconstruct the 4x4 correlation matrix of equation (32).

    Ordering is ``(W, W*, X, Y)``.
    """
    rho_wx, rho_w_star_x = implied_correlations(parameters, rate, rate_star, volatility)
    rho = parameters.rho_ww_star
    matrix = np.array(
        [
            [1.0, rho, rho_wx, parameters.rho_wy],
            [rho, 1.0, rho_w_star_x, parameters.rho_w_star_y],
            [rho_wx, rho_w_star_x, 1.0, parameters.rho_xy],
            [parameters.rho_wy, parameters.rho_w_star_y, parameters.rho_xy, 1.0],
        ],
        dtype=np.float64,
    )
    validate_shape(matrix)
    return matrix


def validate_shape(matrix: NDArray[np.float64]) -> None:
    """Raise if the argument is not a square symmetric unit-diagonal matrix."""
    if matrix.ndim != 2:
        raise ValueError(f"expected a 2-dimensional array, got {matrix.ndim} dimensions")
    rows, columns = matrix.shape
    if rows != columns:
        raise ValueError(f"expected a square matrix, got shape {matrix.shape}")
    if rows < 2:
        raise ValueError("a correlation matrix needs at least two variables")
    if not np.allclose(matrix, matrix.T, atol=TOLERANCE, rtol=0.0):
        worst = float(np.abs(matrix - matrix.T).max())
        raise ValueError(f"matrix is not symmetric; largest asymmetry {worst:.3e}")
    diagonal_error = float(np.abs(np.diag(matrix) - 1.0).max())
    if diagonal_error > TOLERANCE:
        raise ValueError(f"diagonal entries are not one; largest deviation {diagonal_error:.3e}")


def schur_complement(matrix: NDArray[np.float64]) -> float:
    """Return ``1 - r' A^{-1} r`` for the block form ``[[A, r], [r', 1]]``.

    ``A`` is the leading block, here the correlations among ``(W, W*, X)``, and
    ``r`` holds the correlations of those with the last variable.  The full
    matrix is positive definite if and only if ``A`` is positive definite and
    this quantity is strictly positive.
    """
    validate_shape(matrix)
    leading = matrix[:-1, :-1]
    cross = matrix[:-1, -1]
    eigenvalues = np.linalg.eigvalsh(leading)
    # A relative threshold: near the volatility floor the leading block is
    # numerically singular, and inverting it there would report a meaningless
    # Schur complement of order 1e13 rather than raising.
    if eigenvalues.min() <= 1e-8 * max(eigenvalues.max(), 1.0):
        raise ValueError(
            "the leading block is singular or indefinite, so the Schur "
            f"complement is undefined; minimum eigenvalue {eigenvalues.min():.6e}"
        )
    return float(1.0 - cross @ np.linalg.solve(leading, cross))


def leading_minors(matrix: NDArray[np.float64]) -> list[float]:
    """Return the leading principal minors, in increasing order of size."""
    validate_shape(matrix)
    return [float(np.linalg.det(matrix[: k + 1, : k + 1])) for k in range(matrix.shape[0])]


def audit(matrix: NDArray[np.float64]) -> dict[str, float | bool]:
    """Run every validity check and return the diagnostics."""
    validate_shape(matrix)
    off_diagonal = matrix[~np.eye(matrix.shape[0], dtype=bool)]
    eigenvalues = np.linalg.eigvalsh(matrix)
    minors = leading_minors(matrix)
    result: dict[str, float | bool] = {
        "entries_in_range": bool(np.all(np.abs(off_diagonal) <= 1.0)),
        "max_abs_off_diagonal": float(np.abs(off_diagonal).max()),
        "min_eigenvalue": float(eigenvalues.min()),
        "min_leading_minor": float(min(minors)),
        "positive_semidefinite": bool(eigenvalues.min() >= -TOLERANCE),
        "positive_definite": bool(eigenvalues.min() > TOLERANCE),
    }
    try:
        result["schur_complement"] = schur_complement(matrix)
    except ValueError:
        result["schur_complement"] = float("nan")
    return result


def nearest_correlation(
    matrix: NDArray[np.float64],
    iterations: int = 200,
) -> NDArray[np.float64]:
    """Project onto the nearest correlation matrix by alternating projections.

    Diagnostic only.  This is never applied automatically: an invalid matrix
    is a finding about the model, not something to be silently repaired.
    """
    validate_shape(matrix)
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    correction = np.zeros_like(matrix)
    current = matrix.copy()
    for _ in range(iterations):
        adjusted = current - correction
        values, vectors = np.linalg.eigh(adjusted)
        projected = (vectors * np.clip(values, 0.0, None)) @ vectors.T
        correction = projected - adjusted
        current = projected.copy()
        np.fill_diagonal(current, 1.0)
    return current


def _state_grid(parameters: SystemParameters) -> list[tuple[str, float, float, float]]:
    """Return reference states at which to evaluate the matrix."""
    theta, theta_star = parameters.theta, parameters.theta_star
    volatility = parameters.mean_volatility
    return [
        ("long-run means", theta, theta_star, volatility),
        ("rates doubled", 2.0 * theta, 2.0 * theta_star, volatility),
        ("rates halved", 0.5 * theta, 0.5 * theta_star, volatility),
        ("volatility halved", theta, theta_star, 0.5 * volatility),
        ("volatility at 4 per cent", theta, theta_star, 0.04),
        ("rates tripled, volatility 4 per cent", 3.0 * theta, 3.0 * theta_star, 0.04),
        ("rates tripled, volatility at its floor", 3.0 * theta, 3.0 * theta_star, -1.0),
    ]


def run_state_audit() -> pd.DataFrame:
    """Evaluate the matrix across reference states for both systems.

    A state with ``volatility <= 0`` in the grid is a request to use the
    smallest volatility the variance identity permits at those rates.  States
    below that floor are reported with ``feasible = False``: they produce
    invalid matrices, but they are excluded by the model, so they are evidence
    about the audit rather than about the model.
    """
    rows = []
    for parameters in (US_UK, US_DE):
        for label, rate, rate_star, volatility in _state_grid(parameters):
            floor = minimum_feasible_volatility(parameters, rate, rate_star)
            if volatility <= 0.0:
                volatility = floor
            matrix = build_matrix(parameters, rate, rate_star, volatility)
            diagnostics = audit(matrix)
            rows.append(
                {
                    "system": parameters.name,
                    "state": label,
                    "volatility": volatility,
                    "volatility_floor": floor,
                    "feasible": bool(volatility >= floor - TOLERANCE),
                    **diagnostics,
                }
            )
    return pd.DataFrame(rows)


def run_perturbation_audit(
    draws: int = 20_000,
    seed: int = 20260728,
) -> pd.DataFrame:
    """Perturb the free correlations by their reported standard errors.

    Standard errors from Table 3.  Draws that fall outside ``[-1, 1]`` for any
    individual correlation are retained deliberately, because the point of the
    exercise is to find out whether entrywise validity and joint validity can
    come apart.
    """
    rng = np.random.default_rng(seed)
    standard_errors = {
        "U.S. vs. U.K.": (0.012, 0.005, 0.005, 0.003),
        "U.S. vs. Germany": (0.046, 0.008, 0.009, 0.002),
    }
    rows = []
    for parameters in (US_UK, US_DE):
        se_ww, se_wy, se_wsy, se_xy = standard_errors[parameters.name]
        failures = 0
        entrywise_failures = 0
        worst_eigenvalue = math.inf
        for _ in range(draws):
            perturbed = SystemParameters(
                name=parameters.name,
                phi=parameters.phi,
                phi_star=parameters.phi_star,
                rho_ww_star=parameters.rho_ww_star + rng.normal(scale=se_ww),
                rho_wy=parameters.rho_wy + rng.normal(scale=se_wy),
                rho_w_star_y=parameters.rho_w_star_y + rng.normal(scale=se_wsy),
                rho_xy=parameters.rho_xy + rng.normal(scale=se_xy),
                theta=parameters.theta,
                theta_star=parameters.theta_star,
                mean_volatility=parameters.mean_volatility,
            )
            matrix = build_matrix(
                perturbed,
                perturbed.theta,
                perturbed.theta_star,
                perturbed.mean_volatility,
            )
            diagnostics = audit(matrix)
            worst_eigenvalue = min(worst_eigenvalue, float(diagnostics["min_eigenvalue"]))
            if not diagnostics["positive_semidefinite"]:
                failures += 1
            if not diagnostics["entries_in_range"]:
                entrywise_failures += 1
        rows.append(
            {
                "system": parameters.name,
                "draws": draws,
                "psd_failures": failures,
                "entrywise_failures": entrywise_failures,
                "worst_min_eigenvalue": worst_eigenvalue,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    """Run both audits, write the tables and print a summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=TABLES)
    parser.add_argument("--draws", type=int, default=20_000)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)

    states = run_state_audit()
    perturbations = run_perturbation_audit(draws=args.draws)

    states.to_csv(args.output_root / "correlation_audit.csv", index=False)
    perturbations.to_csv(args.output_root / "correlation_perturbation.csv", index=False)

    columns = ["system", "state", "max_abs_off_diagonal", "min_eigenvalue", "schur_complement"]
    (args.output_root / "correlation_audit.tex").write_text(
        states[columns].to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="llrrr",
        ),
        encoding="utf-8",
    )

    pd.set_option("display.width", 200)
    print(states.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print()
    print(perturbations.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
