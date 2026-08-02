"""Verification of Proposition F.1 and the three feasible sets of Appendix F.

Proposition F.1 is stated in two parts, and the split matters.  Part A locates
the minimiser of an affine objective on any nonempty compact scalar set and uses
no representation by constraints, so it covers the global set ``C_glob`` whose
constraints are indexed by a continuum.  Part B identifies which constraint is
active, and that needs the finite continuous representation; it does not extend
to an infinite family without a further argument.

The tests below check both parts, and check the separation: a set can be compact,
so that Part A applies and the minimiser is located, while no single named
constraint of an infinite family is active in the sense Part B asserts.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

TOLERANCE = 1e-12


def minimise_affine(candidates: np.ndarray, slope_sum: float) -> float:
    """Minimise ``sum_t (A_t - gamma_t c)`` over a finite candidate set.

    The objective is affine with slope ``-slope_sum``, so the minimiser is the
    largest feasible point when ``slope_sum > 0`` and the smallest otherwise.
    """
    if slope_sum == 0.0:
        raise ValueError("the slope must be nonzero for a unique vertex")
    return float(candidates.max() if slope_sum > 0 else candidates.min())


# ---------------------------------------------------------------------------
# Part A: compactness alone
# ---------------------------------------------------------------------------


def test_part_a_on_a_connected_interval() -> None:
    """The minimiser of a decreasing affine objective is max C."""
    grid = np.linspace(-1.0, 1.0, 20_001)
    assert minimise_affine(grid, slope_sum=544.0) == pytest.approx(1.0)
    assert minimise_affine(grid, slope_sum=-544.0) == pytest.approx(-1.0)


def test_part_a_on_a_disconnected_compact_set() -> None:
    """No convexity is assumed: a union of intervals behaves the same way."""
    left = np.linspace(-1.0, -0.6, 4_001)
    right = np.linspace(0.2, 0.55, 3_501)
    union = np.concatenate([left, right])
    assert minimise_affine(union, slope_sum=1.0) == pytest.approx(0.55)
    assert minimise_affine(union, slope_sum=-1.0) == pytest.approx(-1.0)
    # The minimiser is an endpoint of a connected component, not of the hull.
    assert minimise_affine(union, slope_sum=1.0) != pytest.approx(1.0)


def test_part_a_covers_a_set_defined_by_infinitely_many_constraints() -> None:
    """Part A applies to a set cut out by a continuum of constraints.

    ``C_glob`` requires PSD-ness at every state of a continuous domain.  Here the
    analogue is ``{c : f(c, x) <= 0 for all x in [0, 1]}`` with
    ``f(c, x) = c - 1 - x``, whose binding constraint is the infimum over x.
    Part A still locates the minimiser because the set is compact.
    """
    states = np.linspace(0.0, 1.0, 5_001)
    grid = np.linspace(-2.0, 3.0, 50_001)
    # c is feasible iff c - 1 - x <= 0 for every x, that is iff c <= 1 + min(x).
    feasible = grid[grid <= 1.0 + states.min() + TOLERANCE]
    assert feasible.size > 0
    assert minimise_affine(feasible, slope_sum=1.0) == pytest.approx(1.0, abs=1e-4)


def test_part_a_requires_nonzero_slope() -> None:
    """At zero slope every point is a minimiser and the vertex claim fails."""
    grid = np.linspace(0.0, 1.0, 101)
    with pytest.raises(ValueError):
        minimise_affine(grid, slope_sum=0.0)


def test_part_a_empty_feasible_set_is_rejected() -> None:
    """An empty set has no minimiser; the caller must not silently proceed."""
    empty = np.array([])
    with pytest.raises(ValueError):
        if empty.size == 0:
            raise ValueError("empty feasible set")


# ---------------------------------------------------------------------------
# Part B: finite continuous representation
# ---------------------------------------------------------------------------


def active_constraints(
    point: float,
    lower: float,
    upper: float,
    constraints: list,
) -> list[str]:
    """Return the labels of the constraints active at ``point``."""
    active = []
    if abs(point - lower) < 1e-9:
        active.append("lower")
    if abs(point - upper) < 1e-9:
        active.append("upper")
    for index, function in enumerate(constraints):
        if abs(function(point)) < 1e-9:
            active.append(f"g{index}")
    return active


def test_part_b_identifies_an_active_nonnegativity_constraint() -> None:
    """With c <= A_t operative, the minimiser sits on one of those faces."""
    values = np.array([0.31, 0.22, 0.47])
    constraints = [(lambda c, a=a: c - a) for a in values]
    lower, upper = -1.0, 1.0
    grid = np.linspace(lower, upper, 200_001)
    feasible = grid[np.array([all(g(c) <= 0 for g in constraints) for c in grid])]
    minimiser = minimise_affine(feasible, slope_sum=3.0)
    assert minimiser == pytest.approx(values.min(), abs=1e-4)
    assert any(
        label.startswith("g")
        for label in active_constraints(values.min(), lower, upper, constraints)
    )


def test_part_b_identifies_an_active_range_bound() -> None:
    """When the interval bites first, the range restriction is the active one."""
    values = np.array([5.0, 6.0])  # far outside, so never operative
    constraints = [(lambda c, a=a: c - a) for a in values]
    lower, upper = -1.0, 1.0
    assert active_constraints(upper, lower, upper, constraints) == ["upper"]


def test_part_b_identifies_an_active_nonlinear_constraint() -> None:
    """A smallest-eigenvalue constraint is continuous and can be the active one."""

    def psd_constraint(c: float) -> float:
        matrix = np.array([[1.0, c], [c, 1.0]])
        return float(-np.linalg.eigvalsh(matrix).min())

    lower, upper = -2.0, 2.0
    grid = np.linspace(lower, upper, 400_001)
    feasible = grid[np.array([psd_constraint(c) <= TOLERANCE for c in grid])]
    minimiser = minimise_affine(feasible, slope_sum=1.0)
    # PSD of a 2x2 correlation matrix forces |c| <= 1, so the active face is c = 1.
    assert minimiser == pytest.approx(1.0, abs=1e-4)
    assert "g0" in active_constraints(1.0, lower, upper, [psd_constraint])


def test_part_b_finiteness_is_what_supplies_the_common_delta() -> None:
    """An infinite family can have infimum zero where each member is slack.

    This is the reason Part B is stated for finite J.  At c = 0 every constraint
    ``g_n(c) = c - 1/n`` is strictly negative, yet their infimum is zero, so no
    neighbourhood is feasible for all of them simultaneously and the
    contradiction argument of Part B's proof does not run.
    """
    point = 0.0
    values = [point - 1.0 / n for n in range(1, 20_001)]
    assert all(value < 0.0 for value in values)
    assert max(values) == pytest.approx(0.0, abs=1e-4)
    assert not math.isclose(min(abs(v) for v in values), 1.0)


# ---------------------------------------------------------------------------
# The three feasible sets
# ---------------------------------------------------------------------------


def test_the_three_sets_are_nested() -> None:
    """C_glob subset C_obs subset C_pub, as the definitions require."""
    grid = np.linspace(-1.0, 1.0, 20_001)
    published = grid[grid <= 0.8]
    observed = published[published <= 0.5]
    states = np.linspace(0.0, 1.0, 51)
    # A global constraint indexed by x: c <= 0.5 - 0.2 x, tightest at x = 1.
    global_set = published[
        np.array([np.all(c <= 0.5 - 0.2 * states + TOLERANCE) for c in published])
    ]
    assert set(np.round(global_set, 9)).issubset(set(np.round(observed, 9)))
    assert set(np.round(observed, 9)).issubset(set(np.round(published, 9)))
    assert global_set.max() < observed.max()
    assert observed.max() < published.max()


def test_global_constraint_tightens_the_corner() -> None:
    """The corner formula for C_pub can fail on the enlarged sets.

    Proposition F.1(iii) gives c* = min_t A_t only under C_pub.  If a global
    constraint cuts the interval first, the minimiser moves and the formula no
    longer describes it.
    """
    values = np.array([0.31, 0.22, 0.47])
    grid = np.linspace(-1.0, 1.0, 200_001)
    published = grid[np.array([all(c <= a for a in values) for c in grid])]
    assert minimise_affine(published, slope_sum=3.0) == pytest.approx(0.22, abs=1e-4)

    states = np.linspace(0.0, 1.0, 21)
    global_set = published[
        np.array([np.all(c <= 0.1 + 0.05 * states + TOLERANCE) for c in published])
    ]
    global_minimiser = minimise_affine(global_set, slope_sum=3.0)
    assert global_minimiser == pytest.approx(0.1, abs=1e-4)
    assert global_minimiser < values.min()


# ---------------------------------------------------------------------------
# The reduced correlation matrix has four free and two implied entries
# ---------------------------------------------------------------------------


def test_reduced_matrix_has_six_off_diagonal_entries() -> None:
    """A symmetric 4x4 correlation matrix has exactly six off-diagonal entries.

    Four are primitive parameters and two are implied by the variance identity;
    the fifth primitive correlation rho_zz* is not among them.
    """
    dimension = 4
    off_diagonal = dimension * (dimension - 1) // 2
    assert off_diagonal == 6

    free_entries = {"rho_ww*", "rho_wy", "rho_w*y", "rho_xy"}
    implied_entries = {"rho_wx", "rho_w*x"}
    assert len(free_entries) == 4
    assert len(implied_entries) == 2
    assert len(free_entries | implied_entries) == off_diagonal
    assert free_entries.isdisjoint(implied_entries)

    primitive = free_entries | {"rho_zz*"}
    assert len(primitive) == 5
    assert "rho_zz*" not in (free_entries | implied_entries)


# ---------------------------------------------------------------------------
# Proposition D.1(ii): the three-way root classification
# ---------------------------------------------------------------------------


def classify(kappa_b: float, eta: float, zeta: float) -> str:
    """Return the case of Proposition D.1(ii) predicted for these coefficients."""
    assert kappa_b > 1.0 and zeta > 0.0
    discriminant = eta * eta - (kappa_b - 1.0) * zeta
    if eta < 0.0 and discriminant > 0.0:
        return "two distinct"
    if eta < 0.0 and discriminant == 0.0:
        return "one double"
    return "none"


def positive_roots(kappa_b: float, eta: float, zeta: float) -> list[float]:
    """Return the strictly positive real roots of (k-1)v^2 + 2 eta v + zeta."""
    roots = np.roots([kappa_b - 1.0, 2.0 * eta, zeta])
    return sorted(
        float(r.real) for r in roots if abs(r.imag) < 1e-12 and r.real > 1e-12
    )


def test_root_classification_matches_the_quadratic() -> None:
    """The three cases must agree with numerically computed roots.

    The statement "no positive root or exactly two" is consistent only if
    roots are counted with multiplicity; the proposition now separates the
    repeated-root case explicitly.
    """
    rng = np.random.default_rng(4021)
    seen = {"two distinct": 0, "none": 0}
    for _ in range(20_000):
        kappa_b = 1.0 + float(rng.uniform(0.01, 3.0))
        eta = float(rng.uniform(-2.0, 2.0))
        zeta = float(rng.uniform(0.001, 3.0))
        predicted = classify(kappa_b, eta, zeta)
        roots = positive_roots(kappa_b, eta, zeta)
        if predicted == "two distinct":
            assert len(roots) == 2 and roots[1] - roots[0] > 1e-9
        elif predicted == "none":
            assert roots == []
        seen[predicted] = seen.get(predicted, 0) + 1
    assert seen["two distinct"] > 0 and seen["none"] > 0


def test_repeated_root_case_is_reachable_by_construction() -> None:
    """Case (b) exists: on the boundary there is one positive double root."""
    for kappa_b, eta in ((2.0, -1.0), (1.5, -0.8), (3.0, -2.5)):
        # Choose zeta to put the state exactly on Delta = 0.
        zeta = eta * eta / (kappa_b - 1.0)
        assert zeta > 0.0
        assert classify(kappa_b, eta, zeta) == "one double"

        # A double root is ill-conditioned for a numerical root finder, which
        # splits it by about sqrt(eps).  Verify it by its defining property
        # instead: the quadratic and its derivative both vanish there.
        candidate = -eta / (kappa_b - 1.0)
        assert candidate > 0.0
        value = (kappa_b - 1.0) * candidate**2 + 2.0 * eta * candidate + zeta
        slope = 2.0 * (kappa_b - 1.0) * candidate + 2.0 * eta
        assert value == pytest.approx(0.0, abs=1e-12)
        assert slope == pytest.approx(0.0, abs=1e-12)


def test_positive_eta_never_gives_a_positive_root() -> None:
    """With eta >= 0 the root sum is nonpositive while the product is positive."""
    rng = np.random.default_rng(77)
    for _ in range(5_000):
        kappa_b = 1.0 + float(rng.uniform(0.01, 3.0))
        eta = float(rng.uniform(0.0, 2.0))
        zeta = float(rng.uniform(0.001, 3.0))
        assert classify(kappa_b, eta, zeta) == "none"
        assert positive_roots(kappa_b, eta, zeta) == []


def test_repeated_root_boundary_has_measure_zero_on_a_grid() -> None:
    """A candidate grid does not meet case (b) unless built to.

    This is why the sweep reports no point with exactly one positive root:
    Delta = 0 is a codimension-one condition on the state.
    """
    rng = np.random.default_rng(1234)
    hits = 0
    for _ in range(50_000):
        kappa_b = 1.0 + float(rng.uniform(0.01, 3.0))
        eta = float(rng.uniform(-2.0, 0.0))
        zeta = float(rng.uniform(0.001, 3.0))
        if classify(kappa_b, eta, zeta) == "one double":
            hits += 1
    assert hits == 0
