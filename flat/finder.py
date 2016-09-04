from abc import abstractmethod
import urllib2
import os
import ConfigParser
from bs4 import BeautifulSoup
import smtplib
import time

from lxml import etree

from urlparse import urlparse

htmlparser = etree.HTMLParser()

class Rule(object):

    def __init__(self, xpath):
        self.xpath = xpath

    def to_int(s):
        res = '0'
        for c in s:
            if c.isdigit():
                res +=c
        return int(res)

    @abstractmethod
    def check(self, tree):
        pass


class WordRule(Rule):

    def __init__(self, xpath, words):
        super(WordRule, self).__init__(xpath)
        self.words = words

    def check(self, tree):
        offer_word = tree.xpath(self.xpath)[0].lower()
        print(offer_word)
        for word in [w.lower() for w in self.words]:
            if word in offer_word:
                print('work')
                return True
        return False


class NumberRule(Rule):

    def __init__(self, xpath, lower, upper):
        super(NumberRule, self).__init__(xpath)
        self.lower = lower
        self.upper = upper

    def check(self, tree):
        offer_number = self.to_int(tree.xpath(self.xpath)[0])
        if offer_number <= upper and offer_number >= lower:
            return True
        return False

class Finder(object):


    def __init__(self, cfg):
        conf = ConfigParser.RawConfigParser()
        conf.read(cfg)
        self.from_config(conf)
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.url))
        self.tree = etree.parse(urllib2.urlopen(self.url), htmlparser)
        self.processed = []

    def from_config(self, conf):
        self.url = conf.get('general', 'url')
        self.offers = conf.get('general', 'offers')
        self.sender = conf.get('smtp', 'from')
        self.rec = conf.get('smtp', 'to')
        self.parse_rules(conf)
        
    def parse_rules(self, conf):
        self.rules = []
        for section in conf.sections():
            if section.startswith('rule'):
                if conf.has_option(section, 'word'):
                    self.rules.append(WordRule(conf.get('rule1', 'xpath'), conf.get('rule1', 'word').split(',')))
                else:
                    lower = 0
                    upper = 100000
                    if conf.has_option(section, 'upper'):
                        upper = conf.get(section, 'upper')
                    if conf.has_option(section, 'lower'):
                        lower = conf.get(section, 'lower')
                    self.rules.append(Number(conf.get('rule1', 'xpath'), lower, upper))


    def send_email(self, content):
        print(content)
        if not content:
            return
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(self.sender, [self.rec], content)
        except:
            pass


    def run(self):
        while True:
            hrefs = self.tree.xpath(self.offers)
            content = ''
            for href in hrefs:
                full_url = self.domain + href
                if full_url in self.processed:
                    break
                self.processed.append(full_url)
                try:
                    tree = etree.parse(urllib2.urlopen(full_url), htmlparser)
                except urllib2.HTTPError:
                    continue
                acc = True
                for rule in self.rules:
                    if not rule.check(tree):
                        acc = False
                if acc:
                    content += full_url + '\n'
            self.send_email(content)
            time.sleep(60)

if __name__ == "__main__":
    Finder('config').run()
