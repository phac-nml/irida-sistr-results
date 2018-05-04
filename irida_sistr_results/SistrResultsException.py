"""
An Exception raised if there was an issue parsing SISTR results.
"""

class SistrResultsException(Exception):

	def __init__(self, msg):
		super().__init__(msg)
