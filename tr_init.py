import os
import sys

"""
Initialize a new language
"""

if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .')
os.system('pybabel init -i messages.pot -d app/translations -l ' + sys.argv[1])
os.unlink('messages.pot')