from Finder import Finder


class GumTreeFinder(Finder):
    def __init__(self, data_dir, config_file, local=False, mx_user=None, mx_password=None):
        super(GumTreeFinder, self).__init__(data_dir, config_file, local, mx_user, mx_password)
        self.subject = 'GumTree Offers: Mieszkania w Warszawie'
        self.log_file = 'found_gumtree.txt'

    def generate_hrefs(self, offers):
        hrefs = []
        for href in offers:
            hrefs.append(self.domain + href)
        return hrefs


if __name__ == "__main__":
    GumTreeFinder('./data/', 'config_gumtree', True, ' ', ' ').run()
