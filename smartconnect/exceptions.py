class SMARTClientException(Exception):
    pass

class SMARTClientServerError(SMARTClientException):
    pass

class SMARTClientServerUnreachableError(SMARTClientServerError):
    pass

class SMARTClientClientError(SMARTClientException):
    pass

class SMARTClientUnauthorizedError(SMARTClientClientError):
    pass


