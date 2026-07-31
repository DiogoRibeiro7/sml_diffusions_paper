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
    currency_quadratic:
        The constant currency-risk quadratic form
        ``C = psi^2 + psi*^2 - 2 rho_zz* psi psi*`` under constant risk prices.
        Table 3 reports ``psi^2 - rho_zz* psi psi*`` and
        ``psi*^2 - rho_zz* psi psi*`` separately, and ``C`` is their sum.
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
    currency_quadratic: float


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
    currency_quadratic=0.024 + (-0.021),
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
    currency_quadratic=(-0.010) + 0.013,
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


def interest_rate_quadratic(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
) -> float:
    """Return ``Q_t = phi_t^2 + phi*_t^2 - 2 rho_ww* phi_t phi*_t``."""
    if rate < 0.0 or rate_star < 0.0:
        raise ValueError("interest rates must be nonnegative")
    phi_t = parameters.phi * math.sqrt(rate)
    phi_star_t = parameters.phi_star * math.sqrt(rate_star)
    return phi_t**2 + phi_star_t**2 - 2.0 * parameters.rho_ww_star * phi_t * phi_star_t


def minimum_feasible_volatility(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
) -> float:
    """Return the smallest volatility the *complete* variance identity permits.

    Equation (29) is

        v_t^2 = Q_t + C_t + eps_t^2,

    with ``Q_t`` the interest-rate quadratic form, ``C_t`` the currency-risk
    quadratic form and ``eps_t^2`` the incompleteness state.  Setting
    ``eps_t^2 = 0`` gives the feasible minimum

        v_min^2 = Q_t + C_t.

    An earlier version of this audit used ``sqrt(Q_t)`` instead.  That is only
    a necessary lower bound, attained solely when ``C_t = 0`` as well; at the
    reported estimates ``C_t = 0.003 > 0``, so states at ``sqrt(Q_t)`` are not
    reachable by the calibrated model.
    """
    quadratic = interest_rate_quadratic(parameters, rate, rate_star)
    return math.sqrt(max(quadratic + parameters.currency_quadratic, 0.0))


def variance_identity_residual(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
    volatility: float,
) -> float:
    """Return the implied ``eps_t^2 = v_t^2 - Q_t - C_t``.

    A negative value means the state violates the variance identity and is
    outside the model, whatever else may be true of it.
    """
    quadratic = interest_rate_quadratic(parameters, rate, rate_star)
    return volatility**2 - quadratic - parameters.currency_quadratic


def induced_xy_correlation(
    parameters: SystemParameters,
    rate: float,
    rate_star: float,
) -> float:
    """Return the correlation of ``X`` with ``Y`` forced when ``C_t = eps_t^2 = 0``.

    In that degenerate configuration equation (28) reduces to
    ``v dX = phi_t dW - phi*_t dW*``, so ``X`` is a deterministic combination
    of ``W`` and ``W*`` and its correlation with ``Y`` is no longer free but
    equal to ``(phi_t rho_wy - phi*_t rho_w*y) / v_t``.

    This is a conditional algebraic statement.  It is **not** reached by the
    calibrated model: at the reported estimates ``C_t = 0.003 > 0``, so the
    configuration requires a parameter vector the application does not report.
    The function therefore takes ``sqrt(Q_t)`` as its reference volatility,
    which is the degenerate value rather than the feasible minimum.
    """
    floor = math.sqrt(max(interest_rate_quadratic(parameters, rate, rate_star), 0.0))
    if floor <= 0.0:
        raise ValueError("the interest-rate quadratic form is zero, so X is not determined")
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
    """Return reference states at which to evaluate the matrix.

    A nonpositive volatility is a request to use the feasible minimum implied
    by the complete variance identity at those rates.
    """
    theta, theta_star = parameters.theta, parameters.theta_star
    volatility = parameters.mean_volatility
    return [
        ("long-run means, mean volatility", theta, theta_star, volatility),
        ("long-run means, v at feasible minimum", theta, theta_star, -1.0),
        ("rates doubled, v at feasible minimum", 2.0 * theta, 2.0 * theta_star, -1.0),
        ("rates tripled, v at feasible minimum", 3.0 * theta, 3.0 * theta_star, -1.0),
        ("rates x10, v at feasible minimum", 10.0 * theta, 10.0 * theta_star, -1.0),
        ("rates x100, v at feasible minimum", 100.0 * theta, 100.0 * theta_star, -1.0),
        ("rates tripled, v at sqrt(Q) [INFEASIBLE]", 3.0 * theta, 3.0 * theta_star, -2.0),
    ]


def run_state_audit() -> pd.DataFrame:
    """Evaluate the matrix across reference states for both systems.

    Every row reports the complete decomposition v^2 = Q + C + eps^2, so a
    state can be judged feasible or not on the identity itself rather than on
    the necessary-but-insufficient bound v^2 >= Q.
    """
    rows = []
    for parameters in (US_UK, US_DE):
        for label, rate, rate_star, volatility in _state_grid(parameters):
            quadratic = interest_rate_quadratic(parameters, rate, rate_star)
            feasible_min = minimum_feasible_volatility(parameters, rate, rate_star)
            if volatility == -1.0:
                volatility = feasible_min
            elif volatility == -2.0:
                # The degenerate value sqrt(Q), which requires C = 0 and is
                # therefore not reachable at the reported estimates.
                volatility = math.sqrt(max(quadratic, 0.0))
            residual = variance_identity_residual(parameters, rate, rate_star, volatility)
            matrix = build_matrix(parameters, rate, rate_star, volatility)
            diagnostics = audit(matrix)
            rows.append(
                {
                    "system": parameters.name,
                    "state": label,
                    "Q": quadratic,
                    "C": parameters.currency_quadratic,
                    "epsilon_squared": residual,
                    "volatility": volatility,
                    "feasible_min_volatility": feasible_min,
                    "feasible": bool(residual >= -1e-12),
                    **diagnostics,
                }
            )
    return pd.DataFrame(rows)


def search_for_infeasible_psd_violation(
    max_rate_multiple: float = 100.0,
    grid: int = 201,
) -> pd.DataFrame:
    """Search the feasible state space for a negative eigenvalue.

    Sweeps both interest rates over multiples of their long-run means and the
    incompleteness state over a range, always taking v from the complete
    variance identity, and reports the worst minimum eigenvalue found.  A
    positive result means no model-feasible counterexample exists in the range
    searched; it is not a proof that none exists anywhere.
    """
    rows = []
    multiples = np.linspace(0.0, max_rate_multiple, grid)
    for parameters in (US_UK, US_DE):
        worst = math.inf
        worst_state = None
        for domestic in multiples:
            for foreign in multiples:
                rate = domestic * parameters.theta
                rate_star = foreign * parameters.theta_star
                base = minimum_feasible_volatility(parameters, rate, rate_star)
                if base <= 0.0:
                    continue
                for epsilon_squared in (0.0, 0.005, 0.02, 0.10):
                    volatility = math.sqrt(base**2 + epsilon_squared)
                    eigenvalue = float(
                        np.linalg.eigvalsh(
                            build_matrix(parameters, rate, rate_star, volatility)
                        ).min()
                    )
                    if eigenvalue < worst:
                        worst = eigenvalue
                        worst_state = (domestic, foreign, epsilon_squared, volatility)
        rows.append(
            {
                "system": parameters.name,
                "max_rate_multiple": max_rate_multiple,
                "worst_min_eigenvalue": worst,
                "rate_multiple": worst_state[0],
                "rate_star_multiple": worst_state[1],
                "epsilon_squared": worst_state[2],
                "volatility": worst_state[3],
                "violation_found": bool(worst < 0.0),
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
                currency_quadratic=parameters.currency_quadratic,
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
    search = search_for_infeasible_psd_violation()

    states.to_csv(args.output_root / "correlation_audit.csv", index=False)
    perturbations.to_csv(args.output_root / "correlation_perturbation.csv", index=False)
    search.to_csv(args.output_root / "correlation_feasible_search.csv", index=False)

    columns = ["system", "state", "Q", "C", "epsilon_squared", "volatility",
               "feasible", "max_abs_off_diagonal", "min_eigenvalue"]
    (args.output_root / "correlation_audit.tex").write_text(
        states[columns].to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="llrrrrcrr",
        ),
        encoding="utf-8",
    )

    pd.set_option("display.width", 200)
    print(states.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print()
    print(perturbations.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print()
    print(search.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ---------------------------------------------------------------------------
# Time-varying risk prices: models B and C of Table 4
# ---------------------------------------------------------------------------

# Table 4 loadings.  Model B has three coefficients per risk price and no
# volatility loading; model C has four, the last being the loading on v_t.
# Table 4 does not re-report the interest-rate risk prices or the free
# correlations, so those are taken from Table 3 and that is an assumption.
TIME_VARYING = {
    ("U.S. vs. U.K.", "B"): ((0.062, 0.117, -0.263), (-0.101, 0.418, 0.135), 0.54),
    ("U.S. vs. Germany", "B"): ((-0.140, 0.066, -0.197), (0.089, -0.003, 0.251), 0.36),
    ("U.S. vs. U.K.", "C"): (
        (-0.026, 0.019, 0.134, 1.514), (0.065, 0.002, -0.329, 2.581), 0.89
    ),
    ("U.S. vs. Germany", "C"): (
        (-0.072, -0.073, 0.006, -0.142), (0.029, 0.028, 0.238, 0.127), 0.94
    ),
}


def volatility_branches(
    parameters: SystemParameters,
    model: str,
    rate: float,
    rate_star: float,
    log_fx: float,
    epsilon_squared: float,
) -> list[float]:
    """Return the positive volatilities consistent with the variance identity.

    Under model B the currency-risk quadratic form ``C_t`` depends only on the
    interest-rate differential and the log exchange rate, so ``v`` follows by
    taking a square root.  Under model C the risk prices load on ``v`` itself,
    and the identity becomes the quadratic of Appendix D,

        (1 - kappa_b) v^2 - 2 eta_t v - (Q_t + zeta^a_t + eps^2) = 0,

    so ``v`` is determined by the remaining state rather than being a free
    unknown.  There is therefore no circularity to obstruct the analysis: the
    fixed point is solvable in closed form.  By Proposition D.1 the number of
    positive roots is one when ``kappa_b < 1`` and zero or two when
    ``kappa_b > 1``.
    """
    if model not in {"B", "C"}:
        raise ValueError("model must be 'B' or 'C'")
    if epsilon_squared < 0.0:
        raise ValueError("epsilon_squared must be nonnegative")
    coefficients, coefficients_star, rho = TIME_VARYING[(parameters.name, model)]
    quadratic = interest_rate_quadratic(parameters, rate, rate_star)
    differential = rate - rate_star

    intercept = coefficients[0] + coefficients[1] * differential + coefficients[2] * log_fx
    intercept_star = (
        coefficients_star[0]
        + coefficients_star[1] * differential
        + coefficients_star[2] * log_fx
    )

    if model == "B":
        currency = (
            intercept**2 + intercept_star**2 - 2.0 * rho * intercept * intercept_star
        )
        total = quadratic + currency + epsilon_squared
        return [math.sqrt(total)] if total > 0.0 else []

    loading, loading_star = coefficients[3], coefficients_star[3]
    kappa_b = loading**2 + loading_star**2 - 2.0 * rho * loading * loading_star
    eta = (
        intercept * loading
        + intercept_star * loading_star
        - rho * (intercept * loading_star + intercept_star * loading)
    )
    zeta_a = (
        intercept**2 + intercept_star**2 - 2.0 * rho * intercept * intercept_star
    )
    a = 1.0 - kappa_b
    b = -2.0 * eta
    c = -(quadratic + zeta_a + epsilon_squared)
    if abs(a) < 1e-15:
        return [-c / b] if b != 0.0 and -c / b > 0.0 else []
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return []
    root = math.sqrt(discriminant)
    return sorted(v for v in ((-b + root) / (2.0 * a), (-b - root) / (2.0 * a)) if v > 1e-12)


def run_time_varying_audit(
    rate_multiples: int = 26,
    fx_points: int = 21,
    max_rate_multiple: float = 5.0,
    fx_range: float = 2.0,
) -> pd.DataFrame:
    """Audit models B and C over a box of states, without the observed series.

    The log exchange rate is swept rather than read from data.  The result is an
    algebraic-domain diagnostic evaluated at a finite collection of candidate
    points: it records whether the inverse variance identity admits no positive
    volatility, one, or two, and it says nothing about whether the diffusion
    visits those points.  For each candidate the volatility is obtained from
    ``volatility_branches``, so every evaluated matrix satisfies the complete
    variance identity by construction.
    """
    rates = np.linspace(0.05, max_rate_multiple, rate_multiples)
    fx_grid = np.linspace(-fx_range, fx_range, fx_points)
    epsilons = (0.0, 0.002, 0.01, 0.05)
    rows = []
    for parameters in (US_UK, US_DE):
        for model in ("B", "C"):
            worst = math.inf
            worst_state = None
            states = evaluated = no_branch = two_branches = 0
            for domestic in rates:
                for foreign in rates:
                    rate = domestic * parameters.theta
                    rate_star = foreign * parameters.theta_star
                    for log_fx in fx_grid:
                        for epsilon_squared in epsilons:
                            states += 1
                            branches = volatility_branches(
                                parameters, model, rate, rate_star, log_fx, epsilon_squared
                            )
                            if not branches:
                                no_branch += 1
                            elif len(branches) == 2:
                                two_branches += 1
                            for volatility in branches:
                                evaluated += 1
                                eigenvalue = float(
                                    np.linalg.eigvalsh(
                                        build_matrix(parameters, rate, rate_star, volatility)
                                    ).min()
                                )
                                if eigenvalue < worst:
                                    worst = eigenvalue
                                    worst_state = (domestic, foreign, log_fx, epsilon_squared)
            rows.append(
                {
                    "system": parameters.name,
                    "model": model,
                    "states": states,
                    "matrices_evaluated": evaluated,
                    "states_with_no_branch": no_branch,
                    "states_with_two_branches": two_branches,
                    "worst_min_eigenvalue": worst if evaluated else float("nan"),
                    "violation_found": bool(evaluated and worst < 0.0),
                    "rate_multiple": None if worst_state is None else worst_state[0],
                    "rate_star_multiple": None if worst_state is None else worst_state[1],
                    "log_fx": None if worst_state is None else worst_state[2],
                    "epsilon_squared": None if worst_state is None else worst_state[3],
                }
            )
    return pd.DataFrame(rows)


# Tolerances for the algebraic-domain diagnostic, stated once so that the table
# caption and the code cannot drift apart.
POSITIVE_ROOT_TOLERANCE = 1e-12
REPEATED_ROOT_TOLERANCE = 1e-9
NEGATIVE_EIGENVALUE_TOLERANCE = -1e-10

# Each design is (label, rate multiples, fx points, max rate multiple, fx range,
# epsilon^2 levels, logarithmic rate spacing).
GRID_DESIGNS: tuple[tuple[str, int, int, float, float, tuple[float, ...], bool], ...] = (
    ("baseline", 26, 21, 5.0, 2.0, (0.0, 0.002, 0.01, 0.05), False),
    ("denser", 41, 33, 5.0, 2.0, (0.0, 0.002, 0.01, 0.05), False),
    ("wider fx", 26, 21, 5.0, 4.0, (0.0, 0.002, 0.01, 0.05), False),
    ("narrower fx", 26, 21, 5.0, 0.5, (0.0, 0.002, 0.01, 0.05), False),
    ("log rates", 26, 21, 5.0, 2.0, (0.0, 0.002, 0.01, 0.05), True),
    ("more eps", 26, 21, 5.0, 2.0, (0.0, 0.001, 0.005, 0.01, 0.02, 0.05), False),
)


def run_grid_sensitivity(
    parameters: Parameters = US_UK,
    model: str = "C",
    designs: tuple[tuple[str, int, int, float, float, tuple[float, ...], bool], ...] = GRID_DESIGNS,
) -> pd.DataFrame:
    """Repeat the algebraic-domain diagnostic under several candidate grids.

    A single grid could produce an artefact of its own spacing, so the diagnostic
    is repeated under denser, wider, narrower, logarithmically spaced and
    finer-incompleteness designs.  The counts are properties of each grid; only
    the qualitative findings, that no candidate point admits exactly one positive
    root and that no matrix is indefinite, are properties of the specification.
    """
    rows = []
    for label, n_rates, n_fx, max_rate, fx_range, epsilons, logarithmic in designs:
        if logarithmic:
            multiples = np.logspace(math.log10(0.05), math.log10(max_rate), n_rates)
        else:
            multiples = np.linspace(0.05, max_rate, n_rates)
        fx_grid = np.linspace(-fx_range, fx_range, n_fx)
        points = evaluated = no_root = one_root = two_roots = repeated = 0
        worst = math.inf
        for domestic in multiples:
            for foreign in multiples:
                rate = domestic * parameters.theta
                rate_star = foreign * parameters.theta_star
                for log_fx in fx_grid:
                    for epsilon_squared in epsilons:
                        points += 1
                        branches = volatility_branches(
                            parameters, model, rate, rate_star, log_fx, epsilon_squared
                        )
                        positive = [v for v in branches if v > POSITIVE_ROOT_TOLERANCE]
                        if len(positive) == 2 and abs(positive[0] - positive[1]) < (
                            REPEATED_ROOT_TOLERANCE
                        ):
                            repeated += 1
                        if not positive:
                            no_root += 1
                        elif len(positive) == 1:
                            one_root += 1
                        else:
                            two_roots += 1
                        for volatility in positive:
                            evaluated += 1
                            eigenvalue = float(
                                np.linalg.eigvalsh(
                                    build_matrix(parameters, rate, rate_star, volatility)
                                ).min()
                            )
                            worst = min(worst, eigenvalue)
        rows.append(
            {
                "design": label,
                "rate_values": n_rates,
                "fx_values": n_fx,
                "fx_range": fx_range,
                "epsilon_levels": len(epsilons),
                "rate_spacing": "log" if logarithmic else "linear",
                "candidate_points": points,
                "no_positive_root": no_root,
                "one_positive_root": one_root,
                "two_positive_roots": two_roots,
                "repeated_roots": repeated,
                "branch_matrices": evaluated,
                "worst_min_eigenvalue": worst if evaluated else float("nan"),
                "indefinite_found": bool(
                    evaluated and worst < NEGATIVE_EIGENVALUE_TOLERANCE
                ),
            }
        )
    return pd.DataFrame(rows)
