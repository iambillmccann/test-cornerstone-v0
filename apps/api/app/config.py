"""Compatibility module for older imports; use app.core.config instead."""

from app.core.config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
