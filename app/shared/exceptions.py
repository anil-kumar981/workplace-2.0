class AppException(Exception):
    """
    Base custom application exception class.
    Allows services and business layers to raise rich errors with custom status codes
    which are automatically caught and formatted by the global exception handler.
    """
    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
