# Data Model: Frontend UI Standardization Migration

## Overview

This feature does not add persistence models or backend data contracts. Its working model is a set of frontend migration entities that define scope, invariants, and validation boundaries for the UI refactor.

## Entities

### 1. Migrated UI Surface

- Description: A route-level or shared frontend surface that is explicitly included in the migration scope.
- Fields:
  - `surface_key`: Stable identifier for the surface
  - `surface_type`: Shell, control, content, state, or detail-analysis surface
  - `location`: Primary file or route location
  - `is_shared`: Whether the surface is reused across multiple routes
  - `current_pattern`: Existing implementation style
  - `target_pattern`: Standardized HeroUI/Tailwind pattern to adopt
  - `status`: Not started, in progress, migrated, or exception-approved
- Validation rules:
  - Every in-scope surface must resolve to either `migrated` or `exception-approved`.
  - Shared surfaces should be migrated before page-specific compositions that depend on them.

### 2. Standardized UI Pattern

- Description: The approved presentation and interaction pattern for a class of UI surfaces.
- Fields:
  - `pattern_key`: Stable identifier
  - `category`: Shell, form, navigation, content, state, metadata, or analytical container
  - `primary_components`: HeroUI primitives or composition pattern used
  - `layout_rules`: Shared spacing, width, alignment, and grouping expectations
  - `identity_rules`: Typography and color constraints that must remain preserved
  - `accessibility_rules`: Keyboard, pointer, and readable-state expectations
- Validation rules:
  - Each standardized pattern must be reusable across multiple surfaces or justify why it exists.
  - Patterns may not introduce duplicate alternatives for the same UI need without an explicit exception.

### 3. Legacy UI Pattern

- Description: An existing bespoke or one-off pattern that is a candidate for replacement.
- Fields:
  - `pattern_key`
  - `usage_locations`
  - `legacy_traits`: Custom CSS, raw HTML structure, one-off behavior, or mixed styling system
  - `replacement_candidate`: Standardized pattern key
  - `replacement_risk`: Low, medium, or high
- Validation rules:
  - Every legacy pattern in scope must either map to a replacement candidate or become an exception candidate.
  - High-risk replacements require targeted regression testing and manual validation.

### 4. Migration Exception

- Description: A documented retained non-standard pattern allowed after review.
- Fields:
  - `exception_key`
  - `surface_key`
  - `reason_category`: Brand identity, product clarity, readability, or unsupported standardized equivalent
  - `justification`
  - `review_scope`: What was considered before keeping the exception
  - `follow_up_required`: Yes or no
- Validation rules:
  - Exceptions must be explicit, bounded, and justified.
  - Exceptions cannot exist merely because migration work was incomplete.

### 5. Visual Identity Guardrail

- Description: The protected aspects of the current UI that must survive the migration.
- Fields:
  - `guardrail_key`
  - `identity_area`: Typography, color, tone, or recognizable layout cue
  - `source_of_truth`: Existing variable, token set, or documented visual rule
  - `must_preserve`: Yes or no
- Validation rules:
  - Protected guardrails must be reflected in the theme/bootstrap layer before broad component migration begins.
  - Changes to a protected guardrail require explicit feature-scope review.

## Relationships

- A `Migrated UI Surface` adopts one `Standardized UI Pattern` or resolves to one `Migration Exception`.
- A `Legacy UI Pattern` maps to one or more `Migrated UI Surface` records.
- A `Standardized UI Pattern` is constrained by one or more `Visual Identity Guardrail` rules.
- A `Migration Exception` references exactly one `Migrated UI Surface`.

## State Transitions

### Surface Migration Lifecycle

1. `not_started`
2. `inventory_confirmed`
3. `pattern_mapped`
4. `migrated`
5. `validated`

Alternative path:

1. `not_started`
2. `inventory_confirmed`
3. `exception_candidate`
4. `exception_approved`
5. `validated`

### Exception Lifecycle

1. `identified`
2. `reviewed`
3. `approved` or `rejected`
4. `documented`

## Coverage-Oriented Scope Inventory

### Shell surfaces

- Root layout
- Header
- Footer
- Global constrained-content/page wrappers

### Shared controls

- Hero search surface
- Navbar search surface
- Dataset list filters/sort
- Toggle-like discovery controls
- Shared pills/chips/metadata links

### Shared content surfaces

- Dataset rows/cards
- Recent updates feed rows
- Catalog/search list containers
- Empty and error states

### Detail and metadata surfaces

- Dataset detail header and analysis containers
- Source/topic/geography headers
- Observation container surfaces around charts and tables
