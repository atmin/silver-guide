# ADR-0003: Product Model

## Status
Accepted

## Context
The product catalogue needs a stable identifier for external systems (ERP, warehouse,
imports), a human-readable title, pricing, a category relationship, and a way to remove
products without breaking order history or foreign-key references.

## Decision
A flat `Product` model with a string `sku` as the business key, a decimal `price`, a
`ForeignKey` to `Category` with `on_delete=PROTECT` (prevents silent data loss when a
category is deleted), and an `is_active` flag for soft-delete. Hard deletes are blocked
at the ORM level; `DELETE /products/{id}/` sets `is_active=False` instead.

## Alternatives considered

- **Hard delete**: simplest to implement, but destroys audit trail and breaks any
  external reference (order lines, analytics events) that holds a product ID. Rejected.
- **Separate `deleted_at` timestamp**: common pattern, carries the deletion time for
  free. Adds a nullable column with the same query overhead as `is_active=False` but
  requires a custom manager to filter by `IS NULL`. Not worth the extra complexity at
  this stage.
- **`sku` uniqueness scoped to `(sku, is_active)`**: would allow a new product to reuse
  a SKU while the old one is soft-deleted. Rejected — a SKU is a stable business
  identifier and must be unique unconditionally; ambiguity across active/inactive records
  complicates imports and external lookups.

## Consequences
- `GET /products/` returns only `is_active=True` records by default; inactive products
  are invisible to the API without a deliberate filter override.
- Re-activating a product is possible (set `is_active=True`), but not exposed via the
  API.
- Deleting a category that still has products raises an `IntegrityError` — the caller
  must reassign or deactivate products first.
