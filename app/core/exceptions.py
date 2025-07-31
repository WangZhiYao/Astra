from app.core.result_codes import ResultCode


class BusinessException(Exception):
    def __init__(self, result_code: ResultCode, detail: str = None):
        self.result_code = result_code
        self.detail = detail or result_code.message
