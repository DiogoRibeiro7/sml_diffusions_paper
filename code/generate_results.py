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
from scipy.special import logsumexp
from scipy.stats import norm

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="directory to receive figures/ and tables/ (default: paper/)",
    )
    main(parser.parse_args().output_root)
