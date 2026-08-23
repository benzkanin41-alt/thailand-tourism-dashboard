from __future__ import annotations

import unittest

from work.fetch_tourism_data import NewsFile, add_required_source_fallbacks, select_best_monthly_rows


def make_source(year: int, category_id: int, article_id: int, published: str) -> NewsFile:
    return NewsFile(
        year=year,
        category_id=category_id,
        article_id=article_id,
        article_nid=0,
        title=f"Tourism Statistics {year}",
        published=published,
        link_download="https://www.mots.go.th/source.xlsx",
        page_url="https://www.mots.go.th/news/category/817",
        file_url="https://www.mots.go.th/source.xlsx",
    )


def make_row(
    year: int,
    month: int,
    arrivals: int,
    article_id: int,
    published: str,
    month_count: int = 12,
    yoy_base: int | None = None,
) -> dict[str, object]:
    return {
        "year": year,
        "month": month,
        "date": f"{year}-{month:02d}-01",
        "arrivals": arrivals,
        "source_article_id": article_id,
        "source_year_month_count": month_count,
        "source_published": published,
        "source_yoy_base_arrivals": yoy_base,
    }


class SelectBestMonthlyRowsTests(unittest.TestCase):
    def test_comparison_block_does_not_replace_full_historical_month(self) -> None:
        historical = make_source(2025, 806, 100, "2026-01-06T00:00:00+00:00")
        current = make_source(2026, 817, 200, "2026-08-03T00:00:00+00:00")
        rows: list[dict[str, object]] = []

        for month in range(1, 13):
            rows.append(make_row(2025, month, 1_000 + month, 100, historical.published))
            adjusted = 800 if month == 6 else 1_000 + month
            rows.append(make_row(2025, month, adjusted, 200, current.published))

        for month in range(1, 8):
            yoy_base = 800 if month == 6 else 1_000 + month
            rows.append(
                make_row(
                    2026,
                    month,
                    2_000 + month,
                    200,
                    current.published,
                    month_count=7,
                    yoy_base=yoy_base,
                )
            )

        selected = select_best_monthly_rows(rows, [historical, current])
        by_period = {(int(row["year"]), int(row["month"])): row for row in selected}

        self.assertEqual(1_006, by_period[(2025, 6)]["arrivals"])
        self.assertEqual(100, by_period[(2025, 6)]["source_article_id"])
        self.assertEqual(200, by_period[(2026, 6)]["source_article_id"])
        self.assertEqual(800, by_period[(2026, 6)]["source_yoy_base_arrivals"])


class RequiredSourceFallbackTests(unittest.TestCase):
    def test_adds_missing_official_2014_workbook(self) -> None:
        sources = add_required_source_fallbacks([])
        by_article = {source.article_id: source for source in sources}

        self.assertIn(1891, by_article)
        self.assertEqual(2014, by_article[1891].year)
        self.assertEqual(476, by_article[1891].category_id)
        self.assertEqual(
            "https://www.mots.go.th/download/article/article_20171206120212.xlsx",
            by_article[1891].file_url,
        )

    def test_does_not_duplicate_existing_2014_workbook(self) -> None:
        existing = make_source(2014, 476, 1891, "2017-12-06T00:00:00.000Z")
        sources = add_required_source_fallbacks([existing])

        self.assertEqual(1, sum(source.article_id == 1891 for source in sources))


if __name__ == "__main__":
    unittest.main()
