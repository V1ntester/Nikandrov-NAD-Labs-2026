class Creator:
    _instance: "Creator | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._id = 1

        return cls._instance

    @property
    def id(self) -> int:
        return self._id


CREATOR = Creator()