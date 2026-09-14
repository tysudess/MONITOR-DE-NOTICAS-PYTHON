from __future__ import annotations

from collections import Counter
from os import environ
from time import monotonic
from typing import Iterable

import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QLabel

from monitor_noticias.ui.home_dashboard import HomeDashboard


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_LATITUDE = -15.793889
WEATHER_LONGITUDE = -47.882778
WEATHER_REFRESH_SECONDS = 600.0


def count_news_last_24h(news: Iterable[object], *, now_ms: int) -> int:
    """Conta matérias pela data real de publicação nas últimas 24 horas."""
    cutoff = int(now_ms) - 86_400_000
    total = 0
    for item in news:
        try:
            published_ms = int(getattr(item, "date", 0) or 0)
        except (TypeError, ValueError):
            published_ms = 0
        if published_ms >= cutoff:
            total += 1
    return total


def top_news_sources(news: Iterable[object], limit: int = 10) -> list[tuple[str, int]]:
    """Retorna os veículos com mais matérias presentes no estado atual."""
    counts: Counter[str] = Counter()
    for item in news:
        source = str(getattr(item, "source", "") or "").strip()
        if source:
            counts[source] += 1
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].casefold()))[: max(0, int(limit))]


def format_top_sources(news: Iterable[object], limit: int = 10) -> str:
    ranking = top_news_sources(news, limit=limit)
    if not ranking:
        return "Nenhuma matéria encontrada ainda."
    return "\n".join(
        f"{position}. {source} — {count} matéria{'s' if count != 1 else ''}"
        for position, (source, count) in enumerate(ranking, start=1)
    )


class WeatherThread(QThread):
    succeeded = Signal(float)
    failed = Signal(str)

    def run(self) -> None:
        try:
            response = requests.get(
                WEATHER_URL,
                params={
                    "latitude": WEATHER_LATITUDE,
                    "longitude": WEATHER_LONGITUDE,
                    "current": "temperature_2m",
                    "timezone": "America/Sao_Paulo",
                    "forecast_days": 1,
                },
                timeout=6,
            )
            response.raise_for_status()
            payload = response.json()
            current = payload.get("current") or {}
            value = current.get("temperature_2m")
            if value is None:
                raise ValueError("temperature_2m ausente na resposta")
            self.succeeded.emit(float(value))
        except Exception as exc:  # clima nunca pode interromper o Monitor
            self.failed.emit(str(exc) or exc.__class__.__name__)


def _set_weather_success(page: HomeDashboard, temperature: float) -> None:
    page.weather_temp.setText(f"{round(temperature)}°C")
    page.weather_temp.setToolTip("Temperatura atual de Brasília - DF")


def _set_weather_failure(page: HomeDashboard, detail: str) -> None:
    page.weather_temp.setToolTip(f"Temperatura indisponível no momento: {detail}")


def _maybe_start_weather(page: HomeDashboard) -> None:
    # Testes/capturas offscreen não devem depender de internet externa.
    if environ.get("QT_QPA_PLATFORM", "").strip().lower() == "offscreen":
        return
    if environ.get("MONITOR_DISABLE_WEATHER", "").strip().lower() in {"1", "true", "yes"}:
        return

    worker = getattr(page, "_home_weather_thread", None)
    if worker is not None and worker.isRunning():
        return

    now = monotonic()
    last = float(getattr(page, "_home_weather_last_started", 0.0) or 0.0)
    if last and now - last < WEATHER_REFRESH_SECONDS:
        return

    page._home_weather_last_started = now
    worker = WeatherThread(page)
    page._home_weather_thread = worker
    worker.succeeded.connect(lambda value, p=page: _set_weather_success(p, value))
    worker.failed.connect(lambda detail, p=page: _set_weather_failure(p, detail))
    worker.finished.connect(lambda p=page: setattr(p, "_home_weather_thread", None))
    worker.start()


def install_home_runtime_features() -> None:
    """Acopla dados reais ao dashboard sem alterar controller, coletores ou banco."""
    if getattr(HomeDashboard, "_runtime_features_installed", False):
        return

    original_init = HomeDashboard.__init__
    original_refresh = HomeDashboard.refresh

    def patched_init(self: HomeDashboard, *args, **kwargs) -> None:
        original_init(self, *args, **kwargs)
        self._home_weather_thread = None
        self._home_weather_last_started = 0.0
        for label in self.findChildren(QLabel):
            if label.text() == "Principais fontes monitoradas pelo sistema.":
                label.setText("Top 10 de veículos por matérias encontradas.")
                break

    def patched_refresh(self: HomeDashboard, state) -> None:
        original_refresh(self, state)

        now_ms = int(__import__("time").time() * 1000)
        news_24h = count_news_last_24h(state.news, now_ms=now_ms)
        self.metric_cards["news"].value.setText(str(news_24h))
        self.summary_values["news"].setText(str(news_24h))

        self.bottom_content[0].setText(format_top_sources(state.news, limit=10))
        _maybe_start_weather(self)

    HomeDashboard.__init__ = patched_init
    HomeDashboard.refresh = patched_refresh
    HomeDashboard._runtime_features_installed = True
