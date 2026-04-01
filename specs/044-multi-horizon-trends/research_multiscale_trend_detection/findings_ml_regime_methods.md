# Findings: ML and Probabilistic Regime Methods

## Scope

Conceptual best practices and tradeoffs for HMM/Markov-switching/Bayesian change-point and multiresolution modeling.

## Key Findings

- Hidden Markov Models (HMMs) provide interpretable latent regime states with probabilistic assignments and are often a strong middle ground between interpretability and flexibility.
- Markov-switching models are strong when regime-specific dynamics differ materially (for example different AR behavior or volatility by regime).
- Bayesian Online Changepoint Detection (BOCPD) is a good fit for low-latency change alerts and run-length uncertainty, especially where online updates matter.
- Hierarchical or multiresolution designs are often better than one monolithic model when true behavior differs by timescale.

## Practical Implications

- If your top objective is stable, explainable regimes in UI, HMM/Markov-switching can be compelling.
- If your top objective is quick detection of fresh shifts, BOCPD is compelling.
- If your objective is productizing multiple user intents (short/medium/long), multiresolution architectures are usually the cleanest conceptual fit.

## Tradeoff Summary

- HMM:
  - Pros: interpretable hidden states, probabilistic outputs.
  - Cons: tuning/model-order sensitivity; retraining workflow required.
- Markov-switching:
  - Pros: explicit regime-dependent dynamics.
  - Cons: more parameterization and calibration burden.
- BOCPD:
  - Pros: online, uncertainty-aware run-length estimates.
  - Cons: hazard/prior tuning and alert-threshold design are critical.
- Multiresolution stack:
  - Pros: aligns naturally with horizon-dependent trend definitions.
  - Cons: compute + operational complexity and cross-layer conflict management.

## Sources

- Hidden Markov model (inference, learning, applications): https://en.wikipedia.org/wiki/Hidden_Markov_model
- Bayesian Online Changepoint Detection (Adams & MacKay): https://arxiv.org/abs/0710.3742
- Change detection framing (online/offline and model-selection perspectives): https://en.wikipedia.org/wiki/Change_detection
- Markov-switching econometrics foundation (Hamilton): https://doi.org/10.2307/1912559
