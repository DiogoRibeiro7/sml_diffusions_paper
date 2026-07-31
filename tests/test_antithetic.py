"""Verification of the antithetic-variates analysis of Section 8.2.

Three claims are checked here.  First, the pair-average variance formula
``Var(A) = sigma^2 (1 + rho) / 2`` and the estimator variance
``Var(qhat) = sigma^2 (1 + rho) / (2P)``, against direct simulation.  Second, the
variance-equivalent evaluation count ``N_eff = E / (1 + rho)``, including the
distinction between the two ratios that an earlier version of the manuscript
conflated: ``E / N_eff = 1 + rho`` measures how far the raw evaluation count
overstates the effective one, whereas ``N_eff / P = 2 / (1 + rho)`` compares the
effective count with the number of independent units.  At ``rho = 1`` the first
is 2 and the second is 1.

Third, Lemma 8.2: antithetic pairing changes the variance constant but not the
``h^{-K/2}`` exponent of the endpoint second moment.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

# Monte Carlo comparisons are checked at a generous relative tolerance because
# a variance of variances converges slowly; the exponent tests below are the
# sharp ones.
MC_RELATIVE_TOLERANCE = 0.12


def n_eff(pairs: int, rho: float) -> float:
    """Variance-equivalent number of independent evaluations, E / (1 + rho).

    The manuscript states the definition on rho in (-1, 1].  At the excluded
    endpoint the idealised pair-average variance is zero, so the convention
    assigns no finite equivalent count; ``inf`` is returned to make that the
    caller's explicit case rather than an exception.
    """
    if rho <= -1.0:
        return math.inf
    return 2.0 * pairs / (1.0 + rho)


# ---------------------------------------------------------------------------
# The variance formula
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rho", [1.0, 0.5, 0.0, -0.5, -0.9, -0.99])
def test_pair_average_variance_matches_simulation(rho: float) -> None:
    """Var(A) = sigma^2 (1 + rho) / 2, checked by direct simulation."""
    rng = np.random.default_rng(abs(int(rho * 1000)) + 11)
    sigma = 1.4
    covariance = sigma**2 * np.array([[1.0, rho], [rho, 1.0]])
    eigenvalues, vectors = np.linalg.eigh(covariance)
    root = vectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0.0))) @ vectors.T
    draws = root @ rng.normal(size=(2, 400_000))
    averages = draws.mean(axis=0)

    predicted = sigma**2 * (1.0 + rho) / 2.0
    if predicted > 1e-6:
        assert averages.var(ddof=1) == pytest.approx(
            predicted, rel=MC_RELATIVE_TOLERANCE
        )
    else:
        assert averages.var(ddof=1) < 1e-3


@pytest.mark.parametrize("rho", [1.0, 0.0, -0.5])
def test_estimator_variance_scales_as_one_over_p(rho: float) -> None:
    """Var(qhat_ant) = sigma^2 (1 + rho) / (2P), across two values of P."""
    rng = np.random.default_rng(4242 + int(rho * 10))
    sigma = 1.0
    covariance = sigma**2 * np.array([[1.0, rho], [rho, 1.0]])
    eigenvalues, vectors = np.linalg.eigh(covariance)
    root = vectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0.0))) @ vectors.T
    for pairs in (250, 1000):
        replications = 6000
        draws = root @ rng.normal(size=(2, replications * pairs))
        averages = draws.mean(axis=0).reshape(replications, pairs).mean(axis=1)
        predicted = sigma**2 * (1.0 + rho) / (2.0 * pairs)
        if predicted > 1e-9:
            assert averages.var(ddof=1) == pytest.approx(
                predicted, rel=MC_RELATIVE_TOLERANCE
            )


def test_perfect_negative_correlation_gives_zero_variance() -> None:
    """At rho = -1 the idealised pair average is deterministic."""
    rng = np.random.default_rng(99)
    base = rng.normal(size=200_000)
    averages = 0.5 * (base + (-base))
    assert averages.var() == pytest.approx(0.0, abs=1e-24)


# ---------------------------------------------------------------------------
# The variance-equivalent count and the two ratios
# ---------------------------------------------------------------------------


def test_n_eff_equals_e_over_one_plus_rho() -> None:
    """N_eff = E / (1 + rho) = 2P / (1 + rho)."""
    pairs = 5_000
    evaluations = 2 * pairs
    for rho in (1.0, 0.5, 0.0, -0.5, -0.9):
        assert n_eff(pairs, rho) == pytest.approx(evaluations / (1.0 + rho))


def test_the_two_ratios_are_distinct_and_not_interchanged() -> None:
    """E / N_eff = 1 + rho, while N_eff / P = 2 / (1 + rho).

    An earlier version of the manuscript used the second where the first was
    meant, and said the misstatement factor was ``2 / (1 + rho)``, "a factor of
    two at a coincident endpoint".  At rho = 1 that expression equals one.
    """
    pairs = 5_000
    evaluations = 2 * pairs
    for rho in (1.0, 0.5, 0.0, -0.5):
        effective = n_eff(pairs, rho)
        assert evaluations / effective == pytest.approx(1.0 + rho)
        assert effective / pairs == pytest.approx(2.0 / (1.0 + rho))

    # At rho = 1 the two ratios take different values, 2 and 1, which is
    # precisely where the earlier wording went wrong.
    at_one = n_eff(pairs, 1.0)
    assert evaluations / at_one == pytest.approx(2.0)
    assert at_one / pairs == pytest.approx(1.0)

    # They agree only at rho = 0, where both equal one.
    at_zero = n_eff(pairs, 0.0)
    assert evaluations / at_zero == pytest.approx(1.0)
    assert at_zero / pairs == pytest.approx(2.0)


def test_principal_cases_of_the_interpretation() -> None:
    """The four cases stated in Section 8.2."""
    pairs = 1_000
    evaluations = 2 * pairs

    # rho = 1: N_eff = P = E/2, so E overstates by exactly two.
    assert n_eff(pairs, 1.0) == pytest.approx(pairs)
    assert n_eff(pairs, 1.0) == pytest.approx(evaluations / 2)

    # rho = 0: N_eff = E, pairing is neutral.
    assert n_eff(pairs, 0.0) == pytest.approx(evaluations)

    # -1 < rho < 0: N_eff > E, genuine variance reduction.
    assert n_eff(pairs, -0.5) > evaluations

    # rho -> -1: N_eff diverges, a convention rather than a literal count.
    assert n_eff(pairs, -0.999) > 100 * evaluations
    assert math.isinf(n_eff(pairs, -1.0)) or n_eff(pairs, -1.0) > 1e12


def test_n_eff_is_never_below_the_pair_count() -> None:
    """rho <= 1 forces N_eff >= P, so R_pair is the conservative diagnostic."""
    pairs = 5_000
    for rho in np.linspace(-0.99, 1.0, 200):
        assert n_eff(pairs, float(rho)) >= pairs - 1e-9


def test_simulated_variance_identifies_n_eff() -> None:
    """N_eff recovered from simulation matches E / (1 + rho).

    The definition is operational: N_eff independent draws should have the same
    average-variance as the antithetic design, so recovering it from a simulated
    variance is the check that the convention means what it says.
    """
    rng = np.random.default_rng(2026)
    sigma, pairs, replications = 1.0, 500, 20_000
    for rho in (1.0, 0.5, 0.0, -0.5):
        covariance = sigma**2 * np.array([[1.0, rho], [rho, 1.0]])
        eigenvalues, vectors = np.linalg.eigh(covariance)
        root = vectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0.0))) @ vectors.T
        draws = root @ rng.normal(size=(2, replications * pairs))
        averages = draws.mean(axis=0).reshape(replications, pairs).mean(axis=1)
        observed = averages.var(ddof=1)
        # An average of n independent draws has variance sigma^2 / n.
        recovered = sigma**2 / observed
        assert recovered == pytest.approx(
            n_eff(pairs, rho), rel=MC_RELATIVE_TOLERANCE
        )


# ---------------------------------------------------------------------------
# Lemma 8.2: the exponent survives pairing
# ---------------------------------------------------------------------------


def endpoint_summand(z: np.ndarray, y: np.ndarray, h: float) -> np.ndarray:
    """One-step Gaussian endpoint density at y from preterminal states z."""
    dimension = y.size
    squared = ((y - z) ** 2).sum(axis=-1)
    return (2.0 * math.pi * h) ** (-dimension / 2.0) * np.exp(-squared / (2.0 * h))


@pytest.mark.parametrize("dimension", [1, 2, 4])
def test_sandwich_bound_holds_pathwise(dimension: int) -> None:
    """(a^2+b^2)/4 <= A^2 <= (a^2+b^2)/2 for nonnegative a, b."""
    rng = np.random.default_rng(500 + dimension)
    a = rng.exponential(size=20_000)
    b = rng.exponential(size=20_000)
    averages = 0.5 * (a + b)
    assert np.all(averages**2 >= (a**2 + b**2) / 4 - 1e-12)
    assert np.all(averages**2 <= (a**2 + b**2) / 2 + 1e-12)


@pytest.mark.parametrize("dimension", [1, 2, 3, 4])
def test_antithetic_second_moment_keeps_the_h_exponent(dimension: int) -> None:
    """E[A^2] grows as h^{-K/2}, exactly as E[G^2] does.

    The pair average is formed from antithetic preterminal draws, so its
    dependence structure is the real one rather than an assumed correlation.
    """
    rng = np.random.default_rng(31_000 + dimension)
    start = np.zeros(dimension)
    endpoint = np.zeros(dimension)  # coincident: the worst case, rho_A = 1
    draws = 60_000

    steps = [1 / 20, 1 / 40, 1 / 80]
    second_moments = []
    for h in steps:
        noise = rng.normal(size=(draws, dimension))
        forward = start + math.sqrt(1.0 - h) * noise
        reflected = start - math.sqrt(1.0 - h) * noise
        plus = endpoint_summand(forward, endpoint, h)
        minus = endpoint_summand(reflected, endpoint, h)
        averages = 0.5 * (plus + minus)
        second_moments.append(float((averages**2).mean()))

    # Successive halvings of h should multiply the second moment by 2^{K/2}.
    for earlier, later in zip(second_moments, second_moments[1:]):
        ratio = later / earlier
        assert ratio == pytest.approx(2.0 ** (dimension / 2.0), rel=0.25)


@pytest.mark.parametrize("dimension", [1, 2, 4])
def test_sandwich_is_tight_within_a_factor_of_two(dimension: int) -> None:
    """E[A^2] lies in [E[G^2]/2, E[G^2]], the bound Lemma 8.2 asserts."""
    rng = np.random.default_rng(770 + dimension)
    start = np.zeros(dimension)
    h = 1 / 40
    draws = 80_000
    for offset in (0.0, 0.4, 1.2):
        endpoint = np.full(dimension, offset)
        noise = rng.normal(size=(draws, dimension))
        plus = endpoint_summand(start + math.sqrt(1.0 - h) * noise, endpoint, h)
        minus = endpoint_summand(start - math.sqrt(1.0 - h) * noise, endpoint, h)
        averages = 0.5 * (plus + minus)
        pair_moment = float((averages**2).mean())
        single_moment = float((np.concatenate([plus, minus]) ** 2).mean())
        assert pair_moment <= single_moment * (1.0 + 1e-6)
        assert pair_moment >= single_moment / 2.0 * (1.0 - 1e-6)


def test_coincident_endpoint_gives_identical_partners() -> None:
    """Proposition 8.1: at y = x the antithetic partner is the same number."""
    rng = np.random.default_rng(8)
    for dimension in (1, 2, 4):
        start = rng.normal(size=dimension)
        h = 1 / 30
        noise = rng.normal(size=(5_000, dimension))
        plus = endpoint_summand(start + math.sqrt(1.0 - h) * noise, start, h)
        minus = endpoint_summand(start - math.sqrt(1.0 - h) * noise, start, h)
        assert np.allclose(plus, minus, rtol=0, atol=1e-12)
        correlation = np.corrcoef(plus, minus)[0, 1]
        assert correlation == pytest.approx(1.0, abs=1e-9)
