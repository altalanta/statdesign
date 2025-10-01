# Mathematical Notes

This page documents the statistical formulas and assumptions used in statdesign calculations.

## Two-Sample Proportions

### Normal Approximation

For two independent samples with proportions $p_1$ and $p_2$, the test statistic follows:

$$Z = \frac{\hat{p}_1 - \hat{p}_2}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}$$

where $\hat{p} = \frac{n_1 p_1 + n_2 p_2}{n_1 + n_2}$ is the pooled proportion.

### Sample Size Formula

Given desired power $1-\beta$, significance level $\alpha$, and allocation ratio $r = n_2/n_1$:

$$n_1 = \frac{\left(Z_{\alpha/2}\sqrt{(1+r)\bar{p}(1-\bar{p})} + Z_\beta\sqrt{p_1(1-p_1) + r \cdot p_2(1-p_2)}\right)^2}{r(p_1-p_2)^2}$$

where $\bar{p} = \frac{p_1 + r \cdot p_2}{1 + r}$ and $Z_{\alpha/2}$, $Z_\beta$ are standard normal quantiles.

## Two-Sample Means

### Z-Test (Known Variance)

For two independent samples with means $\mu_1$, $\mu_2$ and common standard deviation $\sigma$:

$$Z = \frac{\bar{X}_1 - \bar{X}_2}{\sigma\sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}$$

### Sample Size Formula

$$n_1 = \frac{\left(Z_{\alpha/2} + Z_\beta\right)^2 \sigma^2 (1 + r)}{r(\mu_1 - \mu_2)^2}$$

### T-Test (Unknown Variance)

When $\sigma$ is unknown, the test statistic follows a t-distribution with $df = n_1 + n_2 - 2$ degrees of freedom.

**With SciPy**: Uses exact noncentral t-distribution for power calculations.

**Without SciPy**: Uses normal approximation with a conservative adjustment factor of 1.05 to account for additional uncertainty.

## One-Way ANOVA

### F-Test

For $k$ groups with equal sample sizes $n$ per group:

$$F = \frac{MS_{between}}{MS_{within}} \sim F(k-1, k(n-1))$$

### Effect Size (Cohen's f)

$$f = \frac{\sigma_{\text{between}}}{\sigma_{\text{within}}} = \sqrt{\frac{\sum_{i=1}^k (\mu_i - \mu)^2/k}{\sigma^2}}$$

### Sample Size Formula

**With SciPy**: Uses exact noncentral F-distribution:

$$n = \frac{\lambda}{k \cdot f^2} + 1$$

where $\lambda$ is the noncentrality parameter determined by power requirements.

**Without SciPy**: ANOVA calculations require SciPy and will raise an informative error.

## Multiple Testing Corrections

### Bonferroni Correction

For $m$ hypothesis tests:

$$\alpha_{\text{adjusted}} = \frac{\alpha}{m}$$

This controls the family-wise error rate (FWER) at level $\alpha$.

### Benjamini-Hochberg (BH) Correction

For the $i$-th smallest p-value out of $m$ tests:

$$\alpha_{\text{adjusted}} = \frac{i \cdot \alpha}{m}$$

This controls the false discovery rate (FDR) at level $\alpha$.

## Assumptions and Limitations

### Two-Sample Proportions
- Independence of observations
- Large sample sizes (each group should have ≥5 expected successes and failures)
- Normal approximation validity: $np(1-p) \geq 5$ for each group

### Two-Sample Means
- Independence of observations  
- Normality of underlying distributions (or large samples by CLT)
- Equal variances (for pooled t-test)
- Z-test assumes known population variance

### ANOVA
- Independence of observations
- Normality within each group
- Homogeneity of variance (Levene's test recommended)
- Balanced or near-balanced designs recommended

## Conservative Adjustments

When SciPy is unavailable, statdesign applies conservative adjustments:

- **T-tests**: 5% inflation factor to account for t vs. normal distribution differences
- **ANOVA**: Requires SciPy for accurate calculations
- **All calculations**: Round up to ensure adequate power

These adjustments ensure that achieved power is at least as high as requested, erring on the side of slightly larger sample sizes when exact distributions are unavailable.

## References

- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed.
- Fleiss, J. L., Levin, B., & Paik, M. C. (2003). *Statistical Methods for Rates and Proportions*. 3rd ed.
- Lachin, J. M. (1981). Introduction to sample size determination and power analysis for clinical trials. *Controlled Clinical Trials*, 2(2), 93-113.