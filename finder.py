import codecs
import traceback
from abc import abstractmethod
import urllib2
import ConfigParser
import smtplib
import time

from lxml import etree
from urlparse import urlparse

HTML_parser = etree.HTMLParser()


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
        if not tree.xpath(self.xpath)[0]:
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
    def __init__(self, cfg, mx_user = None, mx_password = None):
        conf = ConfigParser.RawConfigParser()
        conf.readfp(codecs.open(cfg, "r", "utf8"))
        self.from_config(conf)

        if mx_user:
            self.mx_user = mx_user
        if mx_password:
            self.mx_passwd = mx_user

        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.url))
        self.tree = etree.parse(urllib2.urlopen(self.url), HTML_parser)
        self.processed = []
        self.subject = "GumTree Offers: Mieszkania w Warszawie"

    def from_config(self, conf):
        self.url = conf.get('general', 'url')
        self.offers = conf.get('general', 'offers')
        self.sender = conf.get('smtp', 'from')
        self.rec = conf.get('smtp', 'to')
        if conf.has_option('smtp', 'mx_user'):
            self.mx_user = conf.get('smtp', 'mx_user')
        if conf.has_option('smtp', 'mx_password'):
            self.mx_passwd = conf.get('smtp', 'mx_password')

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
        message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s\nFlatFinder by Wojciech Gruszka & Krystian Dowolski" % \
                  (self.sender, self.rec, self.subject, content)
        print "[MESSAGE] \n" + message
        try:
            server = smtplib.SMTP('mail.gmx.com', 587)
            server.ehlo()
            server.starttls()
            server.login(self.mx_user, self.mx_passwd)
            server.sendmail(self.sender, self.rec, message)
            server.quit()
            print "[OK] Message sent"
        except:
            print "Could not send message!"
            traceback.print_exc()
            pass

    def run(self):

        # self.send_email("""
        # FlatFinder 0.1.0 init.
        # (c) 2016 Wojciech Gruszka
        # """)

        while True:
            hrefs = self.tree.xpath(self.offers)
            content = ''
            for href in hrefs:
                full_url = self.domain + href
                if full_url in self.processed:
                    continue
                self.processed.append(full_url)
                try:
                    tree = etree.parse(urllib2.urlopen(full_url), HTML_parser)
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
                    content += full_url + '\n\n'
            self.send_email(content)
            time.sleep(60)


if __name__ == "__main__":
    Finder('config').run()
