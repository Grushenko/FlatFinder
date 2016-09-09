from Finder import Finder


class GumTreeFinder(Finder):
    def __init__(self, data_dir, config_file, mx_user=None, mx_password=None):
        super(GumTreeFinder, self).__init__(data_dir, config_file, mx_user, mx_password)
        self.subject = 'GumTree Offers: Mieszkania w Warszawie'

if __name__ == "__main__":
    GumTreeFinder('./data', 'config_gumtree').run()
