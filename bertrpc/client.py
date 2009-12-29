import bert
import error
import socket
import struct


class Service(object):
    def __init__(self, host, port, timeout = None):
        self.host = host
        self.port = port
        self.timeout = timeout

    def request(self, kind, options=None):
        if kind in ['call', 'cast']:
            self._verify_options(options)
            return Request(self, bert.Atom(kind), options)
        else:
            raise error.InvalidRequest('unsupported request of kind: "%s"' % kind)

    def _verify_options(self, options):
        if options is not None:
            cache = options.get('cache', None)
            if cache is not None:
                if len(cache) >= 2 and cache[0] == 'validation' and type(cache[1]) == type(str()):
                    pass
                else:
                    raise error.InvalidOption('Valid cache args are [validation, String]')
            else:
                raise error.InvalidOption('Valid options are: cache')
    
    
class Request(object):
    def __init__(self, service, kind, options):
        self.service = service
        self.kind = kind
        self.options = options

    def __getattr__(self, attr):
        return Module(self.service, self, bert.Atom(attr))
    
    
class Module(object):
    def __init__(self, service, request, module):
        self.service = service
        self.request = request
        self.module = module

    def __getattr__(self, attr):
        def callable(*args, **kwargs):
            return self.method_missing(attr, *args, **kwargs)
        return callable
    
    def method_missing(self, *args, **kwargs):
        return Action(self.service, 
                      self.request, 
                      self.module, 
                      bert.Atom(args[0]), 
                      list(args[1:])).execute()


class Action(object):    
    def __init__(self, service, request, module, function, arguments):
        self.service = service
        self.request = request
        self.module = module
        self.function = function
        self.arguments = arguments
            
    def execute(self):
        python_request = (self.request.kind, 
                          self.module, 
                          self.function, 
                          self.arguments)
        bert_request = Encoder().encode(python_request)
        bert_response = self._transaction(bert_request)
        python_response = Decoder().decode(bert_response)
        return python_response
        
    def _transaction(self, bert_request):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if self.service.timeout is not None: sock.settimeout(self.service.timeout)
            sock.connect((self.service.host, self.service.port))
            if self.request.options is not None:
                if self.request.options.get('cache', None) is not None:
                    if self.request.options['cache'][0] == 'validation':
                        token = self.request.options['cache'][1]
                        info_bert = Encoder().encode(
                            (bert.Atom('info'), bert.Atom('cache'), [bert.Atom('validation'), bert.Atom(token)]))
                        info_header = struct.pack(">l", len(info_bert))
                        sock.sendall(info_header)
                        sock.sendall(info_bert)
            header = struct.pack(">l", len(bert_request))
            sock.sendall(header)
            sock.sendall(bert_request)
            lenheader = sock.recv(4)
            if lenheader is None: raise error.ProtocolError(error.ProtocolError.NO_HEADER)
            length = struct.unpack(">l",lenheader)[0]
            bert_response = sock.recv(length)
            if bert_response is None or len(bert_response) == 0: raise error.ProtocolError(error.ProtocolError.NO_DATA)
            sock.close()
            return bert_response
        except socket.timeout, e:
            raise error.ReadTimeoutError('No response from %s:%s in %ss' % 
                (self.service.host, self.service.port, self.service.timeout))
        except socket.error, e:
            raise error.ConnectionError('Unable to connect to %s:%s' % (self.service.host, self.service.port))


class Encoder(object):
    def encode(self, python_request):
        return bert.encode(python_request)


class Decoder(object):
    def decode(self, bert_response):
        python_response = bert.decode(bert_response)
        if python_response[0] == bert.Atom('reply'):
            return python_response[1]
        elif python_response[0] == bert.Atom('noreply'):
            return None
        elif python_response[0] == bert.Atom('error'):
            return self._error(python_response[1])
        else:
            raise error.BERTRPCError('invalid response received from server')
        
    def _error(self, err):
        level, code, klass, message, backtrace = err
        exception_map = {
            bert.Atom('protocol'): error.ProtocolError,
            bert.Atom('server'): error.ServerError,
            bert.Atom('user'): error.UserError,
            bert.Atom('proxy'): error.ProxyError
        }
        exception = exception_map.get(level, None)
        if level is not None:
            raise exception([code, message], klass, backtrace)
        else:
            raise error.BERTRPCError('invalid error code received from server')


if __name__ == '__main__':
    print 'initializing service now'
    service = Service('localhost', 9999)
    
    print 'RPC call now'
    response = service.request('call').calc.add(1, 2)
    print 'response is: %s' % repr(response)

    print 'RPC call now, with options'
    options = {'cache': ['validation','myToken']}    
    response = service.request('call', options).calc.add(5, 6)
    print 'response is: %s' % repr(response)

    print 'RPC cast now'
    response = service.request('cast').stats.incr()
    print 'response is: %s' % repr(response)
