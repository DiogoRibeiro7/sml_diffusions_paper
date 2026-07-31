"""Verification of the block positive-semidefiniteness lemma of Appendix E.

Lemma E.1 of the manuscript states that for symmetric positive semidefinite
``A``, vector ``r`` and scalar ``c``,

    B = [[A, r], [r^T, c]]  is PSD  <=>  r in Range(A)  and  c >= r^T A^+ r,

where ``A^+`` is the Moore-Penrose pseudoinverse.  An earlier version of the
manuscript asserted that the second condition follows from the first.  It does
not, and the tests below exhibit the separation explicitly: the two conditions
are logically independent, and dropping either one admits an indefinite matrix.

Every claim is checked against numerically computed eigenvalues rather than
against the algebraic condition it is meant to characterise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import check_correlation_matrix as ccm  # noqa: E402

# An eigenvalue below this counts as negative; above its negation, nonnegative.
EIGENVALUE_TOLERANCE = 1e-10


def block(A: np.ndarray, r: np.ndarray, c: float) -> np.ndarray:
    """Assemble the bordered matrix of the lemma."""
    m = A.shape[0]
    B = np.empty((m + 1, m + 1))
    B[:m, :m] = A
    B[:m, m] = r
    B[m, :m] = r
    B[m, m] = c
    return B


def is_psd(matrix: np.ndarray) -> bool:
    """Numerically decide positive semidefiniteness from the spectrum."""
    return bool(np.linalg.eigvalsh(matrix).min() >= -EIGENVALUE_TOLERANCE)


def in_range(A: np.ndarray, r: np.ndarray) -> bool:
    """Decide r in Range(A) through the projector I - A A^+."""
    residual = r - A @ np.linalg.pinv(A) @ r
    return bool(np.linalg.norm(residual) < 1e-9)


def magnitude_slack(A: np.ndarray, r: np.ndarray, c: float) -> float:
    """Return c - r^T A^+ r, nonnegative exactly when the bound holds."""
    return float(c - r @ np.linalg.pinv(A) @ r)


# ---------------------------------------------------------------------------
# The two conditions are separately necessary
# ---------------------------------------------------------------------------


def test_compatibility_fails_gives_indefinite() -> None:
    """Reject a vector outside Range(A): the bordered matrix is indefinite."""
    A = np.diag([1.0, 0.0])
    r = np.array([0.0, 0.5])  # second coordinate spans Null(A)
    assert not in_range(A, r)
    assert not is_psd(block(A, r, 1.0))


def test_range_holds_but_magnitude_fails_gives_indefinite() -> None:
    """The critical case: r in Range(A) but c < r^T A^+ r is still indefinite.

    This is the counterexample to the inference the earlier proof made.  Here
    A is singular, r lies exactly in its range, and yet the matrix is not PSD.
    """
    A = np.diag([1.0, 0.0])
    r = np.array([2.0, 0.0])
    assert in_range(A, r)
    assert magnitude_slack(A, r, 1.0) == pytest.approx(1.0 - 4.0)
    assert magnitude_slack(A, r, 1.0) < 0.0
    assert not is_psd(block(A, r, 1.0))


def test_both_conditions_hold_gives_psd() -> None:
    """Range membership together with the magnitude bound gives PSD."""
    A = np.diag([4.0, 0.0])
    r = np.array([2.0, 0.0])
    assert in_range(A, r)
    assert magnitude_slack(A, r, 1.0) == pytest.approx(0.0)
    assert is_psd(block(A, r, 1.0))


def test_equality_case_has_a_zero_eigenvalue() -> None:
    """At c = r^T A^+ r the bordered matrix is PSD but singular."""
    A = np.diag([4.0, 1.0])
    r = np.array([2.0, 1.0])
    c = float(r @ np.linalg.pinv(A) @ r)
    B = block(A, r, c)
    eigenvalues = np.linalg.eigvalsh(B)
    assert eigenvalues.min() == pytest.approx(0.0, abs=1e-9)
    assert is_psd(B)


def test_positive_definite_block_reduces_to_the_schur_complement() -> None:
    """When A is nonsingular the range condition is vacuous and A^+ = A^-1."""
    rng = np.random.default_rng(20260731)
    for _ in range(50):
        factor = rng.normal(size=(3, 3))
        A = factor @ factor.T + 0.5 * np.eye(3)
        r = rng.normal(size=3)
        schur = float(1.0 - r @ np.linalg.solve(A, r))
        assert in_range(A, r)
        assert magnitude_slack(A, r, 1.0) == pytest.approx(schur)
        assert is_psd(block(A, r, 1.0)) == (schur >= -EIGENVALUE_TOLERANCE)


# ---------------------------------------------------------------------------
# Randomised agreement between the lemma and the spectrum
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dimension", [2, 3, 4])
def test_lemma_agrees_with_eigenvalues_on_random_singular_blocks(dimension: int) -> None:
    """The two-part criterion must match the spectrum on singular blocks."""
    rng = np.random.default_rng(1000 + dimension)
    agreements = 0
    both_outcomes = set()
    for _ in range(400):
        rank = rng.integers(1, dimension)  # strictly singular
        factor = rng.normal(size=(dimension, rank))
        A = factor @ factor.T
        if rng.random() < 0.5:
            # Draw r inside Range(A), then scale it across the critical bound.
            r = factor @ rng.normal(size=rank)
            r = r * rng.uniform(0.1, 3.0)
        else:
            r = rng.normal(size=dimension)
        c = 1.0
        predicted = in_range(A, r) and magnitude_slack(A, r, c) >= -EIGENVALUE_TOLERANCE
        actual = is_psd(block(A, r, c))
        both_outcomes.add(actual)
        agreements += int(predicted == actual)
    assert agreements == 400
    assert both_outcomes == {True, False}, "the sweep must produce both outcomes"


def test_the_two_conditions_are_logically_independent() -> None:
    """Each condition holds without the other in some configuration."""
    A = np.diag([1.0, 0.0])

    # Range holds, magnitude fails.
    r_one = np.array([3.0, 0.0])
    assert in_range(A, r_one) and magnitude_slack(A, r_one, 1.0) < 0.0

    # Magnitude holds, range fails.  A^+ annihilates the null direction, so the
    # quadratic form is zero while r has a component outside the range.
    r_two = np.array([0.0, 5.0])
    assert not in_range(A, r_two) and magnitude_slack(A, r_two, 1.0) > 0.0
    assert not is_psd(block(A, r_two, 1.0))


# ---------------------------------------------------------------------------
# The Brandt and Santa-Clara structure
# ---------------------------------------------------------------------------


def degenerate_blocks(
    phi: float, phi_star: float, rho_ww: float, rho_wy: float, rho_wsy: float
) -> tuple[np.ndarray, np.ndarray, float]:
    """Build A_t and r_t in the degenerate configuration C_t = eps^2 = 0.

    Volatility is pinned at v^2 = Q, so X is the deterministic combination
    (phi W - phi* W*) / v and the 3x3 block for (W, W*, X) is singular.
    """
    quadratic = phi**2 + phi_star**2 - 2.0 * rho_ww * phi * phi_star
    v = np.sqrt(quadratic)
    rho_wx = (phi - rho_ww * phi_star) / v
    rho_wsx = (rho_ww * phi - phi_star) / v
    A = np.array(
        [
            [1.0, rho_ww, rho_wx],
            [rho_ww, 1.0, rho_wsx],
            [rho_wx, rho_wsx, 1.0],
        ]
    )
    induced_rho_xy = (phi * rho_wy - phi_star * rho_wsy) / v
    r = np.array([rho_wy, rho_wsy, induced_rho_xy])
    return A, r, v


def test_degenerate_block_is_singular_with_one_dimensional_kernel() -> None:
    """A_t is singular exactly as Proposition E.2 claims."""
    A, _, _ = degenerate_blocks(0.03, 0.02, 0.3, 0.1, -0.2)
    eigenvalues = np.linalg.eigvalsh(A)
    assert eigenvalues.min() == pytest.approx(0.0, abs=1e-12)
    assert np.linalg.matrix_rank(A, tol=1e-10) == 2


def test_compatibility_alone_is_not_sufficient_in_the_model_structure() -> None:
    """The manuscript's central correction, on the model's own matrices.

    The induced value of rho_xy is imposed, so the compatibility relation holds
    by construction, yet the matrix is indefinite because the free correlations
    with Y violate the three-dimensional magnitude condition.
    """
    # rho_wy and rho_w*y chosen to breach rho_wy^2 - 2 rho_ww rho_wy rho_w*y
    # + rho_w*y^2 <= 1 - rho_ww^2 while every entry, including the induced
    # rho_xy, stays inside [-1, 1].  Equal values make the induced correlation
    # (phi - phi*) rho / v, which is small because phi and phi* are close.
    phi, phi_star, rho_ww = 0.03, 0.02, 0.3
    rho_wy, rho_wsy = 0.9, 0.9
    A, r, _ = degenerate_blocks(phi, phi_star, rho_ww, rho_wy, rho_wsy)

    left = rho_wy**2 - 2.0 * rho_ww * rho_wy * rho_wsy + rho_wsy**2
    right = 1.0 - rho_ww**2
    assert left > right, "the test state must violate the magnitude condition"

    assert in_range(A, r), "compatibility holds by construction"
    assert magnitude_slack(A, r, 1.0) < 0.0, "the magnitude bound must fail"
    assert not is_psd(block(A, r, 1.0))
    assert np.all(np.abs(block(A, r, 1.0)) <= 1.0 + 1e-12), "entrywise bounds hold"


def test_both_conditions_together_give_a_valid_model_matrix() -> None:
    """With the magnitude condition satisfied the full matrix is PSD."""
    phi, phi_star, rho_ww = 0.03, 0.02, 0.3
    rho_wy, rho_wsy = 0.2, -0.1
    A, r, _ = degenerate_blocks(phi, phi_star, rho_ww, rho_wy, rho_wsy)

    left = rho_wy**2 - 2.0 * rho_ww * rho_wy * rho_wsy + rho_wsy**2
    right = 1.0 - rho_ww**2
    assert left <= right

    assert in_range(A, r)
    assert magnitude_slack(A, r, 1.0) >= -EIGENVALUE_TOLERANCE
    assert is_psd(block(A, r, 1.0))


def test_wrong_rho_xy_breaks_compatibility_in_the_model_structure() -> None:
    """Departing from the induced value makes the matrix indefinite."""
    A, r, _ = degenerate_blocks(0.03, 0.02, 0.3, 0.2, -0.1)
    perturbed = r.copy()
    perturbed[2] += 0.05
    assert not in_range(A, perturbed)
    assert not is_psd(block(A, perturbed, 1.0))


def test_three_dimensional_condition_matches_the_full_matrix() -> None:
    """The reduction to the (W, W*, Y) block agrees with the 4x4 spectrum.

    Proposition E.2 proves that, given compatibility, R_t is PSD if and only if
    the three-dimensional correlation matrix of (W, W*, Y) is.  This sweeps a
    grid of free correlations and checks the equivalence pointwise.
    """
    phi, phi_star, rho_ww = 0.03, 0.02, 0.3
    seen = set()
    for rho_wy in np.linspace(-0.99, 0.99, 25):
        for rho_wsy in np.linspace(-0.99, 0.99, 25):
            A, r, _ = degenerate_blocks(phi, phi_star, rho_ww, rho_wy, rho_wsy)
            full_psd = is_psd(block(A, r, 1.0))
            sigma = np.array(
                [
                    [1.0, rho_ww, rho_wy],
                    [rho_ww, 1.0, rho_wsy],
                    [rho_wy, rho_wsy, 1.0],
                ]
            )
            three_psd = is_psd(sigma)
            explicit = (
                rho_wy**2 - 2.0 * rho_ww * rho_wy * rho_wsy + rho_wsy**2
                <= 1.0 - rho_ww**2 + EIGENVALUE_TOLERANCE
            )
            assert full_psd == three_psd
            assert three_psd == explicit
            seen.add(full_psd)
    assert seen == {True, False}


def test_perfectly_correlated_case_uses_the_pseudoinverse_of_b() -> None:
    """Remark E.3: at |rho_ww*| = 1 the range condition forces rho_w*y."""
    for sign in (1.0, -1.0):
        B = np.array([[1.0, sign], [sign, 1.0]])
        pseudo = np.linalg.pinv(B)
        assert pseudo == pytest.approx(0.25 * np.array([[1.0, sign], [sign, 1.0]]))

        compatible = np.array([0.4, sign * 0.4])
        assert in_range(B, compatible)
        assert magnitude_slack(B, compatible, 1.0) == pytest.approx(1.0 - 0.4**2)
        assert is_psd(block(B, compatible, 1.0))

        incompatible = np.array([0.4, -sign * 0.4])
        assert not in_range(B, incompatible)
        assert not is_psd(block(B, incompatible, 1.0))


def test_reported_estimates_are_far_from_the_degenerate_configuration() -> None:
    """The correction is a specification gap, not a defect in the estimates.

    The degenerate configuration needs C_t = 0, and both reported systems have
    C = 0.003 > 0, so no reported state reaches it.
    """
    for parameters in (ccm.US_UK, ccm.US_DE):
        assert parameters.currency_quadratic > 0.0
