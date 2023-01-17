import enum


class Status(enum.Enum):
    """
    Possible statuses of a plugin instance.
    """

    created = "created"
    waiting = "waiting"
    scheduled = "scheduled"
    started = "started"
    registeringFiles = "registeringFiles"
    finishedSuccessfully = "finishedSuccessfully"
    finishedWithError = "finishedWithError"
    cancelled = "cancelled"


class ParameterTypeName(enum.Enum):
    """
    Plugin parameter types.
    """

    string = "string"
    integer = "integer"
    float = "float"
    boolean = "boolean"
