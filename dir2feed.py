#!/usr/bin/env python

import dir2feedSettings
import os, sys, datetime
from stat import *

# this module comes from http://www.dalkescientific.com/Python/PyRSS2Gen.html
import PyRSS2Gen

# file list containing mtime and full local filesystem path
fileMtimeList = []

# nuke feed file before generating, just in case
if (os.path.exists(dir2feedSettings.feedFile)):
	os.remove(dir2feedSettings.feedFile)

# function adapted from Python 2.5 library documentation example
def walktree(top):
	for f in os.listdir(top):
		pathname = os.path.join(top, f)
		try:
			mode = os.stat(pathname)[ST_MODE]
			if S_ISDIR(mode):
				walktree(pathname)
			elif S_ISREG(mode):
				fileMtimeList.append({'pathname': pathname, 'mtime': os.stat(pathname)[ST_MTIME]})
		except OSError:
			# silently skip file read errors
			pass

walktree(dir2feedSettings.whichDir)

# sort according to mtime in descending order
fileMtimeList.sort(lambda x, y: cmp(y['mtime'], x['mtime']))

rss = PyRSS2Gen.RSS2(
	title = dir2feedSettings.feedTitle
	, link = dir2feedSettings.httpFeedFile
	, description = dir2feedSettings.feedDescription
	, lastBuildDate = datetime.datetime.now()
	, items = []
)

for i in range(dir2feedSettings.feedItemCount):
	try:
		httpFileLink = dir2feedSettings.httpPath + fileMtimeList[i]['pathname'].replace(dir2feedSettings.whichDir, '', 1)
		rss.items.append(PyRSS2Gen.RSSItem(
			title = os.path.basename(fileMtimeList[i]['pathname'])
			, link = httpFileLink
			, guid = PyRSS2Gen.Guid(httpFileLink)
			, pubDate = datetime.datetime.fromtimestamp(fileMtimeList[i]['mtime'])
		))
	except IndexError:
		# list had fewer items, just pass then
		pass

rss.write_xml(open(dir2feedSettings.feedFile, "w"), "utf-8")
