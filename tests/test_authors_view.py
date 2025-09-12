import unittest
from unittest.mock import patch, MagicMock

from librium.views.views.authors import get_authors


class TestAuthorsView(unittest.TestCase):
    @patch("librium.views.views.authors.AuthorService.format_authors")
    @patch("librium.views.views.authors.get_raw")
    def test_get_authors_delegates_to_service_and_preserves_structure(
        self, mock_get_raw, mock_format_authors
    ):
        # Arrange: mock authors returned from get_raw and formatted output from service
        mock_author_obj = MagicMock()
        mock_get_raw.return_value = ([mock_author_obj], 3)  # items, pagination
        formatted = [
            {
                "author": "Alice Adams",
                "series": [
                    {
                        "series": "0",
                        "status": {"read": 1, "unread": 1},
                        "books": [
                            {
                                "book": "A",
                                "id": 1,
                                "year": 2000,
                                "read": True,
                                "idx": -1,
                                "uuid": "u1",
                            },
                            {
                                "book": "B",
                                "id": 2,
                                "year": 2001,
                                "read": False,
                                "idx": -1,
                                "uuid": "u2",
                            },
                        ],
                    }
                ],
                "books": [],
            }
        ]
        mock_format_authors.return_value = formatted

        # Act
        result = get_authors({})

        # Assert: pagination and authors keys present
        self.assertIn("authors", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"], 3)
        # Delegation to service for formatting
        mock_get_raw.assert_called_once()
        mock_format_authors.assert_called_once_with([mock_author_obj])
        # Structure preserved
        self.assertEqual(result["authors"], formatted)

    @patch("librium.services.author.SeriesService")
    @patch("librium.views.views.authors.AuthorService")
    @patch("librium.views.views.authors.get_raw")
    def test_formatting_keeps_functionality_series_and_standalone(
        self, mock_get_raw, mock_author_service, mock_series_service
    ):
        # Create fake books and relationships
        # Standalone books for author1
        book_s1 = MagicMock(
            title="Alpha", id=11, released=1999, read=True, uuid="uu1", series=[]
        )
        book_s2 = MagicMock(
            title="Beta", id=12, released=2000, read=False, uuid="uu2", series=[]
        )
        rel1 = type("BA", (), {"book": book_s1})()
        rel2 = type("BA", (), {"book": book_s2})()

        # Series books for author2 in series "Star"
        series_obj = MagicMock()
        series_obj.name = "Star"
        si = type("SI", (), {"series": series_obj, "idx": 2})()
        book_series = MagicMock(
            title="Star Rise", id=21, released=2005, read=True, uuid="uu3", series=[si]
        )
        rel3 = type("BA", (), {"book": book_series})()

        author1 = type(
            "Author", (), {"name": "Author One", "books": [rel1, rel2], "id": 101}
        )()
        author2 = type(
            "Author", (), {"name": "Author Two", "books": [rel3], "id": 102}
        )()

        # get_raw returns two authors
        mock_get_raw.return_value = ([author1, author2], 1)

        # SeriesService.get_all returns a list including our series name
        mock_series_service.get_all.return_value = [series_obj]

        # SeriesService.get_books_in_series returns books in the series
        mock_series_service.get_books_in_series.return_value = [
            # Note: author ID must match in authorship check; emulate structure: b.authors -> list with objects having author_id
            type(
                "Book",
                (),
                {"read": True, "authors": [type("BA", (), {"author_id": 102})()]},
            )()
        ]

        # The AuthorService.format_authors should be our real implementation; ensure we call the real method
        from librium.services.author import AuthorService as RealAuthorService

        mock_author_service.format_authors.side_effect = (
            RealAuthorService.format_authors
        )

        # Act
        result = get_authors({})

        # Assert result contains two authors
        self.assertEqual(len(result["authors"]), 2)

        # Author1 should have a "0" series with two books sorted by idx then title (both idx -1, so title sort)
        a1 = next(a for a in result["authors"] if a["author"] == "Author One")
        series_names = [s["series"] for s in a1["series"]]
        self.assertIn("0", series_names)
        zero_series = next(s for s in a1["series"] if s["series"] == "0")
        # read/unread counts for standalone should reflect one of each
        self.assertEqual(zero_series["status"], {"read": 1, "unread": 1})
        # Books sorted by title since idx is -1 for both
        titles = [b["book"] for b in zero_series["books"]]
        self.assertEqual(titles, ["Alpha", "Beta"])

        # Author2 should have no "0" series and have series "Star" with one book
        a2 = next(a for a in result["authors"] if a["author"] == "Author Two")
        series_names2 = [s["series"] for s in a2["series"]]
        self.assertNotIn("0", series_names2)
        self.assertIn("Star", series_names2)
        star_series = next(s for s in a2["series"] if s["series"] == "Star")
        self.assertEqual(star_series["status"], {"read": 1, "unread": 0})
        # Book preserved with idx and details
        self.assertEqual(len(star_series["books"]), 1)
        self.assertEqual(star_series["books"][0]["idx"], 2)


if __name__ == "__main__":
    unittest.main()
