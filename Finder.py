import codecs
import traceback
from abc import abstractmethod
import urllib2
import ConfigParser
import smtplib
import time

from lxml import etree
from urlparse import urlparse

import datetime


def to_int(s):
    res = '0'
    for c in s:
        if c.isdigit():
            res += c
    return int(res)


class Rule(object):
    def __init__(self, xpath):
        self.xpath = xpath

    @abstractmethod
    def check(self, tree):
        pass


class WordRule(Rule):
    def __init__(self, xpath, words):
        super(WordRule, self).__init__(xpath)
        self.words = words

    def check(self, tree):
        if not tree.xpath(self.xpath):
            return True

        offer_word = tree.xpath(self.xpath)[0].lower()
        print(offer_word)
        for word in [w.lower() for w in self.words]:
            if word in offer_word:
                print ('[OK] Word %s match' % word)
                return True
        print('[BAD] Word not match')
        return False


class NumberRule(Rule):
    def __init__(self, xpath, lower, upper):
        super(NumberRule, self).__init__(xpath)
        self.lower = lower
        self.upper = upper

    def check(self, tree):
        offer_number = to_int(tree.xpath(self.xpath)[0])
        print offer_number
        if self.upper >= offer_number >= self.lower:
            print("[OK] Number %d match" % offer_number)
            return True
        print("[BAD] Number not match")
        return False


class Finder(object):
    def __init__(self, data_dir, config_file, local=False, mx_user=None, mx_password=None):
        self.data_dir = data_dir
        self.config_file = config_file
        self.local = local
        self.HTML_parser = etree.HTMLParser()
        self.from_config()
        if mx_user:
            self.mx_user = mx_user
        if mx_password:
            self.mx_passwd = mx_password

        if not self.mx_user or not self.mx_passwd:
            raise Exception("No credentials")
        print self.url
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.url))
        self.tree = etree.parse(urllib2.urlopen(self.url), self.HTML_parser)
        self.processed = []
        self.subject = 'Blank subject, something is wrong'
        self.log_file = 'found.txt'

    def from_config(self):
        print 'Loading %s file' % self.config_file
        conf = ConfigParser.RawConfigParser()
        conf.readfp(codecs.open(self.data_dir + self.config_file, "r", "utf8"))
        print 'path: ' + self.data_dir + self.config_file
        self.url = conf.get('general', 'url')
        self.offers = conf.get('general', 'offers')
        self.xpath_price = conf.get('general', 'xpath_price')
        self.xpath_name = conf.get('general', 'xpath_name')
        self.xpath_district = conf.get('general', 'xpath_district')
        self.xpath_rooms = conf.get('general', 'xpath_rooms')

        self.interval = int(conf.get('general', 'interval'))
        self.sender = conf.get('smtp', 'from')
        self.rec = conf.get('smtp', 'to').split(',')

        if conf.has_option('smtp', 'mx_user'):
            self.mx_user = conf.get('smtp', 'mx_user')
        else:
            self.mx_user = None

        if conf.has_option('smtp', 'mx_password'):
            self.mx_passwd = conf.get('smtp', 'mx_password')
        else:
            self.mx_passwd = None

        self.parse_rules(conf)

    def parse_rules(self, conf):
        self.rules = []
        for section in conf.sections():
            if section.startswith('rule'):
                if conf.has_option(section, 'word'):
                    self.rules.append(WordRule(conf.get(section, 'xpath'), conf.get(section, 'word').split(',')))
                else:
                    lower = 0
                    upper = 100000
                    if conf.has_option(section, 'upper'):
                        upper = int(conf.get(section, 'upper'))
                    if conf.has_option(section, 'lower'):
                        lower = int(conf.get(section, 'lower'))
                    self.rules.append(NumberRule(conf.get(section, 'xpath'), lower, upper))

    def send_email(self, content):
        if not content:
            return

        for rec in self.rec:
            message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s\nFlatFinder by Wojciech Gruszka & Krystian Dowolski" % \
                      (self.sender, rec, self.subject, content)
            print "[MESSAGE] \n" + message
            try:
                server = smtplib.SMTP('mail.gmx.com', 587)
                server.ehlo()
                server.starttls()
                server.login(self.mx_user, self.mx_passwd)
                server.sendmail(self.sender, rec, message)
                server.quit()
                print "[OK] Message sent"
            except:
                print "Could not send message!"
                traceback.print_exc()
                pass

    def add_to_log(self, url, tree):
        date = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        price = '-'
        name = url
        rooms = '-'
        district = '-'
        try:
            price = str(to_int(tree.xpath(self.xpath_price)))
        except:
            pass
        try:
            name = tree.xpath(self.xpath_name)
            print name
        except:
            pass
        try:
            rooms = tree.xpath(self.xpath_rooms)[0] # first character
        except:
            pass
        try:
            district = tree.xpath(self.xpath_district)
        except:
            pass
        message = '|'.join((url, date, name, district, price, rooms))
        self.update_local_log(message)
        if self.local:
            self.update_remote_log(message)

    def update_local_log(self, data):
        with codecs.open(self.data_dir + self.log_file, 'a', 'utf-8') as log:
            log.write(data + '\n')

    def update_remote_log(self, data):
        return

    def process(self):
        self.tree = etree.parse(urllib2.urlopen(self.url), self.HTML_parser)
        hrefs = self.tree.xpath(self.offers)
        content = ''
        idx = -1
        for href in hrefs:
            full_url = self.domain + href
            idx += 1
            if full_url in self.processed:
                continue
            self.processed.insert(idx, full_url)
            if len(self.processed) >= 100:
                self.processed.pop()

            try:
                print full_url
                tree = etree.parse(urllib2.urlopen(full_url), self.HTML_parser)
            except urllib2.HTTPError:
                print "[ERROR] Parsing offer error"
                continue
            acc = True
            print full_url
            for rule in self.rules:
                if not rule.check(tree):
                    acc = False
                    break
            if acc:
                print "\t[FOUND] Found offer!"
                self.add_to_log(full_url, tree)
                content += full_url + '\n\n'
        self.send_email(content)

    def convert_log(self, f):
        old_log = ''
        with codecs.open(self.data_dir + f, 'r', 'utf-8') as old:
            old_log = old.read()
        for href in old_log.split('\n'):
            try:
                tree = etree.parse(urllib2.urlopen(href), self.HTML_parser)
                self.add_to_log(href, tree)
            except:
                pass

    def sleep(self):
        print 'sleep'
        time.sleep(self.interval)
        print 'wake'

    def run(self):
        # self.send_email("""
        # FlatFinder 0.1.0 init.
        # (c) 2016 Wojciech Gruszka
        # """)

        while True:
            self.process()
            self.sleep()
