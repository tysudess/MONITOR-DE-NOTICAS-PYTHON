from types import SimpleNamespace

from monitor_noticias.ui.home_runtime_features import (
    count_news_last_24h,
    format_top_sources,
    top_news_sources,
)


def test_count_news_last_24h_uses_publication_date() -> None:
    now_ms = 2_000_000_000_000
    items = [
        SimpleNamespace(date=now_ms - 1_000, source="A"),
        SimpleNamespace(date=now_ms - 86_399_999, source="B"),
        SimpleNamespace(date=now_ms - 86_400_001, source="C"),
        SimpleNamespace(date=0, source="D"),
    ]
    assert count_news_last_24h(items, now_ms=now_ms) == 2


def test_top_news_sources_orders_by_quantity_then_name() -> None:
    items = [
        SimpleNamespace(source="Veículo B"),
        SimpleNamespace(source="Veículo A"),
        SimpleNamespace(source="Veículo B"),
        SimpleNamespace(source="Veículo C"),
        SimpleNamespace(source="Veículo A"),
        SimpleNamespace(source="Veículo B"),
        SimpleNamespace(source=""),
    ]
    assert top_news_sources(items) == [
        ("Veículo B", 3),
        ("Veículo A", 2),
        ("Veículo C", 1),
    ]


def test_top_news_sources_is_limited_to_ten() -> None:
    items = [SimpleNamespace(source=f"Fonte {index:02d}") for index in range(15)]
    assert len(top_news_sources(items, limit=10)) == 10


def test_format_top_sources_includes_position_and_quantity() -> None:
    items = [SimpleNamespace(source="G1"), SimpleNamespace(source="G1"), SimpleNamespace(source="CNN Brasil")]
    text = format_top_sources(items)
    assert "1. G1 — 2 matérias" in text
    assert "2. CNN Brasil — 1 matéria" in text
