class Message:
    """
    value: str
    """

    def process(self, tangle, node):
        ...

    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, data: dict):
        return cls(*data)
