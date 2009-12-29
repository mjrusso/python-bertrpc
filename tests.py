import bert
import bertrpc
import unittest


class TestService(unittest.TestCase):
    def testValidRequestInitializationNoTimeout(self):
        service = bertrpc.Service('localhost', 9999)
        service_with_timeout = bertrpc.Service('localhost', 9999, 12)
        self.assertEqual('localhost', service.host)
        self.assertEqual(9999, service.port)
        self.assertEqual(None, service.timeout)

    def testValidRequestInitializationWithTimeout(self):
        service = bertrpc.Service('localhost', 9999, 12)
        self.assertEqual('localhost', service.host)
        self.assertEqual(9999, service.port)
        self.assertEqual(12, service.timeout)

    def testInvalidRequestKind(self):
        service = bertrpc.Service('localhost', 9999)
        request_kind = 'jump' # valid options are 'call', 'cast', ...
        self.assertRaises(bertrpc.error.InvalidRequest, service.request, request_kind)

    def testValidRequestOptions(self):
        service = bertrpc.Service('localhost', 9999)
        options = {
            'cache': [
                'validation',
                'myToken'
            ]
        }
        request = service.request('call',options)
        self.assertEqual(options, request.options)
        
    def testInvalidRequestOptions(self):
        service = bertrpc.Service('localhost', 9999)
        options1 = {
            'fakeOption': 0
        }
        options2 = {
            'cache': [
                'validation',
                1234
            ]
        }
        self.assertRaises(bertrpc.error.InvalidOption, service.request, 'call', options1)
        self.assertRaises(bertrpc.error.InvalidOption, service.request, 'call', options2)


class TestEncodes(unittest.TestCase):
    def testRequestEncoder(self):
        bert_encoded = "\203h\004d\000\004calld\000\005mymodd\000\005myfunl\000\000\000\003a\001a\002a\003j"
        request = (bert.Atom('call'), bert.Atom('mymod'), bert.Atom('myfun'), [1, 2, 3])
        self.assertEqual(bert_encoded, bertrpc.client.Encoder().encode(request))
    

if __name__ == '__main__':
    unittest.main()
