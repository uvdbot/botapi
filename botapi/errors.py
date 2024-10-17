class TelegramAPIError(Exception):
    def __init__(
        self,
        message: str,
        code: int,
        value: str = None
    ) -> None:
        self.message: str = message
        self.code: int = code
        self.value: str = value
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"