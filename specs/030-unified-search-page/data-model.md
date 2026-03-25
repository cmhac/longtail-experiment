# Data Model: Unified Search Page Experience

## Entity: Unified Search Surface

- Purpose: Represents the shared user interaction model for typing, suggestion browsing, and query submission.
- Fields:
  - surface_id: Stable identifier for homepage, dedicated page, or navbar surface.
  - input_value: Current text entered by user.
  - submission_value: Last submitted non-empty query.
  - suggestion_status: idle, loading, ready, unavailable.
  - suggestion_items: Ordered likely-match entries for current input.
- Validation Rules:
  - submission_value must be non-empty after trimming whitespace.
  - suggestion_items must map to current input context when suggestion_status is ready.
  - surface_id must be one of the supported entry surfaces.

## Entity: Search Navigation Context

- Purpose: Captures the canonical query state used when transitioning to the dedicated search route.
- Fields:
  - route_path: Dedicated search route path.
  - query_text: URL-carried search query.
  - source_surface: Originating surface (homepage or navbar).
  - navigation_timestamp: Client-side timestamp for transition diagnostics.
- Validation Rules:
  - query_text must be non-empty and trimmed when navigation occurs.
  - route_path must resolve to the dedicated search page.

## Entity: Dedicated Search View State

- Purpose: Represents page-level search rendering state for the dedicated route.
- Fields:
  - active_query: Query currently shown in the page search input.
  - summary_text: Search summary copy from existing discovery behavior.
  - result_items: Search result rows rendered beneath the search surface.
  - page_state: idle, loading, loaded, empty, error.
  - error_message: Optional fallback message for failure state.
- Validation Rules:
  - loaded and empty states require completion of a search response cycle.
  - error state must include a visible fallback message while preserving active input.
  - active_query must remain editable regardless of page_state.

## Entity: Navbar Search Control State

- Purpose: Represents compact and expanded behavior for shell-level search entry.
- Fields:
  - control_mode: compact or expanded.
  - is_focused: Whether input focus is active.
  - pending_query: Current input before submit.
  - dismiss_reason: explicit_close, blur, navigation, or none.
- Validation Rules:
  - expanded mode must expose an input-ready interaction surface.
  - compact mode must not obscure primary shell navigation actions.

## Relationships

- A Unified Search Surface emits a Search Navigation Context on valid submit.
- Search Navigation Context initializes Dedicated Search View State.
- Dedicated Search View State reuses Unified Search Surface behavior for refinements.
- Navbar Search Control State controls how the navbar-hosted Unified Search Surface is presented.
