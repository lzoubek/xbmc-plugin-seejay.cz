# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import urllib2,re,os,random
import xbmcaddon,xbmc,xbmcgui,xbmcplugin

__scriptid__   = 'plugin.audio.seejay.cz'
__scriptname__ = 'seejay.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.seejay.cz/'

def parse_playlist(url):
	if url.endswith('m3u'):
		return request(url).strip()
	if not url.endswith('asx'):
		return url
	data = request(url)
	refs = re.compile('.*<Ref href = \"([^\"]+).*').findall(data,re.IGNORECASE|re.DOTALL|re.MULTILINE)
	urls = []
	for ref in refs:
		stream = parse_playlist(ref)
		urls.append(stream.replace(' ','%20'))
	if urls == []:
		print 'Unable to parse '+url
		print data
		return ''
	return urls[-1]

def request(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def add_dir(name,id,logo=''):
        u=sys.argv[0]+"?"+id
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=logo)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def substr(data,start,end):
	i1 = data.find(start)
	i2 = data.find(end,i1)
	return data[i1:i2]


def get_params():
        param={}
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
	return param

def add_stream(name,url,logo=''):
	url=sys.argv[0]+"?play="+url
	li=xbmcgui.ListItem(name,path = url,iconImage="DefaultAudio.png",thumbnailImage=logo)
        li.setInfo( type="Audio", infoLabels={ "Title": name} )
	li.setProperty("IsPlayable","true")
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def list_category(id):	
	data = request(BASE_URL+id)
	data = substr(data,'<div id=\"stt\">','</div>')
	streams = []
	for m in re.finditer('<a href(.+?)idx=(?P<id>\d+)[^>]+>(?P<name>[^<]+)', data, re.IGNORECASE | re.DOTALL):
		streams.append((m.group('name'),m.group('id')))
	streams.reverse()
	for name,id in streams:
		add_stream(name,id)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(id):
	if id.startswith('http'):
		url = parse_playlist(id)
	else:
		id_int = int(id)
		data = request(BASE_URL+'archiv.php?idx='+id)
		match = re.search('addVariable\(\"file\",\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
		if match:
			url = BASE_URL+match.group('url').lstrip('./')
	print 'Sending %s to player' % url
	li = xbmcgui.ListItem(path=url,iconImage='DefaultAudio.png')
	return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def list_streams():
	data = substr(request(BASE_URL+'jak-nas-naladit.html'),'<div id="page">','</div>')
	for m in re.finditer('<p>(.*?)<strong>(?P<name>[^<]+)(.+?)<a href=\"(?P<id>[^\"]+)[^>]+>', data, re.IGNORECASE | re.DOTALL):
		add_stream(m.group('name'),m.group('id'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def root():
	add_dir(__language__(30000),'streams=&')
	page = request(BASE_URL+'archiv')
	data = substr(page,'<div id=\"stt\">','<div id=\"rcol\"')
	for m in re.finditer('a(.+?)href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'),'cat='+m.group('url').lstrip('/'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

params=get_params()
if params=={}:
	root()
if 'streams' in params.keys():
	list_streams()
if 'cat' in params.keys():
	list_category(params['cat'])
if 'play' in params.keys():
	play(params['play'])
