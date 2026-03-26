# Quickstart: Tag and Geography Discovery Pages

## Prerequisites

- Start from a clean local stack state:
  - `docker compose down`
  - `docker compose up -d`
- Ensure the discovery backend and frontend are available through the existing local workflow.

## Manual Verification

### Topic Tag Navigation

1. Open a dataset list page or a dataset detail page containing visible topic tag pills.
2. Select a topic tag pill.
3. Confirm the app opens `/topics/{topicId}`.
4. Confirm the destination page shows the selected topic label and only datasets carrying that topic.
5. Confirm a dataset selected from the topic detail page opens the existing `/datasets/{id}` route.

### Geography Navigation

1. Open a dataset list page or a dataset detail page containing a visible geography pill.
2. Select the geography pill.
3. Confirm the app opens `/geographies/{geographyId}`.
4. Confirm the destination page shows the selected geography label and only datasets associated with that geography.
5. Confirm a dataset selected from the geography detail page opens the existing `/datasets/{id}` route.

### Fallback Behavior

1. Open an unknown `/topics/{topicId}` route and confirm the topic not-found experience.
2. Open an unknown `/geographies/{geographyId}` route and confirm the geography not-found experience.
3. Simulate upstream failures for topic and geography detail requests and confirm the generic error state preserves shell navigation.
4. Validate desktop and narrow/mobile viewport readability for both metadata detail pages.

## Validation Outcomes

- Topic pills and geography pills are visibly selectable when corresponding metadata exists.
- Metadata identity remains stable from pill click into the destination detail page.
- Topic detail and geography detail routes both preserve dataset-level onward navigation.
- Empty, not-found, and error states are explicit rather than blank.
