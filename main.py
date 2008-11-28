#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bernd Essl <bernd@b23.at>

from settings import *
from plugins import *
from lib import botlib

class UbuntuBot(botlib.Bot):
    def __init__(self, server, channel, nick, password=None):
        botlib.Bot.__init__(self, server, 6667, channel, nick)

        # Send nickserv password if availible
        if password != None:
            self.protocol.privmsg("nickserv", "identify" % password)

    def __actions__(self):
        botlib.Bot.__actions__(self)

        # Print IRC traffic to stdout (for debbuging)
        if DEBUG:
            print self.data

        # Get the username
        user_name = self.get_username()

        # Scan forum for new postings (start on every IRC server ping)
        if botlib.check_found(self.data, "PING"):
            new_post = get_new_post()
            if new_post:
                self.protocol.privmsg(self.channel, "%s" % (new_post,))

        # Create a Hello World responder/command
        if botlib.check_found(self.data, "!hello"):
            # Send user a message in response
            self.protocol.privmsg(self.channel, "Hello %s!" % user_name)

        # Get lost counter
        if botlib.check_found(self.data, "!lost"):
            self.protocol.privmsg(self.channel, "%s Tage bis die neue Staffel von Lost kommt." % (get_lost_counter(),))

        # Get a beer 
        if botlib.check_found(self.data, "!bier"):
            lieferung = get_beer(self.get_username())
            # Send user a message in response
            self.protocol.privmsg(self.channel, "%s" % (lieferung,))

        # New user join channel
        # :b23!n=bernd@91.113.174.129 JOIN :#uboter23
        if botlib.check_found(self.data, "JOIN :" + self.channel):
            # Send welcome message to new joined user
            # Don't send welcome message when bot enter channel
            if user_name != self.nick:
                # Get user data by username
                user_description = get_user_data(user_name)
                if user_description:
                    # Send user description if one exist
                    self.protocol.privmsg(self.channel, "%s: %s" % (user_name, user_description['desc']))
                else:
                    # Send unknown user a welcome message
                    self.protocol.privmsg(self.channel, "Willkommen %s in %s" % (user_name, self.channel))

        # Description for user
        # User wants to update his description
        # example; !about text ueber mich
        if botlib.check_found(self.data, "PRIVMSG " + self.channel + " :!about"):
            # Get query
            description = self.data.split("!about")[1].strip()
            # Upadate new descripton 
            update_user_description(user_name, description)
            # Get new description
            user_description = get_user_data(user_name)
            self.protocol.privmsg(self.channel, "Update %s: %s" % (user_name, user_description['desc']))

        # Search on wiki.ubuntuusers.de
        if botlib.check_found(self.data, "PRIVMSG " + self.channel + " :!wiki"):
            # Get query
            q = self.data.split("!wiki")[1].strip()
            res = wiki_search(q)
            if res:
                self.protocol.privmsg(self.channel, "%s" % (res))
            else:
                self.protocol.privmsg(self.channel, "Nichts gefunden zu %s" % (q))

        # Salute user
        # example: hi <botname>
        if botlib.check_found(self.data, "PRIVMSG " + self.channel + " :hi " + self.nick):
            salute = salute_user(self.get_username())
            self.protocol.privmsg(self.channel, "%s" % (salute,))

        # wordcount by luke
        if botlib.check_found(self.data, "!tw"):
            for i in range(1,1):
                usr = get_word_count_top(i)
                self.protocol.privmsg(self.channel, "%s" % (usr,))

if __name__ == "__main__":
    # Create new instance of our bot and run it
    UbuntuBot(SERVER, CHANNEL, NAME).run()
