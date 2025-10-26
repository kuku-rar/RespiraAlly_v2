"""
Domain Entities Package

Pure domain entities with NO infrastructure dependencies.

Following Clean Architecture:
- Entities contain business logic and validation
- No ORM, no database, no external dependencies
- Simple data structures with clear responsibilities
"""

from respira_ally.domain.entities.daily_log import DailyLog

__all__ = [
    "DailyLog",
]
