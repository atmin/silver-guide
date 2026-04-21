# ADR-0002: Category Tree Model

## Status
Accepted

## Context
Categories are hierarchical (e.g. Electronics → Phones → Smartphones). The product
search endpoint must be able to return all products under a given category, including
descendants at any depth. Trees are typically shallow (3–5 levels) and small (hundreds
of nodes).

## Decision
Adjacency list (self-referential `parent` FK) with Python BFS for descendant traversal.

## Alternatives considered
- **Recursive CTE**: no maintenance cost, but Django ORM does not generate them — raw
  SQL required. Premature complexity for a tree that fits comfortably in memory.
- **django-mptt / django-treebeard**: solves the problem cleanly, but adds a dependency
  and non-obvious model constraints for a tree small enough not to need it yet.
- **Closure table**: fast reads, but a separate table and write-time maintenance logic
  for a dataset where traversal cost is negligible.

## Consequences
- Descendant lookup fetches all categories once and walks them in Python. Acceptable at
  this scale; if the tree grows large enough to measure, the filter method is the only
  thing that changes — the API contract stays identical.
- Adding `django-treebeard` later is a contained migration with no endpoint changes.
