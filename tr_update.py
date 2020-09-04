import os

"""
Update the translations strings
"""

os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .')
os.system('pybabel update -i messages.pot -d app/translations')
os.unlink('messages.pot')