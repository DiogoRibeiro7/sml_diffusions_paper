"""Generate figures and tables for the simulated-likelihood manuscript.

The experiments are deliberately reproducible and focus on quantities for which
closed-form benchmarks are available.  No external data are required.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.special import logsumexp
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
SEED = 20260726


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
    fig.savefig(FIGURES / "brownian_second_moment_scaling.pdf")
    fig.savefig(FIGURES / "brownian_second_moment_scaling.png", dpi=220)
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
    fig.savefig(FIGURES / "brownian_joint_path_rmse.pdf")
    fig.savefig(FIGURES / "brownian_joint_path_rmse.png", dpi=220)
    plt.close(fig)


def make_subcritical_distribution_results(rng: np.random.Generator) -> None:
    """Simulate the counterexample path M=S in four dimensions."""
    dimension = 4
    q = true_brownian_density_at_origin(dimension)
    m_values = [8, 16, 32, 64, 128, 256, 512]
    rows: list[dict[str, float | int]] = []

    for m in m_values:
        # Keep the total number of endpoint draws roughly controlled while
        # retaining enough replications to estimate medians and quantiles.
        replications = int(min(20_000, max(1_500, 5_000_000 // m)))
        estimates = simulate_brownian_estimator(
            dimension=dimension,
            m_steps=m,
            simulations=m,
            replications=replications,
            rng=rng,
        )
        relative = estimates / q
        rows.append(
            {
                "M": m,
                "S": m,
                "replications": replications,
                "mean_relative": float(np.mean(relative)),
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
    fig.savefig(FIGURES / "brownian_subcritical_distribution.pdf")
    fig.savefig(FIGURES / "brownian_subcritical_distribution.png", dpi=220)
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
        ratios.append(h ** (dimension / 2.0) * ou_second_moment(dimension, int(m)) / limiting_constant)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(m_values, ratios, marker="o")
    ax.axhline(1.0, linestyle="--", linewidth=1.0)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Euler substeps $M$")
    ax.set_ylabel("Scaled second moment divided by its diffusion limit")
    ax.set_title("Four-dimensional Ornstein-Uhlenbeck benchmark")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "ou_second_moment_scaling.pdf")
    fig.savefig(FIGURES / "ou_second_moment_scaling.png", dpi=220)
    plt.close(fig)


def euler_negative_probability(
    x: NDArray[np.float64],
    *,
    alpha: float,
    beta: float,
    h: float,
) -> NDArray[np.float64]:
    """Probability that one Euler step for X=epsilon^2 becomes negative.

    The process is dX = (beta^2 - 2 alpha X) dt + 2 beta sqrt(X) dW.
    """
    if alpha <= 0.0 or beta <= 0.0 or h <= 0.0:
        raise ValueError("alpha, beta, and h must be positive")
    x = np.asarray(x, dtype=np.float64)
    mean = x + (beta**2 - 2.0 * alpha * x) * h
    sd = 2.0 * beta * np.sqrt(x * h)
    probability = np.zeros_like(x)
    positive_sd = sd > 0.0
    probability[positive_sd] = norm.cdf(-mean[positive_sd] / sd[positive_sd])
    probability[~positive_sd] = (mean[~positive_sd] < 0.0).astype(float)
    return probability


def make_boundary_probability_figure() -> None:
    """Plot Euler boundary-violation probabilities using reported estimates."""
    x_values = np.logspace(-8, -1.2, 500)
    parameter_sets = {
        "U.S.-U.K. estimates": (0.320, 0.088),
        "U.S.-Germany estimates": (0.338, 0.101),
    }
    step_sizes = [0.1, 0.02]

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for label, (alpha, beta) in parameter_sets.items():
        for h in step_sizes:
            probability = euler_negative_probability(
                x_values,
                alpha=alpha,
                beta=beta,
                h=h,
            )
            ax.plot(x_values, probability, label=f"{label}, $h={h}$")

    ax.set_xscale("log")
    ax.set_xlabel(r"Current state $X_t=\epsilon_t^2$")
    ax.set_ylabel("One-step probability of a negative Euler state")
    ax.set_ylim(0.0, 0.55)
    ax.set_title("Ordinary Euler discretisation is not positivity preserving")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(FIGURES / "epsilon_squared_euler_negative_probability.pdf")
    fig.savefig(FIGURES / "epsilon_squared_euler_negative_probability.png", dpi=220)
    plt.close(fig)


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
    ]
    frame = pd.DataFrame(rows)
    (TABLES / "rate_conditions.tex").write_text(
        frame.to_latex(index=False, escape=False, column_format="lll"),
        encoding="utf-8",
    )
    frame.to_csv(TABLES / "rate_conditions.csv", index=False)


def main() -> None:
    """Generate all reproducible manuscript outputs."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    make_variance_scaling_figure()
    make_path_rmse_figure()
    make_subcritical_distribution_results(rng)
    make_ou_scaling_figure()
    make_boundary_probability_figure()
    make_implicit_volatility_table()
    make_rate_table()


if __name__ == "__main__":
    main()
