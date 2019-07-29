"""
mm_2019_ss_1_package
MolSSI Sumemr School Final Project.
"""

# Add imports here
from .mc import MC

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
