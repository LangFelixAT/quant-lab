# Project Brief

## Project Name

Quant Lab

------------------------------------------------------------------------

## Problem Statement

Retail investors and developers often experiment with trading
strategies, but most backtesting tools are:

-   Overly complex
-   Opaque in methodology
-   Difficult to extend
-   Not reproducible or well-tested

There is a need for a lightweight, deterministic, modular backtesting
engine that:

-   Clearly separates data, strategy logic, and evaluation
-   Is fully testable and CI-validated
-   Encourages disciplined quantitative experimentation
-   Can evolve incrementally (v0 → v1 → v2)

This project aims to build a minimal but extensible quantitative
research lab for systematic strategy experimentation.

The system prioritizes correctness, reproducibility, and
interpretability over raw performance.

------------------------------------------------------------------------

## Users and Stakeholders

### Primary users:

-   Developers learning quantitative finance
-   Engineers experimenting with systematic strategies
-   The project author (self-education + demonstration)

### Secondary stakeholders:

-   Readers of technical writeups (e.g., LinkedIn)
-   Future collaborators
-   Potential employers interested in quantitative or ML engineering
    discipline

------------------------------------------------------------------------

## Goals

### Goal 1:

Build a deterministic and modular backtesting engine for simple trading
strategies.

### Goal 2:

Ensure reproducibility and correctness through: - CI enforcement - Unit
tests - Clear performance metric definitions

### Goal 3:

Create a project structure that allows incremental extension into: -
Regime detection - Multi-strategy comparison - Robustness testing
(walk-forward, bootstrap, etc.)

------------------------------------------------------------------------

## Non-Goals

### Non-goal 1:

This is not intended to be a production trading system.

### Non-goal 2:

This project will not include: - Live trading execution - Real-time data
streaming - Broker integrations

### Non-goal 3:

The goal is not to maximize performance or optimize speed prematurely.

### Non-goal 4:

The project does not claim predictive power, financial alpha, or
investment advice.

------------------------------------------------------------------------

## Constraints

### Technical:

-   Python-based implementation
-   Deterministic results (no hidden randomness without explicit seed
    control)
-   Pure, side-effect-minimized computation where possible
-   No global mutable state in core engine components
-   No reliance on heavy proprietary infrastructure
-   Reproducible runs from raw data download
-   v0 supports **single-asset backtesting only**

### Timeline:

-   v0 should be achievable in small, atomic tasks
-   Each milestone must be implementable via isolated PRs

### Compliance / Security:

-   Use only publicly available historical data
-   No handling of sensitive financial credentials
-   No automated trading execution

------------------------------------------------------------------------

## Risks

### Risk 1:

Over-engineering the system before validating a minimal working version.

### Risk 2:

Strategy overfitting due to insufficient evaluation methodology.

### Risk 3:

Scope creep when adding advanced features (regime detection, robustness
testing).

------------------------------------------------------------------------

## Success Metrics

### Metric 1:

v0 can: - Download historical price data for a single asset - Run a
simple SMA crossover strategy - Compute and output: - CAGR - Sharpe
Ratio - Maximum Drawdown - Generate an equity curve plot

### Metric 2:

All v0 features: - Implemented via atomic issues - Covered by CI -
Reproducible from a clean clone

------------------------------------------------------------------------

## High-Level Technical Direction (Optional)

-   Language: Python 3.11+
-   Data: yfinance (public historical price data)
-   Numerical stack: pandas + numpy
-   Visualization: matplotlib
-   Testing: pytest
-   Linting: ruff
