

#!/usr/bin/env python3

import sys
import site

site.addsitedir('/var/www/html/docrepo/virtualenv/lib/python3.6/site-packages')

sys.path.insert(0, '/var/www/html/docrepo')

from ivoa_doc import app as application

