from __future__ import annotations

import datetime as dt
import unittest

from sponsor_watch import (
    Article,
    Company,
    article_is_recent,
    dedupe_key,
    headline_without_publisher,
    strict_google_match,
)


def make_company(name: str = "United Wholesale Mortgage", **kwargs) -> Company:
    return Company(
        name=name,
        list_name="lenders",
        aliases=kwargs.get("aliases", []),
        official_domains=[],
        official_sources=[],
        strict_google_match=kwargs.get("strict_google_match", False),
    )


def make_article(company: Company, published: str | None) -> Article:
    title = "A current mortgage headline - Example Publisher"
    return Article(
        company=company,
        list_name=company.list_name,
        title=title,
        url="https://example.com/story",
        summary="",
        published=published,
        source_label="Google News RSS",
        source_url="https://news.google.com/rss",
        is_official=False,
        dedupe_key=dedupe_key(company, title, "https://example.com/story"),
    )


class FreshnessTests(unittest.TestCase):
    def test_rejects_old_article(self) -> None:
        article = make_article(make_company(), "2026-07-28")
        self.assertFalse(article_is_recent(article, 7, today=dt.date(2026, 9, 6)))

    def test_accepts_article_inside_window(self) -> None:
        article = make_article(make_company(), "2026-09-04")
        self.assertTrue(article_is_recent(article, 7, today=dt.date(2026, 9, 6)))

    def test_rejects_undated_article_by_default(self) -> None:
        self.assertFalse(article_is_recent(make_article(make_company(), None), 7))


class MatchingAndDedupeTests(unittest.TestCase):
    def test_alias_matches_as_a_complete_term(self) -> None:
        company = make_company(aliases=["UWM"], strict_google_match=True)
        self.assertTrue(strict_google_match(company, "Broker response to UWM", "mortgage news"))
        self.assertFalse(strict_google_match(company, "AUWMetrics report", "mortgage news"))

    def test_publisher_and_url_variants_share_a_dedupe_key(self) -> None:
        company = make_company()
        title = "Loan officer ranks in Top 25"
        first_title = headline_without_publisher(f"{title} - Yahoo Finance", "Yahoo Finance")
        second_title = headline_without_publisher(f"{title} - finance.yahoo.com", "finance.yahoo.com")
        first = dedupe_key(company, first_title, "https://news.google.com/one")
        second = dedupe_key(company, second_title, "https://news.google.com/two")
        self.assertEqual(first, second)

    def test_headline_dash_is_preserved_when_publisher_does_not_match(self) -> None:
        title = "Rates fall - September update"
        self.assertEqual(headline_without_publisher(title, "Mortgage News"), title)


if __name__ == "__main__":
    unittest.main()
