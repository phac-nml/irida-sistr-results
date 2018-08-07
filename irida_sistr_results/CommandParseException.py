class CommandParseException(Exception):
    """An Exception raised if there was an issue parsing some command-line options."""

    def __init__(self, msg):
        super().__init__(msg)
