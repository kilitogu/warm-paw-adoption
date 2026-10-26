class BusinessException(Exception):
    """自定义的业务异常，用于主动抛出"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)