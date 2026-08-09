"""Generate figures and tables for the simulated-likelihood manuscript.

The experiments are deliberately reproducible and focus on quantities for which
closed-form benchmarks are available.  No external data are required.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import integrate
from scipy.spatial import cKDTree
from scipy.special import gamma as gamma_function
from scipy.special import logsumexp
from scipy.stats import chi, chi2, ncx2, norm

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
FIGURES = PAPER / "figures"
TABLES = PAPER / "tables"
SEED = 20260726


def set_output_root(root: Path) -> None:
    """Redirect figure and table output, so `make verify` can write elsewhere."""
    global FIGURES, TABLES
    FIGURES = root / "figures"
    TABLES = root / "tables"
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def save_figure(fig: "plt.Figure", stem: str) -> None:
    """Write a figure as PDF and PNG with no embedded creation timestamp.

    Matplotlib stamps a CreationDate into PDF output and a Software tag into
    PNG output by default, which makes otherwise identical rebuilds differ
    byte for byte and defeats any hash-based reproducibility check.
    """
    fig.savefig(FIGURES / f"{stem}.pdf", metadata={"CreationDate": None})
    fig.savefig(FIGURES / f"{stem}.png", dpi=220, metadata={"Software": None})


def true_brownian_density_at_origin(dimension: int) -> float:
    """Return the unit-time standard Brownian transition density at zero."""
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    return (2.0 * math.pi) ** (-dimension / 2.0)


def brownian_second_moment(dimension: int, m_steps: int) -> float:
    """Return the exact second moment of one Pedersen endpoint summand.

    The interval has unit length, ``h = 1 / m_steps``, the start and endpoint
    are both zero, and the diffusion is standard Brownian motion in R^K.
    """
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    if m_steps < 2:
        raise ValueError("m_steps must be at least 2")
    h = 1.0 / float(m_steps)
    return (
        (2.0 * math.pi) ** (-dimension)
        * h ** (-dimension / 2.0)
        * (2.0 - h) ** (-dimension / 2.0)
    )


def brownian_estimator_variance(
    dimension: int,
    m_steps: int,
    simulations: int,
) -> float:
    """Return the exact variance of the sample-average density estimator."""
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    q = true_brownian_density_at_origin(dimension)
    return (brownian_second_moment(dimension, m_steps) - q * q) / simulations


def simulate_brownian_estimator(
    *,
    dimension: int,
    m_steps: int,
    simulations: int,
    replications: int,
    rng: np.random.Generator,
    target_draws_per_batch: int = 2_000_000,
) -> NDArray[np.float64]:
    """Simulate independent replications of the endpoint density estimator.

    The implementation uses log-sum-exp to remain stable when most endpoint
    kernels are extremely small and a few are very large.
    """
    if min(dimension, m_steps, simulations, replications) <= 0:
        raise ValueError("all integer arguments must be positive")
    if m_steps < 2:
        raise ValueError("m_steps must be at least 2")

    h = 1.0 / float(m_steps)
    z_scale = math.sqrt(1.0 - h)
    log_prefactor = -(dimension / 2.0) * math.log(2.0 * math.pi * h)
    batch_replications = max(1, target_draws_per_batch // simulations)
    estimates = np.empty(replications, dtype=np.float64)

    start = 0
    while start < replications:
        stop = min(replications, start + batch_replications)
        current = stop - start
        z = rng.normal(
            loc=0.0,
            scale=z_scale,
            size=(current, simulations, dimension),
        )
        squared_norm = np.einsum("rsk,rsk->rs", z, z, optimize=True)
        log_kernel = log_prefactor - squared_norm / (2.0 * h)
        log_estimate = logsumexp(log_kernel, axis=1) - math.log(simulations)
        estimates[start:stop] = np.exp(log_estimate)
        start = stop

    return estimates


def make_variance_scaling_figure() -> None:
    """Plot the exact dimension-dependent variance scaling."""
    m_values = np.array([2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=int)
    dimensions = [1, 2, 4, 8]

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for dimension in dimensions:
        scaled = np.array(
            [
                brownian_second_moment(dimension, int(m))
                * (1.0 / float(m)) ** (dimension / 2.0)
                for m in m_values
            ]
        )
        limit = (2.0 * math.pi) ** (-dimension) * 2.0 ** (-dimension / 2.0)
        ax.plot(m_values, scaled / limit, marker="o", label=fr"$K={dimension}$")

    ax.axhline(1.0, linestyle="--", linewidth=1.0)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Euler substeps $M$")
    ax.set_ylabel(r"$h^{K/2}\,\mathbb{E}[G_{M}^{2}]$ divided by its limit")
    ax.set_title("Local second-moment scaling of the endpoint estimator")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    save_figure(fig, "brownian_second_moment_scaling")
    plt.close(fig)


def make_path_rmse_figure() -> None:
    """Plot exact relative RMSE under three joint asymptotic paths."""
    dimension = 4
    m_values = np.array([4, 8, 16, 32, 64, 128, 256, 512], dtype=int)
    q = true_brownian_density_at_origin(dimension)
    paths = {
        r"$S=M$": lambda m: m,
        r"$S=M^2$": lambda m: m**2,
        r"$S=M^3$": lambda m: m**3,
    }

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for label, rule in paths.items():
        rel_rmse = []
        for m in m_values:
            variance = brownian_estimator_variance(dimension, int(m), int(rule(int(m))))
            rel_rmse.append(math.sqrt(variance) / q)
        ax.plot(m_values, rel_rmse, marker="o", label=label)

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Euler substeps $M$")
    ax.set_ylabel("Exact relative RMSE")
    ax.set_title("Four-dimensional Brownian motion: joint-rate comparison")
    ax.legend()
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    save_figure(fig, "brownian_joint_path_rmse")
    plt.close(fig)


def make_subcritical_distribution_results(rng: np.random.Generator) -> None:
    """Simulate the counterexample path M=S in four dimensions."""
    dimension = 4
    q = true_brownian_density_at_origin(dimension)
    m_values = [8, 16, 32, 64, 128, 256, 512]
    rows: list[dict[str, float | int]] = []

    for m in m_values:
        # A fixed replication count across rows, not a fixed draw budget.
        # The quantiles are what the table is for, and a budget that falls with
        # M estimates them worst exactly where the collapse is sharpest; the
        # mean needs no draws at all, being exactly p by Proposition 3.1.
        replications = 20_000
        estimates = simulate_brownian_estimator(
            dimension=dimension,
            m_steps=m,
            simulations=m,
            replications=replications,
            rng=rng,
        )
        relative = estimates / q
        # The mean is carried by rare large draws, so its Monte Carlo standard
        # error is reported alongside it: without one the value 0.998 at the
        # finest step reads as far more precise than it is.
        mean_standard_error = float(
            np.std(relative, ddof=1) / math.sqrt(replications)
        )
        rows.append(
            {
                "M": m,
                "S": m,
                "replications": replications,
                "mean_relative": float(np.mean(relative)),
                "mean_standard_error": mean_standard_error,
                "median_relative": float(np.median(relative)),
                "q10_relative": float(np.quantile(relative, 0.10)),
                "q90_relative": float(np.quantile(relative, 0.90)),
                "prob_below_half": float(np.mean(relative < 0.5)),
                "prob_within_25pct": float(np.mean(np.abs(relative - 1.0) <= 0.25)),
            }
        )

    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "brownian_subcritical_path.csv", index=False)
    (TABLES / "brownian_subcritical_path.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4g}",
            escape=False,
            column_format="rrrrrrrrr",
        ),
        encoding="utf-8",
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(frame["M"], frame["median_relative"], marker="o", label="Median")
    ax.fill_between(
        frame["M"].to_numpy(dtype=float),
        frame["q10_relative"].to_numpy(dtype=float),
        frame["q90_relative"].to_numpy(dtype=float),
        alpha=0.2,
        label="10th-90th percentiles",
    )
    ax.axhline(1.0, linestyle="--", linewidth=1.0, label="True density")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("$M=S$")
    ax.set_ylabel("Estimator divided by the true density")
    ax.set_title("Counterexample path: typical estimates collapse to zero")
    ax.legend()
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    save_figure(fig, "brownian_subcritical_distribution")
    plt.close(fig)


def ou_preterminal_variance(m_steps: int, mean_reversion: float = 1.0) -> float:
    """Variance of the Euler OU state after M-1 substeps, from zero."""
    if m_steps < 2:
        raise ValueError("m_steps must be at least 2")
    h = 1.0 / float(m_steps)
    coefficient = 1.0 - mean_reversion * h
    if math.isclose(abs(coefficient), 1.0):
        return h * (m_steps - 1)
    return h * (1.0 - coefficient ** (2 * (m_steps - 1))) / (1.0 - coefficient**2)


def ou_second_moment(
    dimension: int,
    m_steps: int,
    mean_reversion: float = 1.0,
) -> float:
    """Exact second moment for the endpoint estimator of a diagonal OU model."""
    h = 1.0 / float(m_steps)
    coefficient = 1.0 - mean_reversion * h
    variance_z = ou_preterminal_variance(m_steps, mean_reversion)
    factor = 1.0 + 2.0 * variance_z * coefficient**2 / h
    return (2.0 * math.pi * h) ** (-dimension) * factor ** (-dimension / 2.0)


def make_ou_scaling_figure() -> None:
    """Show that the same second-moment law holds for a nontrivial OU drift."""
    dimension = 4
    mean_reversion = 1.0
    m_values = np.array([2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=int)
    exact_variance_t1 = (1.0 - math.exp(-2.0 * mean_reversion)) / (2.0 * mean_reversion)
    q_exact = (2.0 * math.pi * exact_variance_t1) ** (-dimension / 2.0)
    limiting_constant = (4.0 * math.pi) ** (-dimension / 2.0) * q_exact

    ratios = []
    for m in m_values:
        h = 1.0 / float(m)
        ratios.append(
            h ** (dimension / 2.0) * ou_second_moment(dimension, int(m)) / limiting_constant
        )

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(m_values, ratios, marker="o")
    ax.axhline(1.0, linestyle="--", linewidth=1.0)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Euler substeps $M$")
    ax.set_ylabel("Scaled second moment divided by its diffusion limit")
    ax.set_title("Four-dimensional Ornstein-Uhlenbeck benchmark")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    save_figure(fig, "ou_second_moment_scaling")
    plt.close(fig)


def euler_negative_probability(
    state: NDArray[np.float64],
    *,
    alpha: float,
    beta: float,
    h: float,
) -> NDArray[np.float64]:
    """Probability that one Euler step for H = epsilon^2 becomes negative.

    The process is dH = (beta^2 - 2 alpha H) dt + 2 beta sqrt(H) dY, so from
    H_t = x the Euler update is Gaussian with mean x + (beta^2 - 2 alpha x) h
    and standard deviation 2 beta sqrt(x h).  The state is written H rather
    than X because X already denotes the Brownian motion driving the log
    exchange rate in the application.
    """
    if alpha <= 0.0 or beta <= 0.0 or h <= 0.0:
        raise ValueError("alpha, beta, and h must be positive")
    state = np.asarray(state, dtype=np.float64)
    if np.any(state < 0.0):
        raise ValueError("the state must be nonnegative")
    mean = state + (beta**2 - 2.0 * alpha * state) * h
    sd = 2.0 * beta * np.sqrt(state * h)
    probability = np.zeros_like(state)
    positive_sd = sd > 0.0
    probability[positive_sd] = norm.cdf(-mean[positive_sd] / sd[positive_sd])
    probability[~positive_sd] = (mean[~positive_sd] < 0.0).astype(float)
    return probability


# Weekly observations with M = 10 Euler substeps give h = 1/520; doubling M
# gives h = 1/1040.  The coarser value is retained only as a labelled
# illustration of how the curve moves with the step size.
APPLICATION_STEPS = ((1.0 / 520.0, "$h=1/520$ (weekly, $M=10$)"),
                     (1.0 / 1040.0, "$h=1/1040$ ($M=20$)"),
                     (0.02, "$h=0.02$ (illustration)"))

INCOMPLETENESS_PARAMETERS = {
    "U.S.-U.K.": (0.320, 0.088),
    "U.S.-Germany": (0.338, 0.101),
}


def make_boundary_probability_figure() -> None:
    """Plot Euler boundary-violation probabilities at application step sizes."""
    state_values = np.logspace(-10, -1.2, 800)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for (label, (alpha, beta)), style in zip(
        INCOMPLETENESS_PARAMETERS.items(), ("-", "--")
    ):
        for (h, step_label), colour in zip(APPLICATION_STEPS, ("C0", "C1", "C2")):
            probability = euler_negative_probability(
                state_values, alpha=alpha, beta=beta, h=h
            )
            ax.plot(
                state_values,
                probability,
                style,
                color=colour,
                linewidth=1.4,
                label=f"{label}, {step_label}",
            )

    ax.set_xscale("log")
    ax.set_xlabel(r"Current state $H_t=\epsilon_t^2$")
    ax.set_ylabel("One-step probability of a negative Euler state")
    ax.set_ylim(0.0, 0.55)
    ax.set_title("Ordinary Euler discretisation is not positivity preserving")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    save_figure(fig, "epsilon_squared_euler_negative_probability")
    plt.close(fig)


def worst_case_boundary(alpha: float, beta: float, h: float) -> tuple[float, float]:
    """Return the exact maximiser and maximum of the negativity probability.

    Proposition C.1: for alpha > 0, beta > 0 and h < 1/(2 alpha),

        argmax = beta^2 h / (1 - 2 alpha h),
        max    = Phi(-sqrt(1 - 2 alpha h)).
    """
    if alpha <= 0.0 or beta <= 0.0:
        raise ValueError("alpha and beta must be positive")
    if not 0.0 < h < 1.0 / (2.0 * alpha):
        raise ValueError("h must lie in (0, 1/(2 alpha))")
    a = 1.0 - 2.0 * alpha * h
    return beta**2 * h / a, float(norm.cdf(-math.sqrt(a)))


def make_boundary_maximum_table() -> None:
    """Tabulate the exact worst case of the one-step Euler violation."""
    rows = []
    for label, (alpha, beta) in INCOMPLETENESS_PARAMETERS.items():
        for h, _ in APPLICATION_STEPS:
            argmax, maximum = worst_case_boundary(alpha, beta, h)
            rows.append(
                {
                    "system": label,
                    "h": h,
                    "argmax_state": argmax,
                    "argmax_epsilon": math.sqrt(argmax),
                    "max_probability": maximum,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "boundary_maximum.csv", index=False)
    (TABLES / "boundary_maximum.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="lrrrr",
        ),
        encoding="utf-8",
    )


# Table 3 estimates for the two square-root interest-rate processes in each
# system: (label, kappa, theta, sigma).
CIR_RATES = (
    ("U.S. (vs. U.K.)", 0.284, 0.053, 0.028),
    ("U.K.", 0.486, 0.074, 0.056),
    ("U.S. (vs. Germany)", 0.305, 0.058, 0.027),
    ("Germany", 0.088, 0.064, 0.042),
)


def cir_negativity(kappa: float, theta: float, sigma: float, state: float, h: float) -> dict:
    """Return the one-step Euler negativity diagnostics for a CIR state.

    Gaussian increments have full support, so this probability is strictly
    positive from every state.  It is reported as a z-score and a base-ten
    logarithm because direct evaluation of the tail underflows to zero in
    double precision well before it becomes zero in fact.
    """
    if state <= 0.0:
        raise ValueError("the state must be strictly positive")
    mean = state + kappa * (theta - state) * h
    sd = sigma * math.sqrt(state * h)
    z = mean / sd
    return {
        "z_score": z,
        "log10_probability": float(norm.logcdf(-z) / math.log(10.0)),
        "probability": float(norm.cdf(-z)),
        "underflows": bool(norm.cdf(-z) == 0.0),
    }


def make_cir_negativity_table() -> None:
    """Quantify the interest-rate boundary probabilities at h = 1/520."""
    h = 1.0 / 520.0
    rows = []
    for label, kappa, theta, sigma in CIR_RATES:
        for state_label, state in (
            ("long-run mean", theta),
            ("half the mean", 0.5 * theta),
            ("1 per cent", 0.01),
            ("0.1 per cent", 0.001),
        ):
            diagnostics = cir_negativity(kappa, theta, sigma, state, h)
            rows.append(
                {
                    "process": label,
                    "state_label": state_label,
                    "state": state,
                    "feller_ratio": 2.0 * kappa * theta / sigma**2,
                    **diagnostics,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "cir_negativity.csv", index=False)
    (TABLES / "cir_negativity.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4g}",
            escape=False,
            column_format="llrrrrrc",
        ),
        encoding="utf-8",
    )


def make_implicit_volatility_table() -> None:
    """Calculate the leading quadratic coefficient in the volatility identity."""
    rows = [
        {
            "market": "U.S. vs. U.K.",
            "beta": 1.514,
            "beta_star": 2.581,
            "rho": 0.89,
        },
        {
            "market": "U.S. vs. Germany",
            "beta": -0.142,
            "beta_star": 0.127,
            "rho": 0.94,
        },
    ]
    for row in rows:
        beta = float(row["beta"])
        beta_star = float(row["beta_star"])
        rho = float(row["rho"])
        kappa = beta**2 + beta_star**2 - 2.0 * rho * beta * beta_star
        row["kappa"] = kappa
        row["one_minus_kappa"] = 1.0 - kappa

    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "implicit_volatility_coefficients.csv", index=False)
    (TABLES / "implicit_volatility_coefficients.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="lrrrrr",
        ),
        encoding="utf-8",
    )


def make_feller_table() -> None:
    """Feller ratios for the square-root states, at the published estimates.

    For dZ = kappa (theta - Z) dt + sigma sqrt(Z) dB the origin is unattainable
    if and only if 2 kappa theta / sigma^2 >= 1.  The incompleteness state
    X = epsilon^2 implied by an Ornstein-Uhlenbeck epsilon has kappa = 2 alpha,
    theta = beta^2 / (2 alpha) and sigma = 2 beta, so its ratio is exactly 1/2
    for every admissible (alpha, beta).
    """
    rows = []
    for system, alpha, beta, rates in (
        (
            "U.S. vs. U.K.",
            0.320,
            0.088,
            (("r (U.S.)", 0.284, 0.053, 0.028), ("r* (U.K.)", 0.486, 0.074, 0.056)),
        ),
        (
            "U.S. vs. Germany",
            0.338,
            0.101,
            (("r (U.S.)", 0.305, 0.058, 0.027), ("r* (Germany)", 0.088, 0.064, 0.042)),
        ),
    ):
        for name, kappa, theta, sigma in rates:
            rows.append(
                {
                    "system": system,
                    "state": name,
                    "kappa": kappa,
                    "theta": theta,
                    "sigma": sigma,
                    "feller_ratio": 2.0 * kappa * theta / sigma**2,
                }
            )
        kappa_x = 2.0 * alpha
        theta_x = beta**2 / (2.0 * alpha)
        sigma_x = 2.0 * beta
        rows.append(
            {
                "system": system,
                "state": "epsilon^2",
                "kappa": kappa_x,
                "theta": theta_x,
                "sigma": sigma_x,
                "feller_ratio": 2.0 * kappa_x * theta_x / sigma_x**2,
            }
        )

    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "feller_conditions.csv", index=False)
    (TABLES / "feller_conditions.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="llrrrr",
        ),
        encoding="utf-8",
    )


def make_design_table() -> None:
    """Finite-sample scaling ratios for the implemented design and variations.

    These are diagnostics, not tests.  A single finite triple (N, M, S) can
    neither satisfy nor violate a limit; what the ratios show is whether the
    implementation sits in a regime resembling the asymptotic ordering that
    Theorem 2 of Brandt and Santa-Clara (2002) describes, namely
    sqrt(S)/M -> 0 together with N / S^(1/4) -> 0.

    The reported estimation uses N = 544 weekly observations, M = 10 Euler
    substeps and S = 5,000 simulations, plus 5,000 antithetic variates.  The
    antithetic draws are a variance-reduction device and are perfectly
    negatively dependent with their partners, so they are not counted as
    independent simulations here.

    Note the arithmetic of the effective endpoint size in K = 4, where
    R(M, S) = S / M^2:  doubling both M and S gives R(2M, 2S) = R(M, S) / 2,
    doubling M alone gives R(M, S) / 4, and holding R fixed while doubling M
    requires quadrupling S.
    """
    n_obs = 544
    scenarios = (
        ("Implemented", 10, 5_000),
        ("Double M and S", 20, 10_000),
        ("Double M, S fixed", 20, 5_000),
        ("Double M, quadruple S", 20, 20_000),
    )
    rows = []
    for label, m_steps, simulations in scenarios:
        rows.append(
            {
                "scenario": label,
                "N": n_obs,
                "M": m_steps,
                "S": simulations,
                "effective_size_K4": simulations / m_steps**2,
                # The antithetic reading of the same design.  With P = S pairs
                # the evaluation count is 2P, and N_eff = 2P/(1 + rho_A), so the
                # effective size doubles as the pair correlation falls to zero.
                # These three columns are quoted in the manuscript table and so
                # must be generated rather than computed by hand.
                "evaluations": 2 * simulations,
                "effective_size_rho_one": simulations / m_steps**2,
                "effective_size_rho_zero": 2 * simulations / m_steps**2,
                "sqrt_S_over_M": math.sqrt(simulations) / m_steps,
                "N_over_S_quarter": n_obs / simulations**0.25,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "implemented_design.csv", index=False)
    (TABLES / "implemented_design.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4g}",
            escape=False,
            column_format="lrrrrrr",
        ),
        encoding="utf-8",
    )


def make_rate_table() -> None:
    """Create a compact table of the principal rate conditions."""
    rows = [
        {
            "property": "Monte Carlo L2 consistency",
            "general_K": r"$S/M^{K/2}\to\infty$",
            "K4": r"$S/M^2\to\infty$",
        },
        {
            "property": "Density CLT centred at Euler density",
            "general_K": r"$S/M^{K/2}\to\infty$",
            "K4": r"$S/M^2\to\infty$",
        },
        {
            "property": "Euler bias negligible in density CLT",
            "general_K": r"$\sqrt{S}/M^{1+K/4}\to0$",
            "K4": r"$S/M^4\to0$",
        },
        {
            "property": "Published condition",
            "general_K": r"$\sqrt{S}/M\to0$",
            "K4": r"$S/M^2\to0$",
        },
        {
            "property": "Published parameter condition",
            "general_K": r"$N/S^{1/4}\to0$",
            "K4": r"$N/S^{1/4}\to0$",
        },
    ]
    frame = pd.DataFrame(rows)
    (TABLES / "rate_conditions.tex").write_text(
        frame.to_latex(index=False, escape=False, column_format="lll"),
        encoding="utf-8",
    )
    frame.to_csv(TABLES / "rate_conditions.csv", index=False)


def make_literature_comparison_table() -> None:
    """Write the claim-by-claim comparison with Detemple, Garcia and Rindisbacher.

    The content is a fixed audit result rather than a computation, but it is
    generated here so that the committed CSV and LaTeX cannot drift from one
    another and so that `make verify` covers them.  See
    docs/detemple_overlap_audit.md for the supporting quotations.
    """
    rows = [
        ("Endpoint density is a Gaussian kernel with bandwidth sqrt(h)",
         "Transition-density estimator interpreted as a kernel estimator on simulated iid data",
         "p.32, citing Milstein-Schoenmakers-Spokoiny", "identical",
         "no longer called the central observation; attributed"),
        ("Optimal M ~ S^{2/(K+4)}, MSE ~ S^{-4/(K+4)}",
         "Score rate M^{-2/(d+4)}, dimension dependent",
         "p.32; footnote 28 p.30", "same rate family, different object",
         "exponent attributed; contribution restricted to exact constants"),
        ("Bias-variance trade-off gives an optimal allocation",
         "sqrt(L)/M^{2/(d+4)} -> e1 and M^{2/(d+4)}/N -> e2",
         "p.32", "prior work", "listed as prior work"),
        ("The published rate condition is inadequate",
         "These authors assume e2=0; this assumption is not sufficient",
         "p.32, naming Pedersen and Brandt-Santa-Clara", "prior work",
         "attributed; claim narrowed to the counterexample"),
        ("Joint limits in data, discretisation and simulation",
         "Joint limits in L, M, N throughout", "sections 3 and 5.2", "prior work",
         "listed as prior work"),
        ("Effective simulation size is S/M^{K/2}", "not stated", "-",
         "conceptually related only", "retained, with the kernel view attributed"),
        ("Exact finite-M Brownian moments of all orders", "not present", "-",
         "no overlap", "retained as new"),
        ("Exact local moment constant c_{r,K}", "not present", "-", "no overlap",
         "retained as new"),
        ("Collapse in probability along M=S", "not present; their negative result is exploding second-order bias",
         "-", "no overlap", "retained as new"),
        ("Direct refutation of Lemmas 2 and 3", "not present", "-", "no overlap",
         "retained as new"),
        ("Exact four-dimensional incompatibility",
         "weaker statement that the condition is not sufficient", "p.32",
         "stronger in the manuscript", "retained, weaker prior claim attributed"),
        ("Analysis of the exchange-rate application", "not present", "-", "no overlap",
         "retained as new"),
    ]
    frame = pd.DataFrame(
        rows,
        columns=["manuscript_claim", "detemple_counterpart", "location", "overlap", "correction"],
    )
    frame.to_csv(TABLES / "literature_comparison.csv", index=False)
    (TABLES / "literature_comparison.tex").write_text(
        frame[["manuscript_claim", "detemple_counterpart", "location", "overlap"]].to_latex(
            index=False, escape=True, column_format="p{3.2cm}p{3.2cm}p{2.0cm}p{2.2cm}"
        ),
        encoding="utf-8",
    )


def make_correlation_tables() -> None:
    """Write the four-dimensional Brownian correlation audit.

    Delegates to ``check_correlation_matrix`` so that the manuscript tables and
    the standalone audit tool cannot drift apart.  The perturbation study is
    run with a reduced draw count here; the standalone tool defaults higher.
    """
    import check_correlation_matrix as ccm

    states = ccm.run_state_audit()
    states.to_csv(TABLES / "correlation_audit.csv", index=False)
    columns = ["system", "state", "feasible", "max_abs_off_diagonal", "min_eigenvalue"]
    (TABLES / "correlation_audit.tex").write_text(
        states[columns].to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="llcrr",
        ),
        encoding="utf-8",
    )

    time_varying = ccm.run_time_varying_audit()
    time_varying.to_csv(TABLES / "time_varying_feasibility.csv", index=False)

    sensitivity = ccm.run_grid_sensitivity()
    sensitivity.to_csv(TABLES / "grid_sensitivity.csv", index=False)
    display = pd.DataFrame(
        {
            "Design": sensitivity["design"],
            "Rates": sensitivity["rate_values"],
            "Spacing": sensitivity["rate_spacing"],
            "$e$ values": sensitivity["fx_values"],
            "$|e|\\le$": sensitivity["fx_range"],
            "$\\epsilon^2$ levels": sensitivity["epsilon_levels"],
            "Points": sensitivity["candidate_points"],
            "No root": sensitivity["no_positive_root"],
            "One": sensitivity["one_positive_root"],
            "Two": sensitivity["two_positive_roots"],
            "Matrices": sensitivity["branch_matrices"],
            "$\\min\\lambda_{\\min}$": sensitivity["worst_min_eigenvalue"],
        }
    )
    (TABLES / "grid_sensitivity.tex").write_text(
        display.to_latex(
            index=False,
            float_format=lambda value: f"{value:.4f}",
            escape=False,
            column_format="lrlrrrrrrrrr",
        ),
        encoding="utf-8",
    )

    perturbation = ccm.run_perturbation_audit(draws=5_000)
    perturbation.to_csv(TABLES / "correlation_perturbation.csv", index=False)

    search = ccm.search_for_infeasible_psd_violation()
    search.to_csv(TABLES / "correlation_feasible_search.csv", index=False)



# ---------------------------------------------------------------------------
# The nearest-neighbour limit behind the argmax appendix.
#
# Direct simulation is the wrong instrument here: convergence is slow enough
# that 5,000 draws reach only 89 per cent of the limit.  But the quantity is a
# pair of one-dimensional integrals, because the conditional distribution of the
# distance from theta to one atom is a noncentral chi-squared in closed form.
# Quadrature therefore reaches any S, and the whole table is deterministic.
# ---------------------------------------------------------------------------

NN_DIMENSIONS = ((4, 0.0), (4, 1.5), (6, 0.0), (3, 0.0))
NN_SIZES = (10.0**3, 10.0**5, 10.0**8, 10.0**12, 10.0**18)
NN_SIGMA2 = 1.0  # the h -> 0 limit of 1 - h


def unit_ball_volume(dimension: int) -> float:
    """Return the volume of the unit ball in the given dimension."""
    return math.pi ** (dimension / 2) / gamma_function(dimension / 2 + 1)


def nearest_neighbour_limit(dimension: int, offset: float) -> float:
    """Return the closed-form limit of S^{2/K} E[min_s ||theta - b_s||^2]."""
    return (
        2
        * math.pi
        * NN_SIGMA2
        * gamma_function(1 + 2 / dimension)
        * unit_ball_volume(dimension) ** (-2 / dimension)
        * (dimension * NN_SIGMA2 / (dimension * NN_SIGMA2 - 2)) ** (dimension / 2)
        * math.exp(offset**2 / (dimension * NN_SIGMA2 - 2))
    )


def _nn_conditional(dimension: int, m: float, size: float) -> float:
    """Return S^{2/K} E[rho^2 | m] by quadrature in the rescaled variable."""

    def integrand(w: float) -> float:
        if w <= 0.0:
            return 1.0
        radius2 = size ** (-2 / dimension) * w / NN_SIGMA2
        cdf = ncx2.cdf(radius2, dimension, m * m / NN_SIGMA2)
        if cdf >= 1.0:
            return 0.0
        return float(np.exp(size * np.log1p(-cdf)))

    density = (2 * math.pi * NN_SIGMA2) ** (-dimension / 2) * math.exp(
        -m * m / (2 * NN_SIGMA2)
    )
    scale = (unit_ball_volume(dimension) * max(density, 1e-300)) ** (-2 / dimension)
    total, _ = integrate.quad(integrand, 0.0, max(40.0 * scale, 40.0), limit=400)
    return total


def nearest_neighbour_expectation(dimension: int, offset: float, size: float) -> float:
    """Return S^{2/K} E[min_s ||theta - b_s||^2], averaged over the centre."""
    ncp = offset**2

    def integrand(m: float) -> float:
        weight = 2 * m * ncx2.pdf(m * m, dimension, ncp)
        if weight <= 0.0:
            return 0.0
        return weight * _nn_conditional(dimension, m, size)

    total, _ = integrate.quad(integrand, 0.0, 14.0, limit=400)
    return total


def make_nn_convergence_table() -> None:
    """Tabulate convergence to the nearest-neighbour limit."""
    rows = []
    for dimension, offset in NN_DIMENSIONS:
        target = nearest_neighbour_limit(dimension, offset)
        for size in NN_SIZES:
            value = nearest_neighbour_expectation(dimension, offset, size)
            rows.append(
                {
                    "dimension": dimension,
                    "offset": offset,
                    "log10_S": round(math.log10(size)),
                    "expectation": value,
                    "limit": target,
                    "ratio": value / target,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "nn_convergence.csv", index=False)
    (TABLES / "nn_convergence.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrr",
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# The collapse bound of the subcritical theorem.
#
# The theorem bounds P(qhat > eps) by C_K lam R^K + P(chi_K > R) / (eps pi^{K/2})
# for every R > 0.  Both terms are deterministic, so the table records the
# optimised bound alongside the exact exceedance probability, which is itself
# computable without simulation: every summand depends on the draw only through
# its distance to the target, so the count inside a ball is binomial and the
# radius inside it is a truncated chi-squared.
# ---------------------------------------------------------------------------

COLLAPSE_DIMENSION = 4
COLLAPSE_TRUNCATION = 12.0
COLLAPSE_REPLICATIONS = 4000


def collapse_bound(effective_size: float, threshold: float, dimension: int) -> tuple[float, float]:
    """Return the optimised collapse bound and the radius attaining it."""
    constant = 1.0 / gamma_function(dimension / 2 + 1)
    grid = np.linspace(0.5, 40.0, 8000)
    total = constant * effective_size * grid**dimension + chi.sf(grid, dimension) / (
        threshold * math.pi ** (dimension / 2)
    )
    index = int(np.argmin(total))
    return float(total[index]), float(grid[index])


def simulate_collapse(
    m_steps: int, draws: int, rng: np.random.Generator, dimension: int
) -> NDArray[np.float64]:
    """Return exact draws of the Brownian endpoint estimator at x = y = 0."""
    h = 1.0 / m_steps
    variance = 1.0 - h
    effective_size = draws * h ** (dimension / 2)
    cut = h * COLLAPSE_TRUNCATION**2 / variance
    inside = chi2.cdf(cut, dimension)

    counts = rng.binomial(draws, inside, size=COLLAPSE_REPLICATIONS)
    values = np.empty(COLLAPSE_REPLICATIONS)
    for index, count in enumerate(counts):
        if count == 0:
            values[index] = 0.0
            continue
        radii = chi2.ppf(rng.random(count) * inside, dimension)
        values[index] = float(np.sum(np.exp(-variance * radii / (2 * h))))
    return (2 * math.pi) ** (-dimension / 2) * values / effective_size


def make_collapse_bound_table(rng: np.random.Generator) -> None:
    """Compare the exact exceedance probability with the theorem's bound."""
    dimension = COLLAPSE_DIMENSION
    true_density = true_brownian_density_at_origin(dimension)
    threshold = true_density / 10
    rows = []
    for exponent in range(1, 8):
        m_steps = 10**exponent
        effective_size = 10.0 ** (-exponent)
        draws = int(round(effective_size * m_steps ** (dimension / 2)))
        values = simulate_collapse(m_steps, draws, rng, dimension)
        bound, radius = collapse_bound(effective_size, threshold, dimension)
        rows.append(
            {
                "m_steps": m_steps,
                "draws": draws,
                "effective_size": effective_size,
                "log_strengthened": effective_size * math.log(m_steps) ** (dimension / 2),
                "exceedance": float(np.mean(values > threshold)),
                "bound": bound,
                "radius": radius,
                "holds": bool(np.mean(values > threshold) <= bound),
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "collapse_bound.csv", index=False)
    (TABLES / "collapse_bound.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrrrl",
        ),
        encoding="utf-8",
    )



# ---------------------------------------------------------------------------
# How the uniform deviation of the nearest-atom criterion grows with S.
#
# The uniform-in-theta step turns on whether
#
#     sup_theta |X_N - E X_N|   scales like  S^{1/K}/sqrt(N)  or  sqrt(log S)/sqrt(N),
#
# the first implying a rate condition N >> S^{2/K} and the second only
# N >> log S.  The ratio of the sup deviation to the pointwise deviation cancels
# the 1/sqrt(N) and the scale of the summand, so it grows like S^{1/K} under the
# first reading and like sqrt((2/K) log S) under the second.
#
# Centring is the pooled mean across replications.  Exact centring by quadrature
# is available but needs millions of noncentral chi-squared evaluations per
# design; pooling shrinks the sup and pointwise deviations by the same factor,
# leaving the ratio unaffected.
# ---------------------------------------------------------------------------

UNIFORM_DIMENSION = 5
UNIFORM_GRID = np.linspace(0.0, 1.5, 21)
UNIFORM_SIZES = (10**2, 10**3, 10**4)
UNIFORM_OBSERVATIONS = 150
UNIFORM_REPLICATIONS = 10


def _uniform_criterion(size: int, rng: np.random.Generator) -> NDArray[np.float64]:
    """One draw of the scaled nearest-atom criterion on the theta grid."""
    dimension = UNIFORM_DIMENSION
    thetas = np.zeros((len(UNIFORM_GRID), dimension))
    thetas[:, 0] = UNIFORM_GRID
    total = np.zeros(len(UNIFORM_GRID))
    for _ in range(UNIFORM_OBSERVATIONS):
        centre = rng.normal(size=dimension)
        atoms = centre - rng.normal(size=(size, dimension))
        distances, _ = cKDTree(atoms).query(thetas, k=1)
        total += distances**2
    return size ** (2 / dimension) * total / UNIFORM_OBSERVATIONS


def make_uniform_scaling_table(rng: np.random.Generator) -> None:
    """Tabulate the sup and pointwise deviations against the two predictions."""
    dimension = UNIFORM_DIMENSION
    rows = []
    for size in UNIFORM_SIZES:
        draws = np.array(
            [_uniform_criterion(size, rng) for _ in range(UNIFORM_REPLICATIONS)]
        )
        deviations = draws - draws.mean(axis=0)
        sup_deviation = float(np.mean(np.max(np.abs(deviations), axis=1)))
        point_deviation = float(np.mean(np.abs(deviations[:, 0])))
        rows.append(
            {
                "simulations": size,
                "sup_deviation": sup_deviation,
                "pointwise_deviation": point_deviation,
                "ratio": sup_deviation / point_deviation,
                "power_prediction": size ** (1 / dimension),
                "log_prediction": math.sqrt(2 * math.log(size) / dimension),
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "uniform_scaling.csv", index=False)
    (TABLES / "uniform_scaling.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrr",
        ),
        encoding="utf-8",
    )



# ---------------------------------------------------------------------------
# The criterion's score at the truth, and why the estimator rate resists.
#
# The scaled nearest-atom criterion is differentiable wherever the nearest atom
# is unique, with grad psi_n(theta) = 2 S^{2/K} (theta - b_n*), and the whole
# configuration is spherically symmetric about theta_0.  So the score there is
# centred with
#
#     E ||grad X_N(theta_0)||^2 = 4 S^{2/K} G_S(theta_0) / N,
#
# exactly.  Turning that into a statement about the estimator needs the
# curvature of G_S, which converges to its limit far more slowly than G_S
# itself; the shape column below is what makes the asymptotic prediction
# unreachable by simulation.
# ---------------------------------------------------------------------------

# The check runs at K = 6, not at the application's K = 4.  The exact formula is
# dimension-free, but a Monte Carlo check of it is not: the sampling variance of
# an estimate of E||grad psi||^2 is governed by E[rho^4], which is finite only
# when K sigma^2 > 4.  At K = 4 that fails on the nose, so the estimate has
# infinite variance and agreement is noisy at any number of draws.  K = 6 puts
# the check safely inside the integrable region.
SCORE_DIMENSION = 6
SCORE_SIZES = (10**2, 10**3, 10**4)
SCORE_DRAWS = 6000
SHAPE_OFFSET = 1.5
SHAPE_SIZES = (10**2, 10**3, 10**4, 10**6, 10**10)


def make_score_moment_table(rng: np.random.Generator) -> None:
    """Check the exact score second moment against direct simulation."""
    dimension = SCORE_DIMENSION
    rows = []
    for size in SCORE_SIZES:
        expected_rho = nearest_neighbour_expectation(dimension, 0.0, float(size))
        predicted = 4 * size ** (2 / dimension) * expected_rho

        squared = np.empty(SCORE_DRAWS)
        for index in range(SCORE_DRAWS):
            centre = rng.normal(size=dimension)
            atoms = centre - rng.normal(size=(size, dimension))
            distances = np.einsum("sk,sk->s", atoms, atoms)
            nearest = atoms[int(np.argmin(distances))]
            gradient = -2 * size ** (2 / dimension) * nearest
            squared[index] = float(gradient @ gradient)

        simulated = float(np.mean(squared))
        rows.append(
            {
                "simulations": size,
                "expected_criterion": expected_rho,
                "predicted_moment": predicted,
                "simulated_moment": simulated,
                "ratio": simulated / predicted,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "score_moment.csv", index=False)
    (TABLES / "score_moment.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrr",
        ),
        encoding="utf-8",
    )


def make_criterion_shape_table() -> None:
    """Tabulate how slowly the criterion's shape approaches its limit.

    Computed at K = 4, the application dimension.  This table is pure
    quadrature, so the integrability boundary that forces the score check to
    K = 6 does not apply here.
    """
    dimension = 4
    limit_centre = nearest_neighbour_limit(dimension, 0.0)
    limit_offset = nearest_neighbour_limit(dimension, SHAPE_OFFSET)
    limit_curvature = 2 * limit_centre / (dimension - 2)
    rows = []
    for size in SHAPE_SIZES:
        centre = nearest_neighbour_expectation(dimension, 0.0, float(size))
        offset = nearest_neighbour_expectation(dimension, SHAPE_OFFSET, float(size))
        # The curvature itself, by the identity grad^2 G_S(theta_0) = (a_1 - a_0) I.
        curvature = central_chi_coefficient(
            dimension, 1, float(size)
        ) - central_chi_coefficient(dimension, 0, float(size))
        rows.append(
            {
                "simulations": size,
                "at_centre": centre,
                "at_offset": offset,
                "shape_ratio": offset / centre,
                "limit_shape_ratio": limit_offset / limit_centre,
                "fraction_of_limit": (offset / centre) / (limit_offset / limit_centre),
                "curvature": curvature,
                "limit_curvature": limit_curvature,
                "curvature_fraction": curvature / limit_curvature,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "criterion_shape.csv", index=False)
    (TABLES / "criterion_shape.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrr",
        ),
        encoding="utf-8",
    )



# ---------------------------------------------------------------------------
# The simulated maximiser itself, in the location model.
#
# The stationarity condition of the scaled nearest-atom criterion is
#
#     grad X_N(theta) = 2 S^{2/K} N^{-1} sum_n (theta - b_n*(theta)) = 0,
#
# that is, theta = N^{-1} sum_n b_n*(theta): the maximiser is a fixed point of
# "replace theta by the average of the nearest atom in each cloud".  So it can
# be computed exactly, without any general-purpose optimiser and without the
# multimodality that defeats one.
#
# The ratio to the exact MLE's error is the quantity of interest.  The
# M-estimator linearisation predicts it grows like S^{1/K}; it does not do so
# over the reachable range, for the reason the criterion-shape table records.
# ---------------------------------------------------------------------------

MAXIMISER_DIMENSION = 4
MAXIMISER_OBSERVATIONS = 4_000
MAXIMISER_SIZES = (16, 81, 256)
MAXIMISER_REPLICATIONS = 16
MAXIMISER_RESTARTS = 8
MAXIMISER_SPREAD = 0.8


def _nearest_atoms(clouds: NDArray[np.float64], theta: NDArray[np.float64]):
    """The nearest atom of each cloud to theta."""
    offsets = clouds - theta
    squared = np.einsum("nsk,nsk->ns", offsets, offsets)
    index = squared.argmin(axis=1)[:, None, None]
    return np.take_along_axis(clouds, index, axis=1)[:, 0, :]


def _criterion_value(clouds: NDArray[np.float64], theta: NDArray[np.float64]) -> float:
    """The unscaled nearest-atom criterion at theta."""
    offsets = clouds - theta
    return float(np.einsum("nsk,nsk->ns", offsets, offsets).min(axis=1).mean())


def _refine(clouds: NDArray[np.float64], start, iterations: int = 200):
    """Iterate theta <- mean of nearest atoms, a fixed point of grad X_N = 0."""
    theta = np.asarray(start, dtype=float).copy()
    for _ in range(iterations):
        updated = _nearest_atoms(clouds, theta).mean(axis=0)
        if np.allclose(updated, theta, atol=1e-13, rtol=0):
            return updated
        theta = updated
    return theta


def simulated_maximiser(clouds: NDArray[np.float64], rng: np.random.Generator):
    """Return the best local minimum found from several random starts.

    The estimator is the GLOBAL minimiser, and theta_0 is not known in practice,
    so the search must not begin there.  An earlier version started at the
    origin, which is theta_0, and understated the error by up to fourteen per
    cent at S = 256; restarts beat that solution in 28 of 30 replications.  With
    a finite restart budget this remains an upper bound on the criterion and so
    a lower bound on the estimator's error.
    """
    dimension = clouds.shape[2]
    best, best_value = None, math.inf
    for _ in range(MAXIMISER_RESTARTS):
        start = rng.normal(size=dimension) * MAXIMISER_SPREAD
        candidate = _refine(clouds, start)
        value = _criterion_value(clouds, candidate)
        if value < best_value:
            best, best_value = candidate, value
    return best



def central_chi_coefficient(dimension: int, order: int, size: float) -> float:
    """Return a_j = E[g_S(sqrt(chi^2_{K+2j}))], the coefficients of the Poisson
    expansion of G_S.  The curvature at the truth is a_1 - a_0 exactly."""
    degrees = dimension + 2 * order

    def integrand(m: float) -> float:
        weight = 2 * m * chi2.pdf(m * m, degrees)
        if weight <= 0.0:
            return 0.0
        return weight * _nn_conditional(dimension, m, size)

    total, _ = integrate.quad(integrand, 0.0, 14.0, limit=400)
    return total


def make_maximiser_table(rng: np.random.Generator) -> None:
    """Compare the simulated maximiser's error with the exact MLE's."""
    dimension = MAXIMISER_DIMENSION
    n_obs = MAXIMISER_OBSERVATIONS
    rows = []
    for size in MAXIMISER_SIZES:
        # The finite-S prediction of the M-estimator linearisation, using the
        # exact curvature grad^2 G_S(theta_0) = (a_1 - a_0) I rather than its
        # limit, since the limit is what the reachable range is short of.
        a_zero = central_chi_coefficient(dimension, 0, float(size))
        a_one = central_chi_coefficient(dimension, 1, float(size))
        curvature = a_one - a_zero
        predicted = 2 * size ** (1 / dimension) * math.sqrt(a_zero) / curvature

        tilde, hat = [], []
        for _ in range(MAXIMISER_REPLICATIONS):
            increments = rng.normal(size=(n_obs, dimension))          # theta_0 = 0
            clouds = increments[:, None, :] - rng.normal(
                size=(n_obs, size, dimension)
            )
            estimate = simulated_maximiser(clouds, rng)
            tilde.append(math.sqrt(n_obs) * float(np.linalg.norm(estimate)))
            hat.append(math.sqrt(n_obs) * float(np.linalg.norm(increments.mean(axis=0))))
        simulated = float(np.mean(tilde))
        exact = float(np.mean(hat))
        standard_error = float(
            np.std(tilde, ddof=1) / math.sqrt(MAXIMISER_REPLICATIONS)
        )
        rows.append(
            {
                "simulations": size,
                "observations": n_obs,
                "replications": MAXIMISER_REPLICATIONS,
                "scaled_simulated_error": simulated,
                "simulated_standard_error": standard_error,
                "scaled_exact_error": exact,
                "ratio": simulated / exact,
                "power_prediction": size ** (1 / dimension),
                "curvature": curvature,
                "predicted_error": predicted,
                "z_score": (predicted - simulated) / standard_error,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES / "simulated_maximiser.csv", index=False)
    (TABLES / "simulated_maximiser.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrrrrrr",
        ),
        encoding="utf-8",
    )



# ---------------------------------------------------------------------------
# The covering radius of the atom cloud over the parameter set.
#
# The envelope of the criterion class is S^{2/K} times the squared covering
# radius, and a covering radius exceeds a nearest-neighbour distance by a
# logarithmic factor.  That is what makes the envelope grow like (log S)^{2/K}
# and so fail to be uniformly integrable, which is why the naive route to the
# empirical-tail condition does not work.
#
# The probe count must be large enough that the supremum is resolved: with too
# few probes the spacing approaches the covering radius itself and the measured
# maximum is biased downward, which flattens the very trend being measured.
# ---------------------------------------------------------------------------

COVERING_DIMENSION = 4
COVERING_HALF_WIDTH = 0.4
COVERING_PROBES = 400_000
COVERING_SIZES = (10**3, 10**4, 10**5)
COVERING_REPLICATIONS = 8


def make_covering_table(rng: np.random.Generator) -> None:
    """Tabulate the covering radius against its two candidate scalings."""
    dimension = COVERING_DIMENSION
    half = COVERING_HALF_WIDTH
    spacing = 2 * half / COVERING_PROBES ** (1 / dimension)
    rows = []
    for size in COVERING_SIZES:
        radii = []
        for _ in range(COVERING_REPLICATIONS):
            atoms = rng.normal(size=(size, dimension))
            probes = rng.uniform(-half, half, size=(COVERING_PROBES, dimension))
            distances, _ = cKDTree(atoms).query(probes, k=1)
            radii.append(float(distances.max()))
        radius = float(np.mean(radii))
        rows.append(
            {
                "simulations": size,
                "covering_radius": radius,
                "probe_spacing": spacing,
                "resolution": radius / spacing,
                "over_plain_rate": radius / size ** (-1 / dimension),
                "over_log_rate": radius / (math.log(size) / size) ** (1 / dimension),
            }
        )
    frame = pd.DataFrame(rows)
    # The drift of each column across the table is what distinguishes the two
    # scalings, so record it rather than leaving it to be computed by hand.
    frame["plain_drift"] = frame["over_plain_rate"] / frame["over_plain_rate"].iloc[0]
    frame["log_drift"] = frame["over_log_rate"] / frame["over_log_rate"].iloc[0]
    predicted = (
        math.log(COVERING_SIZES[-1]) / math.log(COVERING_SIZES[0])
    ) ** (1 / dimension)
    frame["predicted_plain_drift"] = predicted
    frame.to_csv(TABLES / "covering_radius.csv", index=False)
    (TABLES / "covering_radius.tex").write_text(
        frame.to_latex(
            index=False,
            float_format=lambda value: f"{value:.6g}",
            escape=False,
            column_format="rrrrrrrrr",
        ),
        encoding="utf-8",
    )


def main(output_root: Path | None = None) -> None:
    """Generate all reproducible manuscript outputs.

    Parameters
    ----------
    output_root:
        Directory that receives ``figures/`` and ``tables/``.  Defaults to
        ``paper/``.  ``make verify`` passes a scratch directory instead, so the
        regenerated artefacts can be compared with the committed ones.
    """
    if output_root is not None:
        set_output_root(output_root)
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    make_variance_scaling_figure()
    make_path_rmse_figure()
    make_subcritical_distribution_results(rng)
    make_ou_scaling_figure()
    make_boundary_probability_figure()
    make_implicit_volatility_table()
    make_feller_table()
    make_design_table()
    make_rate_table()
    make_correlation_tables()
    make_literature_comparison_table()
    make_boundary_maximum_table()
    make_cir_negativity_table()
    make_nn_convergence_table()
    make_collapse_bound_table(rng)
    make_uniform_scaling_table(rng)
    make_score_moment_table(rng)
    make_criterion_shape_table()
    make_maximiser_table(rng)
    make_covering_table(rng)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="directory to receive figures/ and tables/ (default: paper/)",
    )
    main(parser.parse_args().output_root)
