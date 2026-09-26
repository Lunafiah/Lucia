"""
src/core/language/adapter/registry.py

Language Driver Registry for Phase 23-F.

Manages registration and lookup of language-specific adapters.
Enforces the strict language admission policy: only 'en', 'vi', 'ja'
are permitted.
"""

from __future__ import annotations

import logging
import threading
from typing import Dict, List, Optional

from src.core.language.adapter.contracts import (
    SUPPORTED_LANGUAGES,
    LanguageAdapter,
    UnsupportedLanguageError,
)

logger = logging.getLogger(__name__)


class LanguageDriverRegistry:
    """
    Thread-safe registry for language-specific adapters.
    
    Guarantees that:
    1. Only drivers for supported languages ('en', 'vi', 'ja') can be registered.
    2. Lookup for any unsupported language raises UnsupportedLanguageError immediately.
    """

    def __init__(self) -> None:
        self._drivers: Dict[str, LanguageAdapter] = {}
        self._lock = threading.RLock()

    def register_driver(self, lang: str, driver: LanguageAdapter) -> None:
        """
        Register a driver for a specific language code.
        
        Args:
            lang: ISO 639-1 language code ('en', 'vi', or 'ja').
            driver: LanguageAdapter instance.
            
        Raises:
            UnsupportedLanguageError: If the language is not in SUPPORTED_LANGUAGES.
            ValueError: If driver does not support the given language.
        """
        norm_lang = lang.strip().lower()
        if norm_lang not in SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                f"Cannot register driver for unsupported language '{norm_lang}'. "
                f"Supported languages are: {sorted(SUPPORTED_LANGUAGES)}"
            )

        if not driver.can_handle_language(norm_lang):
            raise ValueError(
                f"Driver {driver.__class__.__name__} reports it cannot handle '{norm_lang}'"
            )

        with self._lock:
            self._drivers[norm_lang] = driver
            logger.info("Registered LanguageAdapter %s for language '%s'", driver.__class__.__name__, norm_lang)

    def get_driver(self, lang: str) -> LanguageAdapter:
        """
        Retrieve the registered driver for the specified language.
        
        Args:
            lang: ISO 639-1 language code.
            
        Returns:
            LanguageAdapter instance.
            
        Raises:
            UnsupportedLanguageError: If language is unsupported or has no registered driver.
        """
        norm_lang = lang.strip().lower()
        if norm_lang not in SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                f"Language '{norm_lang}' is not supported. "
                f"Admitted languages: {sorted(SUPPORTED_LANGUAGES)}"
            )

        with self._lock:
            driver = self._drivers.get(norm_lang)
            if driver is None:
                raise UnsupportedLanguageError(
                    f"No LanguageAdapter registered for supported language '{norm_lang}'"
                )
            return driver

    def is_language_supported(self, lang: str) -> bool:
        """Check if a language code is admitted by policy."""
        return lang.strip().lower() in SUPPORTED_LANGUAGES

    def registered_languages(self) -> List[str]:
        """Return list of currently registered language codes."""
        with self._lock:
            return sorted(self._drivers.keys())

    @classmethod
    def create_default_registry(cls) -> LanguageDriverRegistry:
        """
        Factory to create a registry pre-populated with standard Lucia drivers (EN, VI, JA).
        """
        from src.core.language.adapter.drivers.english import EnglishLanguageDriver
        from src.core.language.adapter.drivers.japanese import JapaneseLanguageDriver
        from src.core.language.adapter.drivers.vietnamese import VietnameseLanguageDriver

        registry = cls()
        registry.register_driver("en", EnglishLanguageDriver())
        registry.register_driver("vi", VietnameseLanguageDriver())
        registry.register_driver("ja", JapaneseLanguageDriver())
        return registry
