from datetime import datetime

from mock import patch

from gittip.billing.payday import Payday
from gittip import testing
from gittip import wireup


# commaize

simplate = testing.load_simplate('/about/stats.html')
commaize = simplate.pages[0]['commaize']

def test_commaize_commaizes():
    actual = commaize(1000.0)
    assert actual == "1,000", actual

def test_commaize_commaizes_and_obeys_decimal_places():
    actual = commaize(1000, 4)
    assert actual == "1,000.0000", actual


# rendering

class TestStatsPage(testing.GittipBaseTest):

    def get_stats_page(self):
        response = testing.serve_request('/about/stats.html')
        return response.body

    def clear_paydays(self):
        "Clear all the existing paydays in the DB."
        from gittip import db
        db.execute("DELETE FROM paydays")

    @patch('datetime.datetime')
    def test_stats_description_accurate_during_payday_run(self, mock_datetime):
        """Test that stats page takes running payday into account.

        This test was originally written to expose the fix required for
        https://github.com/whit537/www.gittip.com/issues/92.
        """
        self.clear_paydays()
        a_thursday = datetime(2012, 8, 9, 12, 00, 01)
        mock_datetime.utcnow.return_value = a_thursday

        db = wireup.db()
        wireup.billing()
        pd = Payday(db)
        pd.start()

        body = self.get_stats_page()
        self.assertTrue("is changing hands <b>right now!</b>" in body)
        pd.end()

    @patch('datetime.datetime')
    def test_stats_description_accurate_outside_of_payday(self, mock_datetime):
        """Test stats page outside of the payday running"""
        self.clear_paydays()
        a_monday = datetime(2012, 8, 6, 12, 00, 01)
        mock_datetime.utcnow.return_value = a_monday

        db = wireup.db()
        wireup.billing()
        pd = Payday(db)
        pd.start()

        body = self.get_stats_page()
        self.assertTrue("is ready for <b>this Thursday</b>" in body)
        pd.end()
