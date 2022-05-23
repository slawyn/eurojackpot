from helpers import log

import datetime
from datetime import timedelta

import requests
from bs4 import  BeautifulSoup


class Updater:
    '''Scans the website for new entries and returns them

    '''
    months = ['','Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez',]
    website = 'https://www.lottoland.com/eurojackpot/zahlen-quoten/'
    monthsID = "dateSelect-selectDrawingsForYear-drawingsForYear"
    yearsID ="dateSelect-selectYearAndDrawing-drawingYearRange"

    date_format_request = "%02d-%02d-%4d"

    lotto_numbers_id = "l-results-lotto_numbers js-results-lotto_numbers"
    lotto_numbers_id_alt = "ll-lottery-balls"

    def check_website(date):
        '''Gets date of last entry on website

        Args:
            date  (formatted_date): date for the entry
        Returns:
            bool (update): if new entries exist
        '''
        update = False
        response = requests.get(Updater.website)
        parsedHTML = BeautifulSoup(response.text,"html.parser")

        yrs = parsedHTML.find('select',attrs={'id':Updater.yearsID})
        mts = parsedHTML.find('select',attrs={'id':Updater.monthsID})

        if yrs != None and mts != None:
            entriesYears = yrs.text
            entriesMonths = mts.text
            try:
                entriesSplit = entriesMonths.split("\n")[1].replace(",",".")
                oneEntry = entriesSplit.split(".")
                day = oneEntry[1].strip()
                month = oneEntry[2].strip()
                year = entriesYears.split("\n")[0].strip()

                for i in range(len(Updater.months)):
                    if month == Updater.months[i]:
                        pageDate = datetime.datetime(int(year),int(i),int(day),12,0)
                        if date <pageDate:
                            update = True
                            break
            except Exception as e:
                 log("Problem:couldn't parse months and years ")
                 log(e)
        else:
            log("Problem:couldn't get info from the page")
        return update


    def fetch_numbers(formatted_date):
        '''Gets numbers from the website

        Args:
            string  (formatted_date): date for the entry
        Returns:
            list (timestamps): numbers for date
        '''
        lotto_numbers = None
        try:
            response = requests.get(Updater.website + formatted_date)
            parsedHTML = BeautifulSoup(response.text,"html.parser")
            lottos = parsedHTML.find('div',attrs={'class':Updater.lotto_numbers_id})
            if lottos != None and len(lottos.text.split()) == 7:
                lotto_numbers = lottos.text.strip().split()

            # New Data Container on the website since 01.02.2021
            else:
                lottos = parsedHTML.find(Updater.lotto_numbers_id_alt)

                # Integer arrays
                nums = eval(lottos["numbers"] )
                nums.extend(eval(lottos["extranumbers"]))

                if len(nums) == 7:
                    lotto_numbers = list(map(str,nums))

        except Exception as e:
            log(e)

        return lotto_numbers


    def fetch_difference(db, start_date, today):
        '''Gets difference between local database and entries from website

        Args:
            list  (db): list of database entries
            date (start_date): start date for entries
            date (today): today's date
        Returns:
            list (timestamps): timestamps for the entries
            list (numbers): 7 numbers per entry
        '''
        timestamps = []
        numbers = []

        request_date = start_date #self.dateStartOfEuroJackpot-timedelta(days=7)
        if len(db) > 0:
            last_line = db[len(db)-1]
            last_date = last_line.split("\t")[0]
            day, month, year = last_date.split("-")
            request_date = datetime.datetime(int(year),int(month),int(day), 12, 0) + timedelta(days=7)

        # Check for updates
        update_required = Updater.check_website(request_date)
        if update_required:

            log("Updating database... ")
            while request_date < today:
                    start_date = Updater.date_format_request%(request_date.day,request_date.month,request_date.year)
                    ln = Updater.fetch_numbers(start_date)

                    if ln != "":
                        timestamps.append(start_date)
                        numbers.append(ln)

                        log(start_date+"\t"+str(ln))
                    else:
                        log("Problem: wrong lotto lotto_numbers for %s"%(start_date))
                        break

                    request_date = request_date + timedelta(days=7)

        else:
            log("Database is already up-to-date")


        return timestamps, numbers
