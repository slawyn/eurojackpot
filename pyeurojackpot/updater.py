from utils import log

import datetime
from datetime import timedelta

import requests
from bs4 import  BeautifulSoup
import json

import urllib

import socket, ssl

MONTHS = ['','Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez',]
WEBSITE = 'https://www.lottoland.com/eurojackpot/zahlen-quoten/'


LOTTO_NUMBERS_ID = "l-results-lotto_numbers js-results-lotto_numbers"
LOTTO_NUMBERS_ID_ALT = "ll-lottery-balls"

DATE_REQUEST_FORMAT = "%02d-%02d-%4d"

MONTHS_ID = "dateSelect-selectDrawingsForYear-drawingsForYear"
YEARS_ID ="dateSelect-selectYearAndDrawing-drawingYearRange"
DATA_REQUEST  = {
	"dateSelect-selectYearAndDrawing": "dateSelect-selectYearAndDrawing",
	YEARS_ID: "2012",
	"javax.faces.ViewState": "stateless",
	"javax.faces.source": YEARS_ID,
	"javax.faces.partial.event": "change",
	"javax.faces.partial.execute": YEARS_ID  +" " +YEARS_ID,
	"javax.faces.partial.render": "dateSelect-selectDrawingsForYear-drawingsForYear",
	"javax.faces.behavior.event": "valueChange",
	"Body-Version": "1.210.2",
	"X-Skin": "lottoland",
	"javax.faces.partial.ajax": "true"
}

DATE_2DAYS_EUROJACKPOT = datetime.datetime(2022, 3, 25, 12, 00)
DATE_LOTTO_START = datetime.datetime(2012, 3, 23, 12, 00),

def check_website(date):
    """Gets date of last entry on WEBSITE

    Args:
        date (date): date for the entry
    Returns:
        bool (update): if new entries exist
    """
    update_required = False
    response = requests.get(WEBSITE)
    parsed_html = BeautifulSoup(response.text,"html.parser")

    years = parsed_html.find('select',attrs={'id':YEARS_ID})
    months = parsed_html.find('select',attrs={'id':MONTHS_ID})

    if years != None and months != None:
        years_txt = years.text
        months_txt = months.text

        try:
            entries = months_txt.split("\n")[1].replace(",",".")
            one_entry = entries.split(".")
            day = one_entry[1].strip()
            month = one_entry[2].strip()
            year = years_txt.split("\n")[0].strip()

            for i in range(len(MONTHS)):
                if month == MONTHS[i]:
                    page_date = datetime.datetime(int(year), int(i), int(day), 12, 0)
                    if date < page_date:
                        update_required = True
                        break
        except Exception as e:
             log("Problem:couldn't parse MONTHS and years ")
             log(e)
    else:
        log("Problem:couldn't get info from the page")

    return update_required



def fetch_numbers(date):
    """Gets numbers from the WEBSITE

    Args:
        date (date): date for the entry
    Returns:
        list (timestamps): numbers for date
    """
    lotto_numbers = None
    fmt_request_date = DATE_REQUEST_FORMAT % (date.day,date.month,date.year)
    try:
        response = requests.get(WEBSITE + fmt_request_date)
        parsed_html = BeautifulSoup(response.text,"html.parser")
        lottos = parsed_html.find('div',attrs={'class':LOTTO_NUMBERS_ID})

        if lottos != None and len(lottos.text.split()) == 7:
            lotto_numbers = lottos.text.strip().split()

        # New Data Container on the WEBSITE since 01.02.2021
        else:
            lottos = parsed_html.find(LOTTO_NUMBERS_ID_ALT)

            # Integer arrays
            nums = eval(lottos["numbers"] )
            nums.extend(eval(lottos["extranumbers"]))

            if len(nums) == 7:
                lotto_numbers = list(map(str, nums))

    except Exception as e:
        log(e)

    return lotto_numbers, fmt_request_date


def fetch_difference_db(database):
    """Gets difference between local database and entries from WEBSITE

    Args:
        dict (database): list of database entries
    Returns:
        list (timestamps): timestamps for the entries
        list (numbers): 7 numbers per entry
    """

    timestamps = []
    numbers = []

    # define request date
    end_date = datetime.datetime.today().replace(hour=12, minute=0, second=0, microsecond=0)
    if len(database) > 0:
        last_date = list(database.keys())[-1]
        day, month, year = last_date.split("-")
        request_date = datetime.datetime(int(year), int(month), int(day), 12, 0)
    else:
        request_date = DATE_LOTTO_START

    # Check for updates
    while request_date < end_date:
        fmt_start_date = ""
        lotto_numbers = ""

        # fetch numbers also for tuesday
        if request_date >= DATE_2DAYS_EUROJACKPOT:
            if request_date.weekday() == 4:
                request_date += timedelta(days=4)
                lotto_numbers, fmt_start_date = fetch_numbers(request_date)

            elif request_date.weekday() == 1:
                request_date += timedelta(days=3)
                lotto_numbers, fmt_start_date = fetch_numbers(request_date)
            else:
                request_date += timedelta(days=1)
                #request_date +=timedelta(days=1)
        else:
            request_date += timedelta(days=7)
            lotto_numbers, fmt_start_date = fetch_numbers(request_date)

        # Check if lotto numbers were obtained
        if lotto_numbers != None and lotto_numbers != "":
            timestamps.append(fmt_start_date)
            numbers.append(lotto_numbers)
            log("Updating database...  %s\t%s" %(fmt_start_date, str(lotto_numbers)))
        else:
            log("Problem: wrong lotto lotto_numbers for %s"%(fmt_start_date))

    return timestamps, numbers

