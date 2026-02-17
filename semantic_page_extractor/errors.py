class ExtractionError(Exception):
    def __init__(self, message: str, code: str = "EXTRACTION_FAILED") -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}
