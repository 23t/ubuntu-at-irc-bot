#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bernd Essl <bernd@b23.at>

from random import shuffle
import httplib
import time
import subprocess
import re
try:
    import sqlite3
except ImportError:
    import sys
    print "Some plugins need the python sqlite3 extension"
    sys.exit(1)
try:
    import feedparser
except ImportError:
    import sys
    print "Some plugins need the python feedparser extension"
    sys.exit(1)


def salute_user(user_name):
    """
    Greet the user by random salutes.
    """
    salutes = ["Ahoy", "Hello", "Hola", "Servus"]
    shuffle(salutes)
    return salutes[0] + " " + user_name + "!"

def wiki_search(q):
    """
    Return URL from given query, to wiki page if exist.
    """
    DOMAIN = "wiki.ubuntuusers.de"
    conn = httplib.HTTPConnection(DOMAIN)
    conn.request("GET", "/%s" % q)
    r = conn.getresponse()
    if r.status == 200 and r.read() != "Fehlender Artikel":
        # Return URL to wiki page
        return "http://%s/%s" % (DOMAIN, q)
    return None

def get_user_data(user_name):
    """
    Get data from user by given ``user_name``.
    If user don't exist return ``None`.
    """
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    c.execute("SELECT id, desc FROM user_data WHERE name=? LIMIT 1;", (user_name,))
    res = c.fetchall()
    c.close()
    if len(res) == 1:
        return {'id' : res[0][0],
                'desc' : res[0][1]}
    return None

def update_user_description(user_name, user_desc):
    """
    Update descripton for user.
    If users don't exist create a new one.
    Return the new user description.
    """
    # Check if user exist
    user = get_user_data(user_name)
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    if user:
        # User exist, update entry
        c.execute("UPDATE user_data SET desc = ? WHERE id = ?;", (user_desc, user['id']))
    else:
        # User don't exist, create new entry
        c.execute("INSERT INTO user_data (id, name, desc) VALUES (NULL, ?, ?);", (user_name, user_desc))
    conn.commit()
    c.close()

def __whatis(appname):
    """
    Wrapper for the whatis unix command
    """
    # clean sonderzeichen from string
    appname = re.sub("\W", "", appname)
    cmd = "whatis %s" % (appname,)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if process.returncode == 0:
        return process.stdout.read()
    return None

def get_new_post():
    """
    Check board http://forum.ubuntu-at.com/ for new topics
    """
    RSSURL = "http://forum.ubuntu-at.com/rss.php"
    f = feedparser.parse(RSSURL)
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    c.execute("SELECT id FROM board WHERE url=? AND id=1;", (f.entries[0].link,))
    res = c.fetchall()
    if len(res) == 0:
        # link is new
        # update DB with id 1
        c.execute("UPDATE board SET url=? WHERE id=1;", (f.entries[0].link,))
        conn.commit()
        # and return new URL
        try:
            return "%s: %s %s" % (f.entries[0].author, f.entries[0].title, f.entries[0].link)
        except UnicodeEncodeError:
            # sometimes problems with umlaute
            return "%s: %s" % (f.entries[0].author, f.entries[0].link)
    c.close()

def get_beer(user_name):
    """
    Give the user, mostly gatewayer, a random beer
    """
    beer_list = ["Budweiser", "Murauer", "Puntigamer"]
    shuffle(beer_list)
    return "gebe %s ein %s aus" % (user_name, beer_list[0])

def get_lost_counter():
    """
    Returns days between today and the lost (TV show) release.
    """
    release_date = 1230850800
    return str(int (release_date - time.time()) / (60 * 60 * 24))
