import requests

from Finder import Finder


class OtoDomFinder(Finder):
    def __init__(self, data_dir, config_file, local=False, mx_user=None, mx_password=None):
        super(OtoDomFinder, self).__init__(data_dir, config_file, local, mx_user, mx_password)
        self.subject = 'OtoDom Offers: Mieszkania w Warszawie'
        self.log_file = 'found_otodom.txt'

    def update_remote_log(self, data):
        r = requests.post('http://flatfinder-grushenko.rhcloud.com/otodom_update', {'value': data})


if __name__ == "__main__":
    OtoDomFinder('./data/', 'config_otodom', True, 'wojciechgruszka@gmx.com', 'Gmx@WkNp13#').run()
