# -*- coding: utf-8 -*-
# author: Krystian Dowolski (krystian.dowolski@dealavo.com)

import urllib2

if __name__ == "__main__":
    a = urllib2.urlopen('http://api.fixer.io/latest').read()
    print(a)
