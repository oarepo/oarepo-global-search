class InvalidServicesError(Exception):
    def __init__(self, message="Could not find any valid service."):
        self.message = message
        super().__init__(self.message)


class PermissionDeniedError(Exception):
    def __init__(
        self,
        message="You do not have the required permissions to perform this operation.",
    ):
        self.message = message
        super().__init__(self.message)
