"""Pytest configuration and fixtures for testing."""

import pytest
from decimal import Decimal
from datetime import datetime


@pytest.fixture
def sample_portfolio_value():
    """Standard portfolio value for testing."""
    return Decimal("10000")


@pytest.fixture
def sample_win_rate():
    """Sample win rate (60%)."""
    return Decimal("0.60")


@pytest.fixture
def sample_avg_win():
    """Sample average win amount."""
    return Decimal("100")


@pytest.fixture
def sample_avg_loss():
    """Sample average loss amount."""
    return Decimal("50")


@pytest.fixture
def sample_confidence():
    """Sample AI confidence score (80%)."""
    return Decimal("0.80")


@pytest.fixture
def high_confidence():
    """High AI confidence score (95%)."""
    return Decimal("0.95")


@pytest.fixture
def low_confidence():
    """Low AI confidence score (55%)."""
    return Decimal("0.55")


@pytest.fixture
def sample_entry_price():
    """Sample entry price for a trade."""
    return Decimal("100.00")


@pytest.fixture
def sample_take_profit():
    """Sample take profit price."""
    return Decimal("120.00")


@pytest.fixture
def sample_stop_loss():
    """Sample stop loss price."""
    return Decimal("95.00")
