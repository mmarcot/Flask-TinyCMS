import os
import sys

'''
Compile the translations to the .mo file
'''

os.system('pybabel compile -d app/translations')