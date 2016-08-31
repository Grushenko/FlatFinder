import urllib2
import ConfigParser
from bs4 import BeautifulSoup
import smtplib
import time


class Finder(object):

    def __init__(self, url, cfg):
        self.url = url
        self.from_config(cfg)

    def from_config(self, cfg):
        conf = ConfigParser.RawConfigParser()
        conf.read(cfg)
        self.last = conf.get('general', 'last')
        self.sender = conf.get('smtp', 'from')
        self.rec = conf.get('smtp', 'to')

    def send_email(self, content):
        try:
            print('send', content)
            smtpObj = smtplib.SMTP('localhost')
            print(self.rec)
            smtpObj.sendmail(self.sender, [self.rec], content)
        except:
            print('dupa')


    def get_last_offer(self):
        return self.last


    def run(self):
        while True:
            t = self.get_last_offer()
            self.send_email(t)
            time.sleep(5)

if __name__ == "__main__":
    url = 'http://www.gumtree.pl/s-mieszkania-i-domy-do-wynajecia/warszawa/v1c9008l3200008p1'
    Finder(url, 'config').run()

