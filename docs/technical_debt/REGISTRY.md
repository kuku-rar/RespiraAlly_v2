# Technical Debt Registry

> **Purpose**: 集中追蹤所有 MVP 簡化決策造成的技術債，確保 MVP 驗證後有清晰的完整開發路徑
> **Created**: 2025-10-26
> **Strategy**: 選項C - 邊開發邊建立追蹤系統

## Active Debt Items

### DEBT-001: Alert System MVP Simplification
- **Status**: 🟡 Active (being tracked during development)
- **Created**: 2025-10-26
- **Impact**: Medium
- **Component**: Alert System
- **Details**: See [DEBT-001-alert-mvp.md](./DEBT-001-alert-mvp.md)

**MVP Approach**:
- 3 fixed alert rules (GOLD-E + High CAT + Frequent Exacerbations)
- No notification delivery mechanism (LINE/Email deferred)
- Simplified alert metadata

**Full Implementation Required**:
- Configurable rule engine (Rule Builder UI)
- Multi-channel notifications (LINE Bot + Email + SMS)
- Alert acknowledgment workflow
- Alert escalation logic
- Historical alert analytics

**Estimated Refactor Cost**: 10-15h
**Migration Path**: Defined in Evolution Map

---

## Debt Categories

### 🟢 Low Impact (< 5h refactor)
- None currently

### 🟡 Medium Impact (5-15h refactor)
- DEBT-001: Alert System MVP

### 🔴 High Impact (> 15h refactor)
- None currently

---

## Tracking Process

1. **Code Level**: All MVP simplifications marked with `TODO(DEBT-xxx)` comments
2. **Registry Level**: This file tracks all debt items at a glance
3. **Detail Level**: Each DEBT-xxx has a dedicated markdown file
4. **Evolution Map**: Provides migration paths from MVP → Full Implementation

---

## Review Schedule

- **Weekly**: Review new debt items added during sprint
- **End of Sprint**: Update debt status and priorities
- **Post-MVP**: Execute migration plan based on Evolution Map
