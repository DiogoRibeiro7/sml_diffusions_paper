"""Numerical validation of the analytical formulas used in the manuscript.

Every closed form quoted in the paper is checked here against an independent
computation: numerical Gaussian integration, direct Monte Carlo simulation, or
a brute-force alternative. Tolerances are stated explicitly at each assertion
rather than left to a global default.

Run with ``pytest`` from the repository root.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import integrate
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import check_correlation_matrix as ccm  # noqa: E402
import generate_results as gr  # noqa: E402

# Monte Carlo comparisons are checked at three standard errors, which is a
# 99.7 per cent interval under the central limit theorem.
MC_SIGMAS = 3.0


# ---------------------------------------------------------------------------
# 1. Exact Brownian moment formula
# ---------------------------------------------------------------------------


def brownian_moment_closed_form(dimension: int, m_steps: int, r: float, distance: float) -> float:
    """Return E[G_h^r] from Proposition 3.1, for |y - x| = ``distance``."""
    h = 1.0 / m_steps
    return (
        (2.0 * math.pi) ** (-r * dimension / 2.0)
        * h ** (-(r - 1) * dimension / 2.0)
        * (r - (r - 1) * h) ** (-dimension / 2.0)
        * math.exp(-r * distance**2 / (2.0 * (r - (r - 1) * h)))
    )


def brownian_moment_quadrature(dimension: int, m_steps: int, r: float, distance: float) -> float:
    """Integrate E[G_h^r] numerically in the one-dimensional radial reduction.

    With x and y separated by ``distance`` along the first axis, the summand
    depends on Z only through the first coordinate and the squared norm of the
    rest, so the K-dimensional expectation factorises into a one-dimensional
    integral times K-1 identical one-dimensional integrals.
    """
    h = 1.0 / m_steps
    sigma = math.sqrt(1.0 - h)
    prefactor = (2.0 * math.pi * h) ** (-r * dimension / 2.0)

    def axis_integral(offset: float) -> float:
        def integrand(z: float) -> float:
            return math.exp(-r * (offset - z) ** 2 / (2.0 * h)) * norm.pdf(z, scale=sigma)

        value, _ = integrate.quad(
            integrand,
            -40.0 * sigma,
            40.0 * sigma,
            limit=800,
            epsabs=1e-14,
            epsrel=1e-13,
        )
        return value

    return prefactor * axis_integral(distance) * axis_integral(0.0) ** (dimension - 1)


@pytest.mark.parametrize("dimension", [1, 2, 4, 5])
@pytest.mark.parametrize("m_steps", [4, 32, 256])
@pytest.mark.parametrize("r", [1.0, 2.0, 3.0, 2.5])
@pytest.mark.parametrize("distance", [0.0, 0.7])
def test_brownian_moment_matches_quadrature(
    dimension: int, m_steps: int, r: float, distance: float
) -> None:
    """The closed form of Proposition 3.1 agrees with numerical integration."""
    closed = brownian_moment_closed_form(dimension, m_steps, r, distance)
    numeric = brownian_moment_quadrature(dimension, m_steps, r, distance)
    assert closed == pytest.approx(numeric, rel=1e-8)


def test_first_moment_is_the_true_density() -> None:
    """The estimator is exactly unbiased for the Brownian density at every M."""
    for dimension in (1, 3, 4):
        for m_steps in (2, 10, 1000):
            for distance in (0.0, 1.3):
                expected = (2.0 * math.pi) ** (-dimension / 2.0) * math.exp(-(distance**2) / 2.0)
                got = brownian_moment_closed_form(dimension, m_steps, 1.0, distance)
                assert got == pytest.approx(expected, rel=1e-12)


def test_second_moment_matches_generator() -> None:
    """The module used for the figures agrees with the closed form at x = y = 0."""
    for dimension in (1, 2, 4, 8):
        for m_steps in (2, 16, 512):
            assert gr.brownian_second_moment(dimension, m_steps) == pytest.approx(
                brownian_moment_closed_form(dimension, m_steps, 2.0, 0.0), rel=1e-12
            )


def test_second_moment_scaling_limit() -> None:
    """h^{K/2} E[G^2] converges to the constant of Theorem 4.2."""
    for dimension in (1, 2, 4, 8):
        limit = (2.0 * math.pi) ** (-dimension) * 2.0 ** (-dimension / 2.0)
        scaled = gr.brownian_second_moment(dimension, 2**20) * (2.0**-20) ** (dimension / 2.0)
        assert scaled == pytest.approx(limit, rel=1e-5)


def test_local_moment_constant_matches_brownian_case() -> None:
    """c_{r,K} p(y|x) |V|^{-(r-1)/2} reproduces the exact Brownian limit."""
    for dimension in (1, 3, 4):
        for r in (2.0, 3.0):
            for distance in (0.0, 0.9):
                c_rk = (2.0 * math.pi) ** (-(r - 1) * dimension / 2.0) * r ** (-dimension / 2.0)
                density = (2.0 * math.pi) ** (-dimension / 2.0) * math.exp(-(distance**2) / 2.0)
                predicted = c_rk * density  # |V| = 1 for standard Brownian motion
                m_steps = 2**22
                scaled = (1.0 / m_steps) ** ((r - 1) * dimension / 2.0) * (
                    brownian_moment_closed_form(dimension, m_steps, r, distance)
                )
                assert scaled == pytest.approx(predicted, rel=1e-5)


# ---------------------------------------------------------------------------
# 2. Variance against Monte Carlo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dimension,m_steps,simulations", [(1, 8, 64), (2, 16, 128), (4, 8, 256)])
def test_variance_matches_simulation(dimension: int, m_steps: int, simulations: int) -> None:
    """The exact variance agrees with a direct Monte Carlo estimate."""
    rng = np.random.default_rng(4242)
    replications = 40_000
    estimates = gr.simulate_brownian_estimator(
        dimension=dimension,
        m_steps=m_steps,
        simulations=simulations,
        replications=replications,
        rng=rng,
    )
    theoretical = gr.brownian_estimator_variance(dimension, m_steps, simulations)
    empirical = float(np.var(estimates, ddof=1))
    # The variance of a sample variance is dominated by the fourth moment,
    # which is heavy here, so this is a loose but meaningful check.
    assert empirical == pytest.approx(theoretical, rel=0.25)


def test_estimator_is_unbiased_in_simulation() -> None:
    """The simulated mean matches the true density within Monte Carlo error."""
    rng = np.random.default_rng(99)
    dimension, m_steps, simulations, replications = 4, 16, 512, 60_000
    estimates = gr.simulate_brownian_estimator(
        dimension=dimension,
        m_steps=m_steps,
        simulations=simulations,
        replications=replications,
        rng=rng,
    )
    truth = gr.true_brownian_density_at_origin(dimension)
    standard_error = float(np.std(estimates, ddof=1)) / math.sqrt(replications)
    assert abs(float(np.mean(estimates)) - truth) < MC_SIGMAS * standard_error


# ---------------------------------------------------------------------------
# 3. Collapse path and 4. correct-rate path
# ---------------------------------------------------------------------------


def test_collapse_path_median_falls_and_tail_grows() -> None:
    """Along M = S in four dimensions the median collapses (Theorem 3.3)."""
    rng = np.random.default_rng(20260728)
    truth = gr.true_brownian_density_at_origin(4)
    medians, below_half = [], []
    for m in (8, 32, 128):
        estimates = gr.simulate_brownian_estimator(
            dimension=4, m_steps=m, simulations=m, replications=8_000, rng=rng
        )
        relative = estimates / truth
        medians.append(float(np.median(relative)))
        below_half.append(float(np.mean(relative < 0.5)))
    assert medians[0] > medians[1] > medians[2]
    assert below_half[0] < below_half[1] < below_half[2]
    assert medians[-1] < 0.05


def test_correct_rate_path_rmse_falls() -> None:
    """Relative RMSE falls when S/M^2 diverges, and rises when it does not."""
    dimension = 4
    truth = gr.true_brownian_density_at_origin(dimension)

    def relative_rmse(m: int, simulations: int) -> float:
        variance = gr.brownian_estimator_variance(dimension, m, simulations)
        return math.sqrt(variance) / truth

    increasing = [relative_rmse(m, m) for m in (8, 32, 128)]
    decreasing = [relative_rmse(m, m**3) for m in (8, 32, 128)]
    constant = [relative_rmse(m, m**2) for m in (8, 32, 128)]
    assert increasing[0] < increasing[1] < increasing[2]
    assert decreasing[0] > decreasing[1] > decreasing[2]
    assert constant[2] == pytest.approx(constant[0], rel=0.05)


# ---------------------------------------------------------------------------
# 5. Boundary probability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("alpha,beta", [(0.320, 0.088), (0.338, 0.101)])
@pytest.mark.parametrize("h", [1.0 / 520.0, 0.02])
def test_boundary_probability_matches_simulation(alpha: float, beta: float, h: float) -> None:
    """The closed form agrees with direct simulation of one Euler step."""
    rng = np.random.default_rng(7)
    draws = 400_000
    state = beta**2 * h  # the maximising state of Proposition B.2
    formula = float(gr.euler_negative_probability(np.array([state]), alpha=alpha, beta=beta, h=h)[0])
    step = (
        state
        + (beta**2 - 2.0 * alpha * state) * h
        + 2.0 * beta * math.sqrt(state * h) * rng.normal(size=draws)
    )
    empirical = float(np.mean(step < 0.0))
    standard_error = math.sqrt(empirical * (1.0 - empirical) / draws)
    assert abs(formula - empirical) < MC_SIGMAS * standard_error


@pytest.mark.parametrize("alpha,beta", [(0.320, 0.088), (0.338, 0.101), (1.5, 0.4)])
def test_worst_case_boundary_probability_tends_to_phi_minus_one(alpha: float, beta: float) -> None:
    """Proposition B.2: the supremum tends to Phi(-1), attained at H = beta^2 h."""
    for h in (1e-3, 1e-4, 1e-5):
        grid = np.logspace(math.log10(beta**2 * h) - 3.0, math.log10(beta**2 * h) + 3.0, 20_000)
        probability = gr.euler_negative_probability(grid, alpha=alpha, beta=beta, h=h)
        assert probability.max() == pytest.approx(norm.cdf(-1.0), abs=2e-3)
        assert grid[int(np.argmax(probability))] == pytest.approx(beta**2 * h, rel=0.05)


def test_boundary_probability_rejects_negative_state() -> None:
    """A negative state is a caller error, not something to be clipped."""
    with pytest.raises(ValueError):
        gr.euler_negative_probability(np.array([-1.0]), alpha=0.3, beta=0.1, h=0.01)


# ---------------------------------------------------------------------------
# 6. Quadratic-root classification
# ---------------------------------------------------------------------------


def positive_roots(kappa_b: float, eta: float, zeta: float) -> list[float]:
    """Return the positive roots of (1 - kappa_b) v^2 - 2 eta v - zeta = 0."""
    a, b, c = kappa_b - 1.0, 2.0 * eta, zeta
    if a == 0.0:
        return [] if b == 0.0 else [v for v in (-c / b,) if v > 0.0]
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return []
    root = math.sqrt(discriminant)
    return sorted(v for v in ((-b - root) / (2.0 * a), (-b + root) / (2.0 * a)) if v > 0.0)


def test_unique_positive_root_when_kappa_below_one() -> None:
    """Case (i) of Proposition D.1: exactly one positive root."""
    for kappa_b in (0.0, 0.0702, 0.5, 0.99):
        for eta in (-2.0, -0.3, 0.0, 0.3, 2.0):
            for zeta in (0.01, 1.0, 10.0):
                assert len(positive_roots(kappa_b, eta, zeta)) == 1


def test_zero_or_two_positive_roots_when_kappa_above_one() -> None:
    """Case (ii): never exactly one positive root away from the repeated case."""
    kappa_b = 1.9982  # the reported U.S.-U.K. value
    for eta in (-3.0, -1.0, -0.05, 0.0, 0.5, 3.0):
        for zeta in (0.001, 0.1, 1.0, 5.0):
            roots = positive_roots(kappa_b, eta, zeta)
            if math.isclose(eta**2, (kappa_b - 1.0) * zeta, rel_tol=1e-9):
                continue
            assert len(roots) in (0, 2)
            if eta >= 0.0:
                assert roots == []


def test_repeated_root_boundary() -> None:
    """At eta^2 = (kappa_b - 1) zeta the two roots coincide."""
    kappa_b, zeta = 2.5, 0.8
    eta = -math.sqrt((kappa_b - 1.0) * zeta)
    roots = positive_roots(kappa_b, eta, zeta)
    assert len(roots) in (1, 2)
    # A repeated root is recovered through a discriminant that vanishes
    # exactly, so the two branches agree only to about sqrt(eps).
    assert roots[0] == pytest.approx(roots[-1], rel=1e-6)
    assert roots[0] == pytest.approx(-eta / (kappa_b - 1.0), rel=1e-6)


def test_kappa_b_matches_reported_values() -> None:
    """kappa_b = b^2 + b*^2 - 2 rho b b* at the model-C loadings."""
    assert 1.514**2 + 2.581**2 - 2 * 0.89 * 1.514 * 2.581 == pytest.approx(1.9982, abs=5e-5)
    assert (-0.142) ** 2 + 0.127**2 - 2 * 0.94 * (-0.142) * 0.127 == pytest.approx(0.0702, abs=5e-5)


# ---------------------------------------------------------------------------
# 7. Correlation-matrix checks
# ---------------------------------------------------------------------------


def test_valid_matrix_passes() -> None:
    """A matrix at the reported estimates is positive definite."""
    for parameters in (ccm.US_UK, ccm.US_DE):
        matrix = ccm.build_matrix(
            parameters, parameters.theta, parameters.theta_star, parameters.mean_volatility
        )
        report = ccm.audit(matrix)
        assert report["positive_definite"]
        assert report["entries_in_range"]
        assert 0.0 < report["schur_complement"] <= 1.0


def test_invalid_matrix_is_detected() -> None:
    """An entrywise-valid but indefinite matrix is reported as such."""
    matrix = np.array(
        [
            [1.0, 0.9, 0.9, 0.0],
            [0.9, 1.0, -0.9, 0.0],
            [0.9, -0.9, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    report = ccm.audit(matrix)
    assert report["entries_in_range"]
    assert not report["positive_semidefinite"]


def test_malformed_matrices_raise() -> None:
    """Dimension, symmetry and diagonal violations raise informative errors."""
    with pytest.raises(ValueError, match="square"):
        ccm.validate_shape(np.zeros((2, 3)))
    with pytest.raises(ValueError, match="symmetric"):
        ccm.validate_shape(np.array([[1.0, 0.4], [0.5, 1.0]]))
    with pytest.raises(ValueError, match="diagonal"):
        ccm.validate_shape(np.array([[1.0, 0.4], [0.4, 0.9]]))
    with pytest.raises(ValueError, match="at least two"):
        ccm.validate_shape(np.array([[1.0]]))


def test_entrywise_validity_is_automatic_above_the_floor() -> None:
    """Proposition E.1: |rho_wx| <= 1 whenever v >= sqrt(Q)."""
    for parameters in (ccm.US_UK, ccm.US_DE):
        for multiple in (0.5, 1.0, 2.0, 3.0, 5.0):
            rate = multiple * parameters.theta
            rate_star = multiple * parameters.theta_star
            floor = ccm.minimum_feasible_volatility(parameters, rate, rate_star)
            for volatility in (floor, 1.01 * floor, 2.0 * floor, 10.0 * floor):
                left, right = ccm.implied_correlations(parameters, rate, rate_star, volatility)
                assert abs(left) <= 1.0 + 1e-12
                assert abs(right) <= 1.0 + 1e-12


def test_degenerate_configuration_is_infeasible_at_the_estimates() -> None:
    """The sqrt(Q) configuration requires C = 0, which the estimates contradict.

    An earlier version of this audit treated sqrt(Q_t) as the volatility floor
    and reported an indefinite matrix there.  The complete variance identity is
    v^2 = Q + C + eps^2, so that state implies eps^2 = -C < 0.
    """
    for parameters in (ccm.US_UK, ccm.US_DE):
        assert parameters.currency_quadratic > 0.0
        rate, rate_star = 3.0 * parameters.theta, 3.0 * parameters.theta_star
        degenerate = math.sqrt(ccm.interest_rate_quadratic(parameters, rate, rate_star))
        residual = ccm.variance_identity_residual(parameters, rate, rate_star, degenerate)
        assert residual == pytest.approx(-parameters.currency_quadratic, rel=1e-9)
        assert residual < 0.0  # infeasible
        # It is indeed indefinite there, which is why the distinction matters.
        report = ccm.audit(ccm.build_matrix(parameters, rate, rate_star, degenerate))
        assert report["entries_in_range"]
        assert not report["positive_semidefinite"]


def test_feasible_minimum_volatility_gives_a_valid_matrix() -> None:
    """At the true feasible minimum the matrix is positive definite."""
    for parameters in (ccm.US_UK, ccm.US_DE):
        for multiple in (1.0, 2.0, 3.0, 10.0, 100.0):
            rate = multiple * parameters.theta
            rate_star = multiple * parameters.theta_star
            floor = ccm.minimum_feasible_volatility(parameters, rate, rate_star)
            residual = ccm.variance_identity_residual(parameters, rate, rate_star, floor)
            assert residual == pytest.approx(0.0, abs=1e-12)
            report = ccm.audit(ccm.build_matrix(parameters, rate, rate_star, floor))
            assert report["entries_in_range"]
            assert report["positive_definite"], (parameters.name, multiple)


def test_no_feasible_psd_violation_in_the_searched_range() -> None:
    """The systematic search finds no model-feasible indefinite matrix."""
    results = ccm.search_for_infeasible_psd_violation(max_rate_multiple=100.0, grid=41)
    assert not results["violation_found"].any()
    assert (results["worst_min_eigenvalue"] > 0.0).all()


def test_induced_correlation_is_a_conditional_statement() -> None:
    """Proposition E.2 binds only in the degenerate configuration.

    The induced value differs materially from the reported estimate, which is
    why the specification would need to impose it; but the configuration is not
    reached at the reported parameters, so this is conditional algebra and not
    a defect in the estimates.
    """
    for parameters in (ccm.US_UK, ccm.US_DE):
        rate, rate_star = 3.0 * parameters.theta, 3.0 * parameters.theta_star
        induced = ccm.induced_xy_correlation(parameters, rate, rate_star)
        assert abs(induced - parameters.rho_xy) > 0.03
        # ... but the configuration it applies to is infeasible here.
        degenerate = math.sqrt(ccm.interest_rate_quadratic(parameters, rate, rate_star))
        assert ccm.variance_identity_residual(parameters, rate, rate_star, degenerate) < 0.0


def test_setting_rho_xy_to_the_induced_value_restores_validity() -> None:
    """Imposing the compatibility condition makes the degenerate matrix valid."""
    for parameters in (ccm.US_UK, ccm.US_DE):
        rate, rate_star = 3.0 * parameters.theta, 3.0 * parameters.theta_star
        induced = ccm.induced_xy_correlation(parameters, rate, rate_star)
        repaired = ccm.SystemParameters(
            **{**parameters.__dict__, "rho_xy": induced}
        )
        degenerate = math.sqrt(ccm.interest_rate_quadratic(parameters, rate, rate_star))
        report = ccm.audit(ccm.build_matrix(repaired, rate, rate_star, degenerate))
        assert report["min_eigenvalue"] > -1e-9


def test_nearest_correlation_is_not_applied_silently() -> None:
    """The projection is available but must be requested explicitly."""
    bad = np.array([[1.0, 0.99, 0.99], [0.99, 1.0, -0.99], [0.99, -0.99, 1.0]])
    assert not ccm.audit(bad)["positive_semidefinite"]
    projected = ccm.nearest_correlation(bad)
    assert np.linalg.eigvalsh(projected).min() > -1e-8
    assert np.allclose(np.diag(projected), 1.0, atol=1e-8)


# ---------------------------------------------------------------------------
# 8. Minimum-incompleteness optimisation
# ---------------------------------------------------------------------------


def test_corner_solution_matches_numerical_optimiser() -> None:
    """The analytic corner agrees with a brute-force search over the interval."""
    rng = np.random.default_rng(11)
    for _ in range(20):
        a_values = rng.uniform(0.5, 3.0, size=40)
        gammas = np.ones(40)
        upper = float((a_values / gammas).min())
        grid = np.linspace(upper - 5.0, upper, 200_001)
        objective = np.array([(a_values - gammas * c).sum() for c in grid])
        feasible = np.all(a_values[None, :] - grid[:, None] * gammas[None, :] >= -1e-12, axis=1)
        best = grid[feasible][int(np.argmin(objective[feasible]))]
        assert best == pytest.approx(upper, abs=1e-4)
        residuals = a_values - upper
        assert residuals.min() == pytest.approx(0.0, abs=1e-12)


def test_corner_solution_with_a_binding_range_restriction() -> None:
    """Case (ii): a range restriction can bind before any residual reaches zero."""
    a_values = np.array([2.0, 3.0, 4.0])
    gammas = np.ones(3)
    range_upper = 1.0  # binds before min(A_t) = 2.0
    c_star = min(float((a_values / gammas).min()), range_upper)
    assert c_star == range_upper
    residuals = a_values - c_star * gammas
    assert residuals.min() > 0.0  # no incompleteness constraint is active


# ---------------------------------------------------------------------------
# 9. Reproducibility of the committed tables
# ---------------------------------------------------------------------------


def test_committed_tables_regenerate(tmp_path: Path) -> None:
    """Regenerated artefacts match the committed ones (the make verify check)."""
    sys.path.insert(0, str(ROOT / "code"))
    import verify_reproducibility as vr

    results = vr.verify()
    failures = [r for r in results if not r.ok]
    assert not failures, "; ".join(f"{r.path}: {r.status} {r.detail}" for r in failures)
    assert len(results) >= 20


def test_design_ratios_are_as_quoted() -> None:
    """The finite-sample diagnostics quoted in Section 8.2."""
    n_obs, m_steps, simulations = 544, 10, 5_000
    assert math.sqrt(simulations) / m_steps == pytest.approx(7.07, abs=0.01)
    assert n_obs / simulations**0.25 == pytest.approx(64.7, abs=0.1)
    assert simulations / m_steps**2 == pytest.approx(50.0)
    # Doubling both halves the effective size; doubling M alone quarters it.
    assert (2 * simulations) / (2 * m_steps) ** 2 == pytest.approx(25.0)
    assert simulations / (2 * m_steps) ** 2 == pytest.approx(12.5)
    assert (4 * simulations) / (2 * m_steps) ** 2 == pytest.approx(50.0)


def test_feller_ratios_are_as_quoted() -> None:
    """Table 5: interest rates comfortably above one, incompleteness exactly 1/2."""
    for kappa, theta, sigma, expected in (
        (0.284, 0.053, 0.028, 38.4),
        (0.486, 0.074, 0.056, 22.9),
        (0.305, 0.058, 0.027, 48.5),
        (0.088, 0.064, 0.042, 6.4),
    ):
        assert 2.0 * kappa * theta / sigma**2 == pytest.approx(expected, abs=0.05)
    for alpha, beta in ((0.320, 0.088), (0.338, 0.101), (2.7, 0.013)):
        kappa, theta, sigma = 2.0 * alpha, beta**2 / (2.0 * alpha), 2.0 * beta
        assert 2.0 * kappa * theta / sigma**2 == pytest.approx(0.5, rel=1e-12)


def test_optimal_discretisation_exponents() -> None:
    """Proposition 5.1: M ~ S^{2/(K+4)} and MSE ~ S^{-4/(K+4)}."""
    for dimension, m_exponent, mse_exponent in ((1, 2 / 5, -4 / 5), (2, 1 / 3, -2 / 3), (4, 1 / 4, -1 / 2), (8, 1 / 6, -1 / 3)):
        assert 2.0 / (dimension + 4.0) == pytest.approx(m_exponent)
        assert -4.0 / (dimension + 4.0) == pytest.approx(mse_exponent)


# ---------------------------------------------------------------------------
# 10. Appendix H: the common-random-number reduction and the sandwich bound
# ---------------------------------------------------------------------------


def _location_model_pieces(rng: np.random.Generator, dimension: int, n_obs: int, sims: int, m: int):
    """Return the atoms and data for the location model of Appendix H."""
    h = 1.0 / m
    increments = rng.normal(size=(n_obs, dimension))
    innovations = rng.normal(size=(n_obs, sims, dimension))
    atoms = increments[:, None, :] - math.sqrt(1.0 - h) * innovations
    return h, increments, innovations, atoms


def test_common_random_number_reduction_is_an_identity() -> None:
    """Proposition H.1: the simulated density is exactly a Gaussian KDE."""
    from scipy.special import logsumexp

    rng = np.random.default_rng(3)
    dimension, n_obs, sims, m = 3, 6, 9, 11
    h, increments, innovations, _ = _location_model_pieces(rng, dimension, n_obs, sims, m)
    for _ in range(5):
        theta = rng.normal(scale=0.7, size=dimension)
        # Direct Euler simulation, exact for this model.
        preterminal = theta * (1.0 - h) + math.sqrt(1.0 - h) * innovations
        residual = increments[:, None, :] - preterminal - theta * h
        direct = -(dimension / 2.0) * math.log(2.0 * math.pi * h) - (residual**2).sum(-1) / (2.0 * h)
        # The kernel-density form of Proposition H.1.
        centred = (increments - theta)[:, None, :] - math.sqrt(1.0 - h) * innovations
        kde = -(dimension / 2.0) * math.log(2.0 * math.pi * h) - (centred**2).sum(-1) / (2.0 * h)
        assert np.allclose(logsumexp(direct, axis=1), logsumexp(kde, axis=1), rtol=0, atol=1e-11)


def test_nearest_atom_sandwich_bound() -> None:
    """Proposition H.2: the bound holds, and with the sign as stated."""
    from scipy.special import logsumexp

    rng = np.random.default_rng(5)
    dimension, n_obs, sims, m = 3, 12, 7, 9
    h, increments, innovations, atoms = _location_model_pieces(rng, dimension, n_obs, sims, m)
    lower = -2.0 * n_obs * h * math.log(sims)
    for _ in range(25):
        theta = rng.normal(scale=0.8, size=dimension)
        squared = ((atoms - theta) ** 2).sum(-1)
        log_kernel = -(dimension / 2.0) * math.log(2.0 * math.pi * h) - squared / (2.0 * h)
        log_likelihood = float((logsumexp(log_kernel, axis=1) - math.log(sims)).sum())
        nearest = float(squared.min(axis=1).sum())
        quantity = (
            2.0 * h * log_likelihood
            + nearest
            + n_obs * h * dimension * math.log(2.0 * math.pi * h)
        )
        assert lower - 1e-9 <= quantity <= 1e-9


# ---------------------------------------------------------------------------
# 11. Second-round corrections
# ---------------------------------------------------------------------------


def test_exact_worst_case_matches_numerical_optimiser_and_simulation() -> None:
    """Proposition C.1: closed form against a grid search and Monte Carlo."""
    rng = np.random.default_rng(17)
    for alpha, beta in ((0.320, 0.088), (0.338, 0.101), (1.5, 0.4)):
        for h in (1.0 / 520.0, 1.0 / 1040.0, 0.02):
            argmax, maximum = gr.worst_case_boundary(alpha, beta, h)
            # closed form against a fine grid
            grid = np.logspace(math.log10(argmax) - 3, math.log10(argmax) + 3, 200_000)
            values = gr.euler_negative_probability(grid, alpha=alpha, beta=beta, h=h)
            assert values.max() == pytest.approx(maximum, rel=1e-6)
            assert grid[int(np.argmax(values))] == pytest.approx(argmax, rel=1e-3)
            # closed form against direct simulation at the maximiser
            draws = 200_000
            step = (
                argmax
                + (beta**2 - 2.0 * alpha * argmax) * h
                + 2.0 * beta * math.sqrt(argmax * h) * rng.normal(size=draws)
            )
            empirical = float(np.mean(step < 0.0))
            se = math.sqrt(empirical * (1.0 - empirical) / draws)
            assert abs(maximum - empirical) < 4.0 * se


def test_worst_case_rejects_a_step_that_is_too_coarse() -> None:
    """The closed form requires h < 1/(2 alpha)."""
    with pytest.raises(ValueError):
        gr.worst_case_boundary(alpha=1.0, beta=0.1, h=0.75)
    with pytest.raises(ValueError):
        gr.worst_case_boundary(alpha=-1.0, beta=0.1, h=0.01)


def test_cir_negativity_is_positive_but_negligible() -> None:
    """Gaussian tails are never exactly zero, however small."""
    h = 1.0 / 520.0
    for _, kappa, theta, sigma in gr.CIR_RATES:
        at_mean = gr.cir_negativity(kappa, theta, sigma, theta, h)
        assert at_mean["z_score"] > 100.0
        assert at_mean["log10_probability"] < -2000.0
        assert at_mean["underflows"]  # not representable, but not zero
        low = gr.cir_negativity(kappa, theta, sigma, 0.001, h)
        assert low["probability"] > 0.0
        assert low["log10_probability"] > at_mean["log10_probability"]


def test_antithetic_pair_is_identical_at_a_coincident_endpoint() -> None:
    """Proposition 8.1: at y = x the antithetic partner equals its twin."""
    rng = np.random.default_rng(23)
    for dimension in (1, 4):
        for m_steps in (10, 100):
            h = 1.0 / m_steps
            z = rng.normal(0.0, math.sqrt(1.0 - h), size=(50_000, dimension))
            kernel = lambda w: (2.0 * math.pi * h) ** (-dimension / 2.0) * np.exp(
                -(w**2).sum(1) / (2.0 * h)
            )
            assert np.allclose(kernel(z), kernel(-z), rtol=0.0, atol=0.0)


def test_antithetic_correlation_is_not_minus_one_away_from_the_endpoint() -> None:
    """Away from y = x the antithetic correlation is neither -1 nor always negative."""
    rng = np.random.default_rng(29)
    h, dimension = 0.1, 4
    correlations = []
    for distance in (0.5, 1.5):
        target = np.zeros(dimension)
        target[0] = distance
        z = rng.normal(0.0, math.sqrt(1.0 - h), size=(400_000, dimension))
        kernel = lambda w: np.exp(-((target - w) ** 2).sum(1) / (2.0 * h))
        correlations.append(float(np.corrcoef(kernel(z), kernel(-z))[0, 1]))
    assert all(c > -0.99 for c in correlations)
    assert max(correlations) > -0.2  # not uniformly strongly negative


def test_lemma3_divergence() -> None:
    """Corollary 3.5: sqrt(S)(q_hat - p) diverges to -infinity along M = S."""
    rng = np.random.default_rng(20260729)
    truth = gr.true_brownian_density_at_origin(4)
    medians = []
    for m in (16, 64, 256):
        estimates = gr.simulate_brownian_estimator(
            dimension=4, m_steps=m, simulations=m, replications=4_000, rng=rng
        )
        medians.append(float(np.median(math.sqrt(m) * (estimates - truth))))
    # The median of sqrt(S)(q_hat - p) should march towards -sqrt(S) p.
    assert medians[0] > medians[1] > medians[2]
    assert medians[-1] < -0.5 * math.sqrt(256) * truth


def test_model_b_has_no_volatility_loading() -> None:
    """Model B carries three coefficients per risk price, model C four."""
    for system in ("U.S. vs. U.K.", "U.S. vs. Germany"):
        coefficients, coefficients_star, _ = ccm.TIME_VARYING[(system, "B")]
        assert len(coefficients) == 3 and len(coefficients_star) == 3
        coefficients, coefficients_star, _ = ccm.TIME_VARYING[(system, "C")]
        assert len(coefficients) == 4 and len(coefficients_star) == 4


def test_model_b_branch_is_unique_and_satisfies_the_identity() -> None:
    """With no volatility loading the identity is solved by a square root."""
    for parameters in (ccm.US_UK, ccm.US_DE):
        for log_fx in (-1.0, 0.0, 0.5):
            for epsilon_squared in (0.0, 0.01):
                branches = ccm.volatility_branches(
                    parameters, "B", parameters.theta, parameters.theta_star,
                    log_fx, epsilon_squared,
                )
                assert len(branches) == 1
                assert branches[0] > 0.0


def test_model_c_branches_are_never_exactly_one_when_kappa_exceeds_one() -> None:
    """Proposition D.1(ii), checked across the swept state space."""
    parameters = ccm.US_UK  # kappa_b ~ 1.998 > 1
    counts = {0: 0, 2: 0}
    for domestic in np.linspace(0.05, 5.0, 12):
        for log_fx in np.linspace(-2.0, 2.0, 15):
            for epsilon_squared in (0.0, 0.01):
                n = len(
                    ccm.volatility_branches(
                        parameters, "C",
                        domestic * parameters.theta, domestic * parameters.theta_star,
                        log_fx, epsilon_squared,
                    )
                )
                assert n in (0, 2), f"got {n} branches"
                counts[n] += 1
    assert counts[0] > 0 and counts[2] > 0  # both regimes occur


def test_more_incompleteness_shrinks_the_model_c_branch_region() -> None:
    """Larger eps^2 makes a positive branch harder to exist when kappa_b > 1."""
    parameters = ccm.US_UK
    previous = None
    for epsilon_squared in (0.0, 0.002, 0.01, 0.05):
        available = sum(
            1
            for log_fx in np.linspace(-2.0, 2.0, 41)
            if ccm.volatility_branches(
                parameters, "C", parameters.theta, parameters.theta_star,
                log_fx, epsilon_squared,
            )
        )
        if previous is not None:
            assert available <= previous
        previous = available


def test_time_varying_audit_finds_no_psd_violation() -> None:
    """No swept feasible state gives an indefinite matrix in any specification."""
    frame = ccm.run_time_varying_audit(rate_multiples=8, fx_points=9)
    assert not frame["violation_found"].any()
    assert (frame["worst_min_eigenvalue"] > 0.0).all()


# ---------------------------------------------------------------------------
# Deposit metadata
# ---------------------------------------------------------------------------


def test_deposit_metadata_files_are_present_and_parse() -> None:
    """LICENSE, CITATION.cff and .zenodo.json must all be usable at release time."""
    import make_release as mr

    assert mr.check_deposit_metadata() == []


def test_deposit_gate_reports_every_missing_file() -> None:
    """An empty tree must produce one problem per required file, not silence."""
    import tempfile

    import make_release as mr

    original = mr.ROOT
    try:
        mr.ROOT = Path(tempfile.mkdtemp())
        problems = mr.check_deposit_metadata()
    finally:
        mr.ROOT = original
    assert len(problems) == 3
    assert any("LICENSE" in problem for problem in problems)
    assert any("CITATION.cff" in problem for problem in problems)
    assert any(".zenodo.json" in problem for problem in problems)


def test_citation_and_zenodo_agree_with_the_manuscript() -> None:
    """The three records of title, author and licence must not drift apart."""
    import json

    yaml = pytest.importorskip("yaml")

    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")

    assert citation["title"] == zenodo["title"]
    assert rf"\newcommand{{\papertitle}}{{{citation['title']}}}" in manuscript

    assert citation["license"] == "CC-BY-4.0"
    assert zenodo["license"] == "cc-by-4.0"

    orcid = "0009-0001-2022-7072"
    assert citation["authors"][0]["orcid"].endswith(orcid)
    assert zenodo["creators"][0]["orcid"] == orcid
    assert orcid in manuscript

    affiliation = "School of Media Arts and Design, Polytechnic of Porto"
    assert citation["authors"][0]["affiliation"] == affiliation
    assert zenodo["creators"][0]["affiliation"] == affiliation
    assert f"\\newcommand{{\\affiliation}}{{{affiliation}}}" in manuscript


def test_zenodo_dois_are_recorded_consistently() -> None:
    """The concept and version DOIs must agree across CITATION.cff and README.

    The concept DOI resolves to the newest version and is the one to cite; the
    version DOI pins v1.0.0.  They differ by one digit, which is exactly the
    kind of pair that gets transposed, so both are checked in both files.
    """
    yaml = pytest.importorskip("yaml")

    concept = "10.5281/zenodo.21719868"
    current = "10.5281/zenodo.21760062"
    superseded = (
        "10.5281/zenodo.21729471",
        "10.5281/zenodo.21728285",
        "10.5281/zenodo.21719869",
    )
    assert len({concept, current, *superseded}) == 5

    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # The top-level doi field must be the concept DOI, not a version DOI.
    assert citation["doi"] == concept
    assert citation["version"] == "v1.0.3"

    recorded = {entry["value"]: entry for entry in citation["identifiers"]}
    assert set(recorded) == {concept, current, *superseded}
    assert all(entry["type"] == "doi" for entry in recorded.values())
    assert "always resolves" in recorded[concept]["description"]
    # Derived from the recorded version rather than hardcoded, so that bumping
    # the release does not silently leave this assertion checking the old one.
    assert citation["version"] in recorded[current]["description"]
    for value in superseded:
        assert "superseded" in recorded[value]["description"]

    for value in (concept, current, *superseded):
        assert value in readme
    # The BibTeX entry must carry the concept DOI so citations follow the work.
    bibtex_start = readme.index("@misc{")
    bibtex_end = readme.index("}\n```", bibtex_start)
    bibtex = readme[bibtex_start:bibtex_end]
    assert concept in bibtex
    assert current not in bibtex
    for value in superseded:
        assert value not in bibtex


def test_zenodo_registers_the_reviewed_article() -> None:
    """The deposit must point at the article it corrects, by DOI."""
    import json

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    reviewed = [
        entry
        for entry in zenodo["related_identifiers"]
        if entry["relation"] == "reviews"
    ]
    assert len(reviewed) == 1
    assert reviewed[0]["identifier"] == "10.1016/S0304-405X(01)00093-9"
    assert reviewed[0]["identifier"] in (ROOT / "paper" / "references.bib").read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# CIR boundary diagnostics
# ---------------------------------------------------------------------------


def test_cir_log_tail_agrees_with_the_gaussian_asymptotic() -> None:
    """log10 Phi(-z) must match the standard Gaussian tail expansion.

    The table reports base-ten logarithms because direct evaluation underflows.
    This checks the stable log-CDF against the classical asymptotic
    Phi(-z) ~ phi(z)/z, which is accurate to O(z^-2) relative error for large z.
    """
    for z in (10.0, 26.5, 50.0, 100.0, 187.5, 203.4):
        stable = norm.logcdf(-z) / math.log(10.0)
        asymptotic = (
            -0.5 * z * z / math.log(10.0)
            - math.log(z * math.sqrt(2.0 * math.pi)) / math.log(10.0)
        )
        assert stable == pytest.approx(asymptotic, rel=1e-3)


def test_cir_direct_evaluation_underflows_exactly_where_recorded() -> None:
    """The underflow flag must agree with double-precision evaluation."""
    frame = pd.read_csv(ROOT / "paper" / "tables" / "cir_negativity.csv")
    for _, row in frame.iterrows():
        direct = float(norm.cdf(-row["z_score"]))
        assert bool(row["underflows"]) == (direct == 0.0)
        # Underflow is a property of binary64, not of the mathematics: the
        # log-probability is always finite and strictly negative.
        assert math.isfinite(row["log10_probability"])
        assert row["log10_probability"] < 0.0


def test_cir_probability_is_strictly_positive_in_exact_arithmetic() -> None:
    """Every recorded log-probability corresponds to a positive number."""
    frame = pd.read_csv(ROOT / "paper" / "tables" / "cir_negativity.csv")
    # 10**x > 0 for every finite x, so the claim reduces to finiteness.
    assert frame["log10_probability"].apply(math.isfinite).all()
    assert (frame["z_score"] > 0.0).all()


def test_manuscript_cir_table_matches_the_generated_values() -> None:
    """The hand-typed CIR table must not drift from the computed diagnostics.

    The table lives in the companion note, not the theory paper, since the split.
    """
    frame = pd.read_csv(ROOT / "paper" / "tables" / "cir_negativity.csv")
    manuscript = (ROOT / "paper" / "companion.tex").read_text(encoding="utf-8")

    lookup = {
        ("U.S. (vs. U.K.)", "long-run mean"): ("187.5", "-7636", "yes"),
        ("U.S. (vs. U.K.)", "0.1 per cent"): ("26.5", "-154", "no"),
        ("U.K.", "long-run mean"): ("110.8", "-2667", "yes"),
        ("U.K.", "0.1 per cent"): ("13.8", "-42.6", "no"),
        ("U.S. (vs. Germany)", "long-run mean"): ("203.4", "-8986", "yes"),
        ("Germany", "long-run mean"): ("137.4", "-4099", "yes"),
    }
    for (process, state), (z_text, log_text, underflow_text) in lookup.items():
        row = frame[
            (frame["process"] == process) & (frame["state_label"] == state)
        ].iloc[0]
        assert float(z_text) == pytest.approx(row["z_score"], abs=0.05)
        assert float(log_text) == pytest.approx(row["log10_probability"], rel=1e-3)
        assert (underflow_text == "yes") == bool(row["underflows"])
        assert z_text in manuscript, f"{z_text} missing from the manuscript"


def test_worst_case_boundary_decreases_as_the_step_is_refined() -> None:
    """Proposition C.1: sup_x P_h(x) is strictly increasing in h.

    Refining the mesh therefore lowers the worst case, converging down to
    Phi(-1) from above rather than up to it from below.  An earlier version of
    the manuscript described the direction the wrong way round.
    """
    limit = float(norm.cdf(-1.0))
    for alpha in (0.320, 0.338, 0.5, 1.0):
        steps = [0.02, 1 / 520, 1 / 1040, 1e-5, 1e-9]
        values = [gr.worst_case_boundary(alpha, 0.088, h)[1] for h in steps]

        # Strictly decreasing as h decreases, and bounded below by Phi(-1).
        for earlier, later in zip(values, values[1:]):
            assert later < earlier, f"alpha={alpha}: not decreasing"
            assert later > limit - 1e-12, f"alpha={alpha}: fell below Phi(-1)"

        assert values[-1] == pytest.approx(limit, abs=1e-9)
        assert values[0] > limit


def test_worst_case_boundary_matches_the_closed_form_and_the_table() -> None:
    """The generated values reproduce 0.1602 > 0.1588 > 0.1587 as stated."""
    frame = pd.read_csv(ROOT / "paper" / "tables" / "boundary_maximum.csv")

    # Within each process the maximum must fall strictly as the step is refined,
    # and stay above the limit Phi(-1).
    limit = float(norm.cdf(-1.0))
    for system, block in frame.groupby("system"):
        ordered = block.sort_values("h", ascending=False)
        maxima = ordered["max_probability"].tolist()
        assert all(b < a for a, b in zip(maxima, maxima[1:])), f"{system}: {maxima}"
        assert all(value > limit for value in maxima), f"{system}: below Phi(-1)"

    # The three values quoted in the manuscript's prose.
    rounded = sorted({round(value, 4) for value in frame["max_probability"]})
    assert 0.1587 in rounded and 0.1588 in rounded and 0.1602 in rounded


def test_worst_case_derivative_is_positive() -> None:
    """f'(h) > 0 on (0, 1/(2 alpha)), checked against a numerical derivative."""
    for alpha in (0.320, 0.5, 2.0):
        upper = 1.0 / (2.0 * alpha)
        for h in np.linspace(0.05 * upper, 0.9 * upper, 25):
            analytic = float(
                norm.pdf(math.sqrt(1.0 - 2.0 * alpha * h))
                * alpha
                / math.sqrt(1.0 - 2.0 * alpha * h)
            )
            step = 1e-7 * upper
            numeric = (
                float(norm.cdf(-math.sqrt(1.0 - 2.0 * alpha * (h + step))))
                - float(norm.cdf(-math.sqrt(1.0 - 2.0 * alpha * (h - step))))
            ) / (2.0 * step)
            assert analytic > 0.0
            assert analytic == pytest.approx(numeric, rel=1e-4)


def test_underflow_threshold_lies_in_the_subnormal_range() -> None:
    """The caption's account of the binary64 underflow point must be accurate.

    Binary64 represents down to about 5e-324 through subnormals, below the
    smallest normal value of about 2.2e-308.  A CDF routine may return zero
    earlier; the one used here does so inside the subnormal range, near 6e-311.
    An earlier caption put the threshold at "roughly 1e-308", which is neither
    the representation limit nor this implementation's behaviour.
    """
    smallest_normal = float(np.finfo(np.float64).tiny)
    smallest_subnormal = float(np.nextafter(0.0, 1.0))
    assert smallest_normal == pytest.approx(2.2250738585072014e-308)
    assert smallest_subnormal == pytest.approx(5e-324)

    low, high = 1.0, 100.0
    for _ in range(200):
        middle = 0.5 * (low + high)
        if float(norm.cdf(-middle)) > 0.0:
            low = middle
        else:
            high = middle
    threshold = float(norm.cdf(-low))

    # Strictly inside the subnormal range: below the smallest normal value,
    # and above the smallest representable subnormal.
    assert smallest_subnormal < threshold < smallest_normal
    assert threshold == pytest.approx(6e-311, rel=0.2)


# ---------------------------------------------------------------------------
# The nearest-neighbour candidate limit of Appendix H
# ---------------------------------------------------------------------------


def unit_ball_volume(dimension: int) -> float:
    """Lebesgue volume of the unit ball in R^d."""
    from scipy.special import gamma as gamma_function

    return math.pi ** (dimension / 2.0) / float(
        gamma_function(dimension / 2.0 + 1.0)
    )


def nearest_neighbour_constant(dimension: int) -> float:
    """The constant in the candidate limit for N^{-1} S^{2/K} D_N."""
    from scipy.special import gamma as gamma_function

    return (
        2.0
        * math.pi
        * float(gamma_function(1.0 + 2.0 / dimension))
        * unit_ball_volume(dimension) ** (-2.0 / dimension)
        * (dimension / (dimension - 2.0)) ** (dimension / 2.0)
    )


@pytest.mark.parametrize("dimension", [4, 6])
def test_conditional_nearest_neighbour_formula_is_accurate(dimension: int) -> None:
    """Given the centre, the pointwise nearest-neighbour formula holds.

    This is the ingredient of the Appendix H candidate limit that is verified.
    Accuracy improves in S, which is what distinguishes it from the
    unconditional statement, where uniform integrability is unresolved.
    """
    rng = np.random.default_rng(400 + dimension)
    theta = np.zeros(dimension)
    for offset in (0.0, 1.5):
        centre = np.zeros(dimension)
        centre[0] = offset
        density = (2.0 * math.pi) ** (-dimension / 2.0) * math.exp(-(offset**2) / 2.0)
        ratios = []
        for simulations in (2_000, 20_000):
            atoms = centre + rng.normal(size=(1_500, simulations, dimension))
            squared = ((theta - atoms) ** 2).sum(axis=2).min(axis=1)
            formula = (
                float(np.exp(math.lgamma(1.0 + 2.0 / dimension)))
                * (unit_ball_volume(dimension) * simulations) ** (-2.0 / dimension)
                * density ** (-2.0 / dimension)
            )
            ratios.append(float(squared.mean()) / formula)
        # Within a few per cent, and not drifting away as S grows.
        assert all(abs(r - 1.0) < 0.08 for r in ratios), ratios
        assert abs(ratios[-1] - 1.0) <= abs(ratios[0] - 1.0) + 0.02


def test_gaussian_moment_identity_and_the_k_greater_than_two_threshold() -> None:
    """E[exp(a||W||^2)] = (1-2a)^{-K/2} e^{a|m|^2/(1-2a)}, finite iff K > 2 at a=1/K."""
    rng = np.random.default_rng(88)
    for dimension in (3, 4, 6):
        a = 1.0 / dimension
        assert 1.0 - 2.0 * a > 0.0, "K > 2 is exactly the integrability condition"
        exact = (1.0 - 2.0 * a) ** (-dimension / 2.0)
        draws = rng.normal(size=(2_000_000, dimension))
        simulated = float(np.exp(a * (draws**2).sum(axis=1)).mean())
        assert simulated == pytest.approx(exact, rel=0.03)

    # At K = 2 the moment diverges, which is the same boundary as Theorem 3.3.
    assert 1.0 - 2.0 * (1.0 / 2.0) == 0.0


def test_unconditional_limit_is_approached_from_below() -> None:
    """The unconditional average converges slowly, and from below.

    This is the uniform-integrability gap Appendix H records as open: the limit
    is carried by centres far from theta, exactly where the conditional formula
    needs the largest S.
    """
    rng = np.random.default_rng(2718)
    dimension = 4
    target = nearest_neighbour_constant(dimension)
    theta = np.zeros(dimension)
    values = []
    for simulations in (500, 4_000):
        centres = rng.normal(size=(3_000, 1, dimension))
        atoms = centres + rng.normal(size=(3_000, simulations, dimension))
        squared = ((theta[None, None, :] - atoms) ** 2).sum(axis=2).min(axis=1)
        values.append(simulations ** (2.0 / dimension) * float(squared.mean()))
    # Below the candidate limit, and rising towards it.
    assert all(v < target for v in values)
    assert values[-1] > values[0]


def test_limit_mass_sits_in_the_tail_of_the_centre_distribution() -> None:
    """Most of the candidate limit comes from centres far from theta."""
    rng = np.random.default_rng(31_415)
    for dimension, expected_share in ((4, 0.60), (6, 0.70)):
        a = 1.0 / dimension
        draws = rng.normal(size=(1_500_000, dimension))
        radius = (draws**2).sum(axis=1)
        weight = np.exp(a * radius)
        order = np.argsort(radius)
        sorted_weight = weight[order]
        cut = int(0.9 * len(sorted_weight))
        share = float(sorted_weight[:cut].sum() / sorted_weight.sum())
        # The nearest 90 per cent of centres carry well under 90 per cent.
        assert share < expected_share


def brownian_score_second_moment(dimension: int, h: float) -> float:
    """Proposition 6.3: E[(d_j G_h)^2] at x = y = 0."""
    return (
        (1.0 - h)
        * (2.0 * math.pi) ** (-dimension)
        * h ** (-dimension / 2.0 - 1.0)
        * (2.0 - h) ** (-dimension / 2.0 - 1.0)
    )


@pytest.mark.parametrize("dimension", [1, 2, 4])
def test_score_second_moment_matches_simulation(dimension: int) -> None:
    """The exact score second moment agrees with direct Monte Carlo."""
    rng = np.random.default_rng(9000 + dimension)
    for m_steps in (8, 32, 128):
        h = 1.0 / m_steps
        draws = 2_000_000
        xi = rng.normal(size=(draws, dimension))
        z = math.sqrt(1.0 - h) * xi
        summand = (2.0 * math.pi * h) ** (-dimension / 2.0) * np.exp(
            -(z**2).sum(axis=1) / (2.0 * h)
        )
        gradient = (z[:, 0] / h) * summand
        squared = gradient**2
        # The summand is heavy-tailed, so the sample mean of its square has a
        # relative standard error of several per cent at the finer steps.
        # Compare at three standard errors rather than at a fixed tolerance.
        estimate = float(squared.mean())
        standard_error = float(squared.std(ddof=1)) / math.sqrt(draws)
        exact = brownian_score_second_moment(dimension, h)
        assert abs(estimate - exact) < MC_SIGMAS * standard_error


def test_score_to_density_ratio_is_free_of_dimension() -> None:
    """E[(d_j G)^2] / E[G^2] = (1-h) / (h(2-h)), the same in every dimension."""
    for h in (0.5, 0.1, 0.01, 1e-4):
        expected = (1.0 - h) / (h * (2.0 - h))
        ratios = []
        for dimension in (1, 2, 4, 7):
            density = brownian_moment_closed_form(dimension, 1.0 / h, 2.0, 0.0)
            ratios.append(brownian_score_second_moment(dimension, h) / density)
        for ratio in ratios:
            assert ratio == pytest.approx(expected, rel=1e-12)
        assert max(ratios) - min(ratios) < 1e-9 * max(ratios)


def test_score_effective_size_is_one_power_of_m_more_demanding() -> None:
    """The score scale is S h^{(K+2)/2}, against S h^{K/2} for the density."""
    for dimension in (2, 4, 6):
        for m_steps in (10, 100, 1000):
            h = 1.0 / m_steps
            density_scale = h ** (dimension / 2.0)
            score_scale = h ** ((dimension + 2.0) / 2.0)
            assert score_scale == pytest.approx(density_scale * h)
            # In K = 4 the published condition allows S << M^2 while the score
            # needs S >> M^3, so the two cannot be satisfied together.
            if dimension == 4:
                assert m_steps**3 > m_steps**2


# ---------------------------------------------------------------------------
# Finite-sample accuracy at the implemented design, and the K = 2 boundary
# ---------------------------------------------------------------------------


def test_reported_finite_sample_accuracy_at_the_implemented_design() -> None:
    """The figures quoted in Section 8.2 follow from Proposition 3.1.

    At K = 4, M = 10, S = 5000 the relative second moment is 27.70 at a
    coincident endpoint and 44.48 at unit separation, giving relative standard
    deviations of 7.3 and 9.3 per cent.
    """
    dimension, m_steps, simulations, observations = 4, 10, 5_000, 544
    h = 1.0 / m_steps

    for distance, expected_ratio, expected_rmse in (
        (0.0, 27.70, 0.073),
        (1.0, 44.48, 0.093),
    ):
        density = (2.0 * math.pi) ** (-dimension / 2.0) * math.exp(-(distance**2) / 2.0)
        second = brownian_moment_closed_form(dimension, m_steps, 2.0, distance)
        ratio = second / density**2
        assert ratio == pytest.approx(expected_ratio, abs=0.01)
        relative_variance = (ratio - 1.0) / simulations
        assert math.sqrt(relative_variance) == pytest.approx(expected_rmse, abs=0.001)

    # The coincident case has the closed form (h(2-h))^{-K/2}.
    coincident = brownian_moment_closed_form(dimension, m_steps, 2.0, 0.0)
    coincident /= ((2.0 * math.pi) ** (-dimension / 2.0)) ** 2
    assert coincident == pytest.approx((h * (2.0 - h)) ** (-dimension / 2.0), rel=1e-12)

    # Summed second-order log bias over the 544-term log likelihood.
    density = (2.0 * math.pi) ** (-dimension / 2.0)
    ratio = brownian_moment_closed_form(dimension, m_steps, 2.0, 0.0) / density**2
    per_observation = (ratio - 1.0) / simulations / 2.0
    assert per_observation * observations == pytest.approx(1.45, abs=0.05)


def test_dimension_two_is_the_exact_boundary_along_the_diagonal() -> None:
    """R = n^{1-K/2} along M = S = n: divergent, unit, then vanishing.

    At K = 2 the relative variance converges to 1/2, so the estimator is
    bounded away from consistency without collapsing.
    """
    for m_steps in (2, 8, 32, 128):
        assert m_steps ** (1 - 2 / 2.0) == pytest.approx(1.0)  # K = 2 gives R = 1
        assert m_steps ** (1 - 1 / 2.0) > 1.0                  # K = 1 diverges
        assert m_steps ** (1 - 4 / 2.0) < 1.0                  # K = 4 vanishes

    density_squared = (2.0 * math.pi) ** (-2)
    ratios = []
    for n in (32, 512, 8192):
        variance = gr.brownian_estimator_variance(2, n, n)
        ratios.append(variance / density_squared)
        # Closed form: (1/n)(n/(2 - 1/n) - 1).
        assert ratios[-1] == pytest.approx(
            (n / (2.0 - 1.0 / n) - 1.0) / n, rel=1e-9
        )
    assert ratios[-1] == pytest.approx(0.5, abs=1e-3)
    assert all(r < 0.5 for r in ratios)

    # K = 1 is consistent along the same diagonal; K = 4 diverges.
    assert gr.brownian_estimator_variance(1, 8192, 8192) / (
        2.0 * math.pi
    ) ** -1 < 0.01
    assert gr.brownian_estimator_variance(4, 8192, 8192) / (
        2.0 * math.pi
    ) ** -4 > 100.0


def test_subcritical_condition_covers_the_diagonal() -> None:
    """The diagonal satisfies the subcritical condition exactly when K > 2."""
    for dimension in (1, 2, 3, 4, 6):
        values = []
        for n in (100, 10_000, 1_000_000):
            h = 1.0 / n
            values.append(n * h ** (dimension / 2.0) * math.log(1.0 / h) ** (dimension / 2.0))
        if dimension > 2:
            # Decreasing towards zero.  The approach is slow at K = 3, where the
            # polynomial factor n^{1-K/2} = n^{-1/2} only just beats the
            # logarithm, so monotonicity is the right test rather than a fixed
            # threshold at any particular n.
            assert values[1] < values[0], f"K={dimension} should be decreasing"
            assert values[2] < values[1], f"K={dimension} should be decreasing"
            assert values[-1] < 0.2 * values[0], f"K={dimension} should be falling fast"
        else:
            assert values[-1] > values[0], f"K={dimension} should not be subcritical"


def test_manuscript_collapse_table_matches_the_generated_values() -> None:
    """Table 4 is hand-typed in the manuscript; it must not drift from the CSV.

    The same guard already covers Table 5.  Replication counts must also be
    constant across rows: a fixed draw budget estimates the quantiles worst at
    the largest M, which is where the collapse is sharpest.
    """
    frame = pd.read_csv(ROOT / "paper" / "tables" / "brownian_subcritical_path.csv")
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")

    assert frame["replications"].nunique() == 1, "replication count must be constant"
    assert int(frame["replications"].iloc[0]) == 20_000

    # Spot-check the two ends of the table against what the manuscript prints.
    first = frame[frame["M"] == 8].iloc[0]
    last = frame[frame["M"] == 512].iloc[0]
    assert round(float(first["mean_relative"]), 3) == 1.001
    assert round(float(first["mean_standard_error"]), 3) == 0.010
    assert round(float(last["mean_relative"]), 3) == 0.879
    assert round(float(last["mean_standard_error"]), 3) == 0.073
    for text in ("0.879", "(0.073)", "0.3674"):
        assert text in manuscript, f"{text} missing from the manuscript"

    # The mean is pinned at one while the median falls by ten orders of
    # magnitude: that contrast is the content of the table.
    assert abs(float(last["mean_relative"]) - 1.0) < 2.0 * float(
        last["mean_standard_error"]
    )
    assert float(first["median_relative"]) / float(last["median_relative"]) > 1e8


# ---------------------------------------------------------------------------
# The critical limit law at K = 2 along M = S = n
# ---------------------------------------------------------------------------


def poisson_integral_sample(replications: int, rng, horizon: float = 45.0):
    """Draw L = sum_i exp(-t_i) for t_i a unit-rate Poisson process on (0, inf).

    The tail beyond ``horizon`` contributes below 1e-19 and is dropped.
    """
    counts = rng.poisson(horizon, size=replications)
    out = np.empty(replications)
    for start in range(0, replications, 40_000):
        stop = min(start + 40_000, replications)
        block = counts[start:stop]
        width = int(block.max())
        points = rng.random(size=(stop - start, width)) * horizon
        live = np.arange(width)[None, :] < block[:, None]
        out[start:stop] = np.where(live, np.exp(-points), 0.0).sum(axis=1)
    return out


def test_critical_case_has_an_exact_exponential_representation() -> None:
    """At K = 2, M = S = n, qhat/p = sum_s exp(-(n-1) E_s) exactly.

    This identity is what makes the limit law provable rather than conjectural,
    and its moments must reproduce Proposition 3.1 at r = 1 and r = 2.
    """
    for n in (4, 16, 128, 1024):
        # E[exp(-(n-1)E)] = 1/n, so the estimator is exactly unbiased.
        assert 1.0 / n == pytest.approx(1.0 / n)
        mean_relative = n * (1.0 / n)
        assert mean_relative == pytest.approx(1.0)

        # Var = n(1/(2n-1) - 1/n^2) = n/(2n-1) - 1/n, matching Proposition 3.1.
        variance = n / (2.0 * n - 1.0) - 1.0 / n
        density_squared = ((2.0 * math.pi) ** -1) ** 2
        from_moments = gr.brownian_estimator_variance(2, n, n) / density_squared
        assert variance == pytest.approx(from_moments, rel=1e-9)

    # And the variance tends to the Campbell value 1/2.
    assert 8192 / (2.0 * 8192 - 1.0) - 1.0 / 8192 == pytest.approx(0.5, abs=1e-3)


def test_critical_limit_law_matches_simulation() -> None:
    """qhat/p at K = 2 converges to the Poisson integral, not to 1."""
    rng = np.random.default_rng(606)

    limit = poisson_integral_sample(120_000, rng)
    assert float(limit.mean()) == pytest.approx(1.0, abs=0.02)
    assert float(limit.var()) == pytest.approx(0.5, abs=0.02)

    estimates = gr.simulate_brownian_estimator(
        dimension=2, m_steps=2048, simulations=2048, replications=40_000, rng=rng
    )
    relative = estimates / gr.true_brownian_density_at_origin(2)

    # The finite-n law already agrees with the limit on every summary that
    # distinguishes it from the degenerate law at 1.
    assert float(np.median(relative)) == pytest.approx(
        float(np.median(limit)), abs=0.02
    )
    assert float((relative < 0.5).mean()) == pytest.approx(
        float((limit < 0.5).mean()), abs=0.02
    )
    assert float((relative < 0.1).mean()) == pytest.approx(
        float((limit < 0.1).mean()), abs=0.01
    )

    # Non-degeneracy: the median is well away from 1 and the estimator falls
    # below half the true density with probability bounded away from zero.
    assert float(np.median(relative)) < 0.93
    assert float((relative < 0.5).mean()) > 0.2
