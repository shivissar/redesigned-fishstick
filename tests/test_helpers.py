
import unittest
import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

import pandas as pd

# This is a bit of a hack to import the helpers module from the parent directory
import sys
sys.path.append(str(Path(__file__).parent.parent))
import helpers

class TestHelpers(unittest.TestCase):

    def test_normalize(self):
        self.assertEqual(helpers.normalize("  Hello World  "), "hello world")
        self.assertEqual(helpers.normalize(None), "")

    def test_schedule_from_box(self):
        today = datetime.date.today()
        self.assertEqual(helpers.schedule_from_box(1), today + datetime.timedelta(days=1))
        self.assertEqual(helpers.schedule_from_box(5), today + datetime.timedelta(days=15))
        self.assertEqual(helpers.schedule_from_box(99), today + datetime.timedelta(days=1)) # Test default

    @patch("helpers.today")
    def test_get_card_state(self, mock_today):
        mock_today.return_value = datetime.date(2023, 1, 1)
        progress = {"1": {"box": 2, "due": "2023-01-05"}}
        state = helpers.get_card_state(progress, 1)
        self.assertEqual(state["box"], 2)
        self.assertEqual(state["due"], "2023-01-05")

        # Test default state for a new card
        state = helpers.get_card_state(progress, 2)
        self.assertEqual(state["box"], 1)
        self.assertEqual(state["due"], "2023-01-01")

    def test_update_card_progress(self):
        progress = {}
        today = datetime.date.today()

        # Test correct answer
        helpers.update_card_progress(progress, 1, correct=True)
        self.assertEqual(progress["1"]["box"], 2)
        self.assertEqual(progress["1"]["due"], str(today + datetime.timedelta(days=2)))

        # Test incorrect answer
        helpers.update_card_progress(progress, 1, correct=False)
        self.assertEqual(progress["1"]["box"], 1)
        self.assertEqual(progress["1"]["due"], str(today + datetime.timedelta(days=1)))

    @patch("helpers.DECKS_DIR", Path("/fake/decks"))
    @patch("pandas.read_csv")
    def test_load_deck(self, mock_read_csv):
        mock_df = pd.DataFrame({"id": [1, 2], "tamil": ["வணக்கம்", "நன்றி"]})
        mock_read_csv.return_value = mock_df
        df = helpers.load_deck("my_deck")
        mock_read_csv.assert_called_with(Path("/fake/decks/my_deck.csv"))
        self.assertEqual(df["id"].dtype, "int")

if __name__ == "__main__":
    unittest.main()
