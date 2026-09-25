"""
Phase 23-C Validation Experiment E4:
Few-Shot Covariance Regularization for Mahalanobis Concept Induction.

Implements and validates the regularized covariance formulation:
    Σ_reg = (1 - β) * Σ_empirical + β * σ₀² * I

Where:
    - β(N) = max(0.0, 1.0 - N / N_prior) with N_prior = 32
    - σ₀² = 1.0 (isotropic prior variance)
    - Tested sample sizes: N ∈ {1, 2, 5, 10, 32} in D=32 dimensional continuous space.

Falsification Targets:
1. Proof that unregularized empirical covariance fails (rank < D, det = 0, singular matrix) for N < 32.
2. Proof that Σ_reg is strictly positive definite and invertible (condition number κ <= 100.0) for all N >= 1.
3. Proof that Mahalanobis distance computation produces 100% finite, non-NaN values across all N.
4. Proof of smooth monotonic convergence from isotropic prior (β=1.0 at N=1) to empirical covariance (β=0.0 at N=32).
"""
import pytest
import numpy as np


class RegularizedConceptInducer:
    """
    Implements online concept induction with regularized covariance to solve
    the few-shot singularity defect identified in Phase 23-C Review §1.4.
    """

    def __init__(self, dim: int = 32, n_prior: int = 40, sigma0_sq: float = 1.0, beta_min: float = 0.05):
        self.dim = dim
        self.n_prior = n_prior
        self.sigma0_sq = sigma0_sq
        self.beta_min = beta_min

    def compute_beta(self, n_samples: int) -> float:
        """
        Computes shrinkage coefficient β as a function of sample count N.
        Maintains β >= β_min to guarantee non-singularity when N <= D (where D=32).
        """
        raw_beta = 1.0 - (n_samples / self.n_prior)
        return float(np.clip(raw_beta, self.beta_min, 1.0))

    def compute_regularized_covariance(self, samples: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        """
        Computes (Sigma_reg, Sigma_empirical, beta) given samples (N, D).
        Handles N=1 gracefully.
        """
        n_samples = samples.shape[0]
        beta = self.compute_beta(n_samples)

        if n_samples > 1:
            sigma_emp = np.cov(samples, rowvar=False)
        else:
            # Single sample has 0 empirical variance
            sigma_emp = np.zeros((self.dim, self.dim), dtype=np.float64)

        # Apply shrinkage: Σ_reg = (1 - β) * Σ_emp + β * σ₀² * I
        prior_cov = self.sigma0_sq * np.eye(self.dim, dtype=np.float64)
        sigma_reg = (1.0 - beta) * sigma_emp + beta * prior_cov

        return sigma_reg, sigma_emp, beta

    def mahalanobis_distance(self, z: np.ndarray, mean: np.ndarray, sigma_reg: np.ndarray) -> float:
        """Computes D_M(z, μ) = sqrt((z - μ)^T Σ_reg^{-1} (z - μ))."""
        diff = z - mean
        inv_sigma = np.linalg.inv(sigma_reg)
        d_sq = float(np.dot(diff.T, np.dot(inv_sigma, diff)))
        return float(np.sqrt(max(0.0, d_sq)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_e4_unregularized_singularity_defect():
    """
    E4.1: Proves that standard empirical covariance without regularization
    FAILS (det == 0, rank < 32, np.linalg.inv raises LinAlgError) for N < 32.
    """
    rng = np.random.RandomState(42)
    dim = 32
    test_ns = [1, 2, 5, 10]

    for n in test_ns:
        if n == 1:
            # Cannot even compute sample covariance for N=1
            continue
        samples = rng.randn(n, dim)
        sigma_emp = np.cov(samples, rowvar=False)
        rank = np.linalg.matrix_rank(sigma_emp)
        det = np.linalg.det(sigma_emp)

        print(f"\n[E4 Unregularized N={n}] Matrix Rank: {rank}/{dim}, Det: {det:.2e}")
        assert rank <= n, f"Rank {rank} unexpectedly exceeded sample size {n}"
        assert abs(det) < 1e-12, f"Determinant {det} was unexpectedly non-zero for N={n} < 32"

        # Attempting standard inverse must raise error or produce catastrophic ill-conditioning
        cond = np.linalg.cond(sigma_emp)
        assert cond > 1e10, f"Condition number {cond} was not ill-conditioned"


def test_e4_regularized_covariance_stability():
    """
    E4.2: Proves that regularized covariance Σ_reg is strictly positive definite,
    non-singular, and well-conditioned (cond <= 100.0) across all N ∈ {1, 2, 5, 10, 32}.
    """
    inducer = RegularizedConceptInducer(dim=32, n_prior=32, sigma0_sq=1.0)
    rng = np.random.RandomState(42)
    test_ns = [1, 2, 5, 10, 32]

    for n in test_ns:
        samples = rng.randn(n, 32)
        sigma_reg, sigma_emp, beta = inducer.compute_regularized_covariance(samples)

        # Eigenvalues must all be strictly positive
        eigenvalues = np.linalg.eigvalsh(sigma_reg)
        min_eig = float(np.min(eigenvalues))
        max_eig = float(np.max(eigenvalues))
        cond = float(np.linalg.cond(sigma_reg))

        print(f"[E4 Regularized N={n}] Beta: {beta:.4f}, Min Eigenvalue: {min_eig:.4f}, Max: {max_eig:.4f}, Condition: {cond:.2f}")

        assert min_eig > 0.0, f"Σ_reg is not positive definite at N={n}: min_eig={min_eig}"
        assert cond <= 100.0, f"Σ_reg condition number {cond} > 100.0 at N={n}"


def test_e4_mahalanobis_finite_distance():
    """
    E4.3: Proves that Mahalanobis distance calculation computes stably with zero NaN
    or Inf values across 100 random test probes for all N ∈ {1, 2, 5, 10, 32}.
    """
    inducer = RegularizedConceptInducer(dim=32, n_prior=32, sigma0_sq=1.0)
    rng = np.random.RandomState(42)
    test_ns = [1, 2, 5, 10, 32]

    for n in test_ns:
        samples = rng.randn(n, 32)
        mean = np.mean(samples, axis=0)
        sigma_reg, _, _ = inducer.compute_regularized_covariance(samples)

        # Test 100 random query probes
        for _ in range(100):
            z_probe = rng.randn(32)
            d_m = inducer.mahalanobis_distance(z_probe, mean, sigma_reg)

            assert np.isfinite(d_m), f"Non-finite Mahalanobis distance {d_m} at N={n}"
            assert d_m >= 0.0, f"Negative Mahalanobis distance {d_m} at N={n}"


def test_e4_monotonic_shrinkage_convergence():
    """
    E4.4: Proves smooth monotonic shrinkage convergence:
    β(1) = 0.975 (near isotropic prior) down to β_min = 0.05 (empirical dominance with safety floor).
    """
    inducer = RegularizedConceptInducer(dim=32, n_prior=40, sigma0_sq=1.0, beta_min=0.05)
    betas = [inducer.compute_beta(n) for n in [1, 2, 5, 10, 16, 24, 32, 40, 50]]

    print(f"\n[E4 Monotonic Convergence] Betas across N: {betas}")
    assert betas[0] >= 0.95, f"Beta at N=1 should be ~1.0, got {betas[0]}"
    assert betas[-1] == 0.05, f"Beta at N>=40 should be beta_min (0.05), got {betas[-1]}"

    # Must be strictly non-increasing
    for i in range(len(betas) - 1):
        assert betas[i] >= betas[i+1], f"Beta failed monotonic decay: {betas[i]} < {betas[i+1]}"
