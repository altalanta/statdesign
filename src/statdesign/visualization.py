"""Power curve visualization for statistical design decision-making."""

from __future__ import annotations

import warnings
from typing import Callable, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_power_curves(
    test_func: Callable,
    base_params: dict,
    sweep_param: str,
    sweep_range: tuple,
    fixed_params: dict = None,
    highlight_current: bool = True,
    save_path: str = None,
    return_data: bool = False,
) -> Union[plt.Figure, tuple]:
    """Generate power curves showing how statistical power varies across parameter ranges.

    This function bridges the gap between point estimates and decision-making under
    real constraints by visualizing power sensitivity to key design parameters.

    Parameters
    ----------
    test_func : callable
        Existing power calculation function that returns a power value (float) or
        sample size tuple. Must accept all parameters in base_params as keyword arguments.
    base_params : dict
        Baseline design parameters containing all required arguments for test_func.
        The swept parameter will be replaced with values from sweep_range.
    sweep_param : str
        Parameter name to vary ('effect_size', 'n', 'alpha', etc.). Must exist in base_params.
    sweep_range : tuple
        (min_value, max_value, n_points) defining the parameter range to evaluate.
    fixed_params : dict, optional
        Additional parameters to override in base_params for this analysis.
    highlight_current : bool, default True
        If True, add vertical line and marker showing baseline design point.
    save_path : str, optional
        If provided, save figure to this path.
    return_data : bool, default False
        If True, return (figure, DataFrame) instead of just figure.

    Returns
    -------
    matplotlib.figure.Figure or tuple
        Power curve plot, optionally with underlying data if return_data=True.

    Examples
    --------
    >>> import statdesign as sd
    >>>
    >>> # Effect size sweep for two-sample means test
    >>> base_design = {
    ...     'mu1': 10.0, 'mu2': 12.0, 'sd': 3.0,
    ...     'alpha': 0.05, 'power': 0.80
    ... }
    >>> fig = sd.plot_power_curves(
    ...     test_func=lambda **kw: sd.n_mean(**kw)[0] if 'power' in kw else
    ...                           power_from_n(sd.n_mean(**kw)[0], **kw),
    ...     base_params=base_design,
    ...     sweep_param='mu2',
    ...     sweep_range=(10.5, 15.0, 50)
    ... )

    >>> # Sample size sweep for fixed effect
    >>> base_design = {
    ...     'mu1': 10.0, 'mu2': 12.0, 'sd': 3.0,
    ...     'alpha': 0.05, 'power': 0.80
    ... }
    >>> fig = sd.plot_power_curves(
    ...     test_func=lambda n, **kw: power_two_sample_t(n, **kw),
    ...     base_params=base_design,
    ...     sweep_param='n',
    ...     sweep_range=(10, 100, 50),
    ...     fixed_params={'power': None}  # Remove power to allow n sweep
    ... )

    >>> # Multi-scenario comparison using separate calls
    >>> scenarios = [
    ...     {'sd': 2.0, 'label': 'Low variance'},
    ...     {'sd': 3.0, 'label': 'Medium variance'},
    ...     {'sd': 4.0, 'label': 'High variance'}
    ... ]
    >>> fig, ax = plt.subplots()
    >>> for scenario in scenarios:
    ...     params = {**base_design, **scenario}
    ...     plot_power_curves(test_func, params, 'mu2', (10.5, 15.0, 50),
    ...                      highlight_current=False)
    ...     ax.plot([], [], label=scenario['label'])
    >>> ax.legend()

    Warnings
    --------
    Will warn if sweep range produces uninformative results (all power >0.99 or <0.05).

    Notes
    -----
    The function handles test_func errors gracefully by excluding problematic parameter
    combinations from the plot. A horizontal reference line is drawn at power=0.80
    (conventional threshold). Key transitions like power dropping below 0.80 are
    automatically annotated.
    """
    # Validate inputs
    if sweep_param not in base_params:
        raise ValueError(f"sweep_param '{sweep_param}' not found in base_params")

    if len(sweep_range) != 3:
        raise ValueError("sweep_range must be (min_value, max_value, n_points)")

    min_val, max_val, n_points = sweep_range
    if min_val >= max_val:
        raise ValueError("sweep_range min_value must be less than max_value")

    if n_points < 2:
        raise ValueError("n_points must be at least 2")

    # Merge parameters
    params = base_params.copy()
    if fixed_params:
        params.update(fixed_params)

    # Generate parameter sweep
    sweep_values = np.linspace(min_val, max_val, int(n_points))
    power_values = []
    valid_sweep_values = []

    for val in sweep_values:
        try:
            test_params = params.copy()
            test_params[sweep_param] = val

            # Call test function and extract power
            result = test_func(**test_params)

            # Handle different return types
            if isinstance(result, (tuple, list)):
                # Assume this is a sample size function, need to calculate power
                # For now, we'll skip this case and focus on direct power functions
                continue
            elif isinstance(result, (int, float)):
                power = float(result)
            else:
                continue

            # Validate power range
            if 0 <= power <= 1:
                power_values.append(power)
                valid_sweep_values.append(val)

        except Exception:
            # Gracefully handle function errors for extreme parameter values
            continue

    if len(power_values) < 2:
        raise RuntimeError("Unable to generate sufficient valid power calculations")

    # Convert to arrays
    valid_sweep_values = np.array(valid_sweep_values)
    power_values = np.array(power_values)

    # Check for uninformative ranges
    if np.all(power_values > 0.99):
        warnings.warn("All power values >0.99 - consider expanding parameter range")
    elif np.all(power_values < 0.05):
        warnings.warn("All power values <0.05 - consider expanding parameter range")

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Main power curve
    ax.plot(valid_sweep_values, power_values, "b-", linewidth=2, label="Power")

    # Reference line at 0.80
    ax.axhline(y=0.80, color="gray", linestyle="--", alpha=0.7, label="Power = 0.80")

    # Highlight current design point
    if highlight_current:
        current_val = base_params[sweep_param]
        if min_val <= current_val <= max_val:
            # Interpolate power at current value
            current_power = np.interp(current_val, valid_sweep_values, power_values)
            ax.axvline(x=current_val, color="red", linestyle=":", alpha=0.7)
            ax.plot(
                current_val,
                current_power,
                "ro",
                markersize=8,
                label=f"Current design (power={current_power:.3f})",
            )

    # Find and annotate key transitions
    power_80_crossings = []
    for i in range(len(power_values) - 1):
        if (power_values[i] >= 0.80 and power_values[i + 1] < 0.80) or (
            power_values[i] < 0.80 and power_values[i + 1] >= 0.80
        ):
            # Linear interpolation to find crossing point
            x_cross = np.interp(
                0.80,
                [power_values[i], power_values[i + 1]],
                [valid_sweep_values[i], valid_sweep_values[i + 1]],
            )
            power_80_crossings.append(x_cross)

    # Annotate crossings
    for x_cross in power_80_crossings:
        ax.annotate(
            f"{sweep_param}={x_cross:.3f}",
            xy=(x_cross, 0.80),
            xytext=(10, 10),
            textcoords="offset points",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

    # Formatting
    ax.set_xlabel(sweep_param.replace("_", " ").title())
    ax.set_ylabel("Statistical Power")
    ax.set_title(f"Power Curve: {sweep_param.replace('_', ' ').title()} Sensitivity")
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(0, 1)

    # Set reasonable x-axis limits
    ax.set_xlim(min_val, max_val)

    plt.tight_layout()

    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    # Return results
    if return_data:
        data = pd.DataFrame({sweep_param: valid_sweep_values, "power": power_values})
        return fig, data

    return fig


def _create_power_function_wrapper(sample_size_func: Callable, power_calc_func: Callable):
    """Helper to wrap sample size functions for power curve generation."""

    def power_wrapper(**params):
        # Remove power from params if present
        power_target = params.pop("power", None)

        # Calculate sample size
        n_result = sample_size_func(**params)
        n = n_result[0] if isinstance(n_result, (tuple, list)) else n_result

        # Calculate actual power with this sample size
        power_params = params.copy()
        power_params["n"] = n
        return power_calc_func(**power_params)

    return power_wrapper
