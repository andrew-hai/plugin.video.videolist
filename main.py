# -*- coding: utf-8 -*-
# Module: videolist
# Author: Melchenko A
# Created on: 26.04.2017
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib import urlencode
from urlparse import parse_qsl
import json, requests
import xbmc
import xbmcgui
import xbmcplugin

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

API_BASI_URL = 'http://videolist.com.ua/kodi/v1/videos'


def get_url(params):
  allowed_args = (
    'action',
    'directory_path',
    'name',
    'video_file_url'
  )
  args = dict((k, params[k]) for k in allowed_args if k in params.keys())

  return '{0}?{1}'.format(_url, urlencode(args))


def get_resources(params):
  url = API_BASI_URL + params['directory_path']
  allowed_params = (
    'sort_by'
  )
  filtered_params = dict((k, params[k]) for k in allowed_params if k in params.keys())
  resp = requests.get(url=url, params=filtered_params)

  return json.loads(resp.text)


def list_default_directories():
  # Get video default directories
  directories = get_resources({'directory_path': '/root_directory'})
  # Iterate through directories
  _render_directories_list(directories)


def list_directories(params):
  if params['name'] == 'search':
    skbd = xbmc.Keyboard()
    skbd.setHeading('Enter video name to search')
    skbd.doModal()
    if skbd.isConfirmed():
      params['search_text'] = skbd.getText()
      directories = get_resources(params)
      _render_directories_list(directories)
  else:
    directories = get_resources(params)
    _render_directories_list(directories)


def list_files(params):
  # Get the list of videos in the category.
  videos = get_resources(params)
  # Iterate through videos.
  _render_files_list(videos)


def _render_directories_list(directories):
  for directory in directories:
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=directory['label'])
    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    # Here we use the same image for all items for simplicity's sake.
    # In a real-life plugin you need to set each image accordingly.
    list_item.setArt({'thumb': directory['thumb'],
                      'icon': directory['thumb'],
                      'fanart': directory['thumb']})
    # Set additional info for the list item.
    # Here we use a category name for both properties for for simplicity's sake.
    # setInfo allows to set various information for an item.
    # For available properties see the following link:
    # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
    list_item.setInfo('video', {'title': directory['label'], 'genre': directory['name']})
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&category=Animals
    url = get_url(directory)
    # url = get_url(directory)
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_handle)


def _render_files_list(videos):
  for video in videos:
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=video['title'])
    # Set additional info for the list item.
    list_item.setInfo('video', {'title': video['title'], 'genre': 'search'})
    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    # Here we use the same image for all items for simplicity's sake.
    # In a real-life plugin you need to set each image accordingly.


    # list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
    list_item.setArt({'thumb': '', 'icon': '', 'fanart': ''})


    # Set 'IsPlayable' property to 'true'.
    # This is mandatory for playable items!
    list_item.setProperty('IsPlayable', 'true')
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
    url = get_url(video)
    # Add the list item to a virtual Kodi folder.
    # is_folder = False means that this item won't open any sub-list.
    is_folder = False
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(_handle)


def play_video(params):
  # Create a playable item with a path to play.
  play_item = xbmcgui.ListItem(path=params['video_file_url'])
  # Pass the item to the Kodi player.
  xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
  # Parse a URL-encoded paramstring to the dictionary of
  # {<parameter>: <value>} elements
  params = dict(parse_qsl(paramstring))
  # Check the parameters passed to the plugin
  if params:
    if params['action'] == 'list_directories':
      # Display the list of videos in a provided category.
      list_directories(params)
    elif params['action'] == 'list_files':
      # Display the list of videos in a provided category.
      list_files(params)
    elif params['action'] == 'play':
      # Play a video from a provided URL.
      play_video(params)
    else:
      # If the provided paramstring does not contain a supported action
      # we raise an exception. This helps to catch coding errors,
      # e.g. typos in action names.
      raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
  else:
    # If the plugin is called from Kodi UI without any parameters,
    # display the list of video categories
    list_default_directories()


if __name__ == '__main__':
  # Call the router function and pass the plugin call parameters to it.
  # We use string slicing to trim the leading '?' from the plugin call paramstring
  router(sys.argv[2][1:])
