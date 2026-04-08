# Research: Local Development Performance Stabilization (Spec 051)

## Decision 1: Dataset detail metadata retrieval must be dataset-scoped

- Decision: Use a dataset-targeted metadata retrieval path for detail requests instead of loading and scanning full catalog metadata for every detail lookup.
- Rationale: Current behavior performs broad catalog aggregation work when only one dataset is requested, creating avoidable latency that grows with catalog size.
- Alternatives considered:
  - Keep full-catalog retrieval and add in-memory caching: rejected because it retains heavy global query work and introduces cache invalidation complexity in local development.
  - Keep current behavior and optimize only frontend loading UI: rejected because it does not address backend request-time bottleneck.

## Decision 2: As-of descriptor candidate mapping should minimize non-essential filtering work

- Decision: Keep as-of descriptor correctness semantics, but reduce candidate assembly/filtering cost by constraining work to the minimal candidate set needed per dataset detail response.
- Rationale: The current detail observation path performs extra candidate processing beyond what is required for each response; reducing this work improves latency without changing payload shape.
- Alternatives considered:
  - Remove as-of descriptor mapping from detail response: rejected because it would alter behavior expected by existing consumers.
  - Leave candidate path unchanged and optimize only DB connection behavior: rejected because this leaves a significant detail-path hotspot unresolved.

## Decision 3: Local runtime request overhead should be reduced while preserving safety checks

- Decision: Reduce avoidable per-request backend runtime setup overhead while preserving schema readiness and runtime safety guarantees.
- Rationale: Repeated setup costs can add noticeable latency in local development where developers rapidly reload and navigate between detail pages.
- Alternatives considered:
  - Disable readiness/safety checks entirely in local development: rejected because it weakens reliability and can hide environment drift issues.
  - Treat local slowness as acceptable and defer to production-only optimization: rejected because local feedback-loop speed is a primary developer productivity requirement.

## Decision 4: Frontend behavior remains functionally unchanged

- Decision: Preserve dataset detail route, response consumption, and error semantics on the frontend; focus optimization on backend and request-path efficiency.
- Rationale: The user-visible delay occurs before detail content is available, and the current route behavior is functionally correct.
- Alternatives considered:
  - Redesign route loading architecture: rejected for scope creep relative to the identified bottlenecks.
  - Introduce new client-side data contract shapes: rejected because the feature goal is performance stabilization without contract churn.

## Decision 5: Validation protocol uses before/after local measurements plus regression checks

- Decision: Validate improvement with a fixed local sample of dataset detail pages and repeated-load runs, and confirm no regressions on related discovery endpoints.
- Rationale: Feature success criteria are local and measurable; results must be comparable on the same environment.
- Alternatives considered:
  - Use ad hoc subjective verification only: rejected because it cannot prove SC-001/SC-002/SC-003.
  - Validate only one detail page: rejected because it does not represent realistic variance across dataset sizes.

## Decision 6: Contract stability is a hard requirement

- Decision: Preserve existing discovery endpoint payload shape and error behavior while improving request performance.
- Rationale: This feature targets speed improvements, not interface redesign; contract stability lowers rollout risk.
- Alternatives considered:
  - Introduce a new detail endpoint contract for performance mode: rejected due to unnecessary migration complexity.

No unresolved technical clarifications remain for planning.
