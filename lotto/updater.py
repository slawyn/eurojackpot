import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup

from .utils import log


class Updater:
    MONTHS = ['', 'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    WEBSITE = 'https://www.lottoland.com/eurojackpot/zahlen-quoten/'
    LOTTO_NUMBERS_ID_ALT = "ll-lottery-balls"
    DATE_FORMAT = "%02d-%02d-%4d"
    MONTHS_ID = "dateSelect-selectDrawingsForYear-drawingsForYear"
    YEARS_ID = "dateSelect-selectYearAndDrawing-drawingYearRange"
    DATE_2DAYS_EUROJACKPOT = datetime.datetime(2022, 3, 25, 12)
    DATE_LOTTO_START = datetime.datetime(2012, 3, 23, 12)

    def check_website(self, date):
        try:
            html = BeautifulSoup(requests.get(self.WEBSITE).text, "html.parser")
            years = html.find('select', {'id': self.YEARS_ID})
            months = html.find('select', {'id': self.MONTHS_ID})

            if not (years and months):
                log("Problem: couldn't get info from the page")
                return False

            day, month = months.text.split("\n")[1].replace(",", ".").split(".")[1:3]
            year = years.text.split("\n")[0].strip()

            month_index = self.MONTHS.index(month.strip())
            page_date = datetime.datetime(int(year), month_index, int(day.strip()), 12)

            return date < page_date
        except Exception as e:
            log("Problem: couldn't parse MONTHS and years")
            log(e)
            return False

    def _fetch_numbers(self, date):
        date_str = self.DATE_FORMAT % (date.day, date.month, date.year)
        soup = BeautifulSoup(requests.get(self.WEBSITE + date_str).text, "html.parser")

        parent_container = soup.find('ul', class_='l-lottery-numbers-container')
        if parent_container:
            # 2. If the container is found, find its child object with the class 'll-lottery-balls'
            child_object = parent_container.find('ll-lottery-balls')

            if child_object:
                nums = eval(child_object["numbers"]) + eval(child_object["extranumbers"])
                if len(nums) == 7:
                    return [int(n) for n in nums], date_str
                return [], date_str
            else:
                raise Exception("Child object with class 'll-lottery-balls' not found inside the container.")
        else:
            raise Exception("Parent container with id 'euroJackpot' not found.")

    def fetch(self, database):
        today = datetime.datetime.today().replace(hour=12, minute=0, second=0, microsecond=0)
        date = self._get_last_date(database)

        if date < today:
            next_date = self._next_draw_date(date)
            numbers, date_str = self._fetch_numbers(next_date)

            if numbers:
                log(f"Updating database... {date_str}\t{numbers}")
                return {date_str: numbers}
            else:
                log(f"Problem: wrong lotto numbers for {date_str} {numbers}")
        return {}

    def _get_last_date(self, db):
        if not db:
            return self.DATE_LOTTO_START
        day, month, year = map(int, list(db.keys())[-1].split("-"))
        return datetime.datetime(year, month, day, 12)

    def _next_draw_date(self, date):
        if date >= self.DATE_2DAYS_EUROJACKPOT:
            return date + timedelta(days={4: 4, 1: 3}.get(date.weekday(), 1))
        return date + timedelta(days=7)
