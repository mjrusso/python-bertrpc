class BERTRPCError(Exception):    
    def __init__(self, msg = None, klass = None, bt = []):
        Exception.__init__(self, msg)
        if type(msg) == type(list()):
            code, message = msg[0], msg[1:]
        else:
            code, message = [0, msg]
        self.code = code
        self.message = message
        self.klass = klass
        self.bt = bt
    
    def __str__(self):
        details = []
        if self.bt is not None and len(self.bt) > 0:
            details.append('Traceback:\n%s\n' % ('\n'.join(self.bt)))
        if self.klass is not None:
            details.append('Class: %s\n' % self.klass)
        if self.code is not None:
            details.append('Code: %s\n' % self.code)
        details.append('%s: %s' % (self.__class__.__name__, self.message))
        return ''.join(details)

    # override the python 2.6 DeprecationWarning re: 'message' property
    def _get_message(self): return self._message
    def _set_message(self, message): self._message = message
    message = property(_get_message, _set_message)
    

class RemoteError(BERTRPCError):
    pass


class ConnectionError(BERTRPCError):
    pass


class ReadTimeoutError(BERTRPCError):
    pass


class ProtocolError(BERTRPCError):
    NO_HEADER = [0, "Unable to read length header from server."]
    NO_DATA = [1, "Unable to read data from server."]


class ServerError(BERTRPCError):
    pass


class UserError(BERTRPCError):
    pass


class ProxyError(BERTRPCError):
    pass


class InvalidRequest(BERTRPCError):
    pass


class InvalidOption(BERTRPCError):
    pass
