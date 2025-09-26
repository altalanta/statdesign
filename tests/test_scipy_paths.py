from __future__ import annotations

import importlib
from collections.abc import Iterator

import pytest

from statdesign import api
from statdesign.core import ncf


@pytest.fixture
def scipy_enabled(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    pytest.importorskip("scipy.stats")
    monkeypatch.setenv("STATDESIGN_AUTO_SCIPY", "1")
    importlib.reload(ncf)
    try:
        yield
    finally:
        monkeypatch.delenv("STATDESIGN_AUTO_SCIPY", raising=False)
        importlib.reload(ncf)


@pytest.mark.usefixtures("scipy_enabled")
def test_n_mean_scipy_matches_golden() -> None:
    result = api.n_mean(mu1=0.0, mu2=0.5, sd=1.0, power=0.8, alpha=0.05, test="t")
    assert result == (64, 64)


@pytest.mark.usefixtures("scipy_enabled")
def test_n_anova_scipy_matches_golden() -> None:
    total = api.n_anova(k_groups=4, effect_f=0.25, alpha=0.05, power=0.80)
    assert total == 179
