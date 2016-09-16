import requests
import urllib2
from lxml import etree

from Finder import Finder


class OLXFinder(Finder):
    def __init__(self, data_dir, config_file, local=False, mx_user=None, mx_password=None):
        super(OLXFinder, self).__init__(data_dir, config_file, local, mx_user, mx_password)
        self.subject = 'OLX Offers: Mieszkania w Warszawie'
        self.log_file = 'found_olx.txt'

    def generate_hrefs(self, offers):
        print 'generate'
        hrefs = []
        for href in offers:
            if 'olx.pl' in href:
                hrefs.append(href)
        return hrefs

    def update_remote_log(self, data):
        requests.post('http://flatfinder-grushenko.rhcloud.com/olx_update', {'value': data})


if __name__ == "__main__":
    OLXFinder('./data/', 'config_olx', True, 'wojciechgruszka@gmx.com', 'Gmx@WkNp13#').run()
