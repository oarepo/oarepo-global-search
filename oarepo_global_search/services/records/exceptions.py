class InvalidServicesError(Exception):
    def __init__(self, message="Could not find any valid service."):
        self.message = message
        super().__init__(self.message)
