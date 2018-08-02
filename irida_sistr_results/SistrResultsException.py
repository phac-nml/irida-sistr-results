class SistrResultsException(Exception):
    """An Exception raised if there was an issue parsing SISTR results."""

    def __init__(self, msg):
        super().__init__(msg)
