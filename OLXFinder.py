import urllib2
from lxml import etree
from Finder import Finder


class OLXFinder(Finder):
    def __init__(self, data_dir, config_file, mx_user=None, mx_password=None):
        super(OLXFinder, self).__init__(data_dir, config_file, mx_user, mx_password)
        self.subject = 'OLX Offers: Mieszkania w Warszawie'
        self.log_file = 'found_olx.txt'

    def process(self):
        self.tree = etree.parse(urllib2.urlopen(self.url), self.HTML_parser)
        hrefs = self.tree.xpath(self.offers)
        content = ''
        idx = -1
        for href in hrefs:
            idx += 1
            if 'olx.pl' not in href:
                self.add_to_log(href)
                content += 'Can not check: ' + href + '\n\n'
                self.processed.insert(idx, href)
                if len(self.processed) >= 100:
                    self.processed.pop()
                continue
            if href in self.processed:
                continue
            self.processed.insert(idx, href)
            if len(self.processed) >= 100:
                self.processed.pop()
            try:
                tree = etree.parse(urllib2.urlopen(href), self.HTML_parser)
            except urllib2.HTTPError:
                print "[ERROR] Parsing offer error"
                continue
            acc = True
            print href
            for rule in self.rules:
                if not rule.check(tree):
                    acc = False
                    break
            if acc:
                print "\t[FOUND] Found offer!"
                self.add_to_log(href)
                content += href + '\n\n'
        self.send_email(content)

if __name__ == "__main__":
    OLXFinder('./data/', 'config_olx').run()
