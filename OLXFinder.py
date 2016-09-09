from Finder import Finder


class OLXFinder(Finder):
    def __init__(self, data_dir, config_file, mx_user=None, mx_password=None):
        super(OLXFinder, self).__init__(data_dir, config_file, mx_user, mx_password)
        self.subject = 'OLX Offers: Mieszkania w Warszawie'

if __name__ == "__main__":
    OLXFinder('./data', 'config_olx').run()