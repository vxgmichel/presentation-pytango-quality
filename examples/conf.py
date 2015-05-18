"""Sphinx configuration."""

# To find powersupply module
import sys, os
sys.path.insert(0, os.path.abspath('.'))

# Configuration
extensions = ['sphinx.ext.autodoc', 'devicedoc']
master_doc = 'index'

# Data
project = u'tango-device-motor'
copyright = u'2015, Tango Controls'
release = '1.0'
