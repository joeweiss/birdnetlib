class AudioFormatError(Exception):
    pass


class AnalyzerRuntimeWarning(Warning):
    pass


class IncompatibleAnalyzerError(Exception):
    def __init__(self, message):
        super().__init__(message)
