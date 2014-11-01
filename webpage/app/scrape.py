import requests
import urllib
import datetime
import time
import pytz
from pytz import timezone
from datetime import datetime
from bs4 import BeautifulSoup

def get_content():
	# Get the month and week of month of today.
	date = datetime.now().date()
	year = date.year
	year = year % 2000  # only the last two digits of year.
	month = date.month
	padded_month = ("%02d" % month)
	day = date.day
	week_of_month = (day + 6/7)
	letter_for_week = chr(ord('a') + week_of_month - 1) # first week is A, etc.

	last_year = year
	last_month = month
	last_week = week_of_month - 1
	# Get the previous week.
	if week_of_month == 1:
		last_month = month - 1
		last_week = 5
		if month == 1:
			last_month = 12
			last_year = year - 1
		if last_month == 2:
			last_week = 4
	padded_last_month = ("%02d" % last_month)
	letter_for_last_week = chr(ord('a') + last_week - 1) # first week is A, etc.

	# Scrape for this week.
	listserv_url = 'https://listserv.dartmouth.edu/scripts/wa.exe?A1=ind' + str(year) + str(padded_month) + letter_for_week + '&L=CAMPUS-EVENTS&O=D&H=0&D=1&T=1'

	r = requests.get(listserv_url)
	soup = BeautifulSoup(r.text)
	events = []
	iterator = 0
	for link in soup.find_all('a'):
		if iterator > 0:
			break
		href = link.get('href')
		if href:
			if  '/scripts/wa.exe?A1=' in href:
   				r = requests.get('https://listserv.dartmouth.edu'+href)
   				soup2 = BeautifulSoup(r.text)
   				for event in soup2.find_all('a'):
   					if event.get('href'):
   						if '/scripts/wa.exe?A2=' in event.get('href'):
   							data = []
   							data.append(event.text)
   							data.append(urllib.quote_plus(event.get('href')))
   							events.append(data)
   				iterator = iterator + 1

   	# Scrape for last week
   	# NOTE: I will move this soup/link/event/iterator stuff into a separate function,
   	# once I know it is okay to do that.
   	listserv_url2 = 'https://listserv.dartmouth.edu/scripts/wa.exe?A1=ind' + str(last_year) + str(padded_last_month) + letter_for_last_week + '&L=CAMPUS-EVENTS&O=D&H=0&D=1&T=1'

	r = requests.get(listserv_url2)
	soup3 = BeautifulSoup(r.text)
	iterator = 0
	for link in soup3.find_all('a'):
		if iterator > 0:
			break
		href = link.get('href')
		if href:
			if  '/scripts/wa.exe?A1=' in href:
   				r = requests.get('https://listserv.dartmouth.edu'+href)
   				soup4 = BeautifulSoup(r.text)
   				for event in soup4.find_all('a'):
   					if event.get('href'):
   						if '/scripts/wa.exe?A2=' in event.get('href'):
   							data = []
   							data.append(event.text)
   							data.append(urllib.quote_plus(event.get('href')))
   							events.append(data)
   				iterator = iterator + 1
	return events

def get_event(event_url):
	#initialize vars
	url = ''
	txt = ''
	data = []
	event_url = ''+urllib.unquote_plus(event_url)
	event_subject = ''

	#get request
	r = requests.get('https://listserv.dartmouth.edu'+event_url)
	soup = BeautifulSoup(r.text)

	#get subject, from, and date
	event_subject = soup.find(text="Subject:").findNext('a').contents[0]
	event_from = soup.find(text="From:").findNext('p').contents[0].replace('<','')
	date = soup.find(text="Date:").findNext('p').contents[0].replace('<','')
	utc_dt = datetime.strptime(date.replace(' +0000',''),'%a, %d %b %Y %H:%M:%S').replace(tzinfo=pytz.utc)
	loc_dt = utc_dt.astimezone(timezone('US/Eastern'))
	event_date = loc_dt.strftime('%A, %b %d %I:%M%p')

	#get txt
	for link in soup.find_all('a'):
		if (link.get('href')):
			if (link.text == 'text/plain'):
				url = link.get('href')
				break
	if (url != ''):
		r = requests.get('https://listserv.dartmouth.edu'+url)
		soup = BeautifulSoup(r.text)
		for pre in soup.find_all('pre'):
			txt = pre.text

	#return all
	data.append(txt)
	data.append(event_subject)
	data.append(event_from)
	data.append(event_date)
	return data
