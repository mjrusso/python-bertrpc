BERTRPC
=======

A BERT-RPC client library for Python.  A port of Tom Preston-Werner's [Ruby library](http://github.com/mojombo/bertrpc).

See the full BERT-RPC specification at [bert-rpc.org](http://bert-rpc.org).

This library currently only supports the following BERT-RPC features:

* `call` requests
* `cast` requests

Installation
------------

Install from PyPI:

    easy_install bertrpc

Examples
--------

Import the library and create an RPC client:

    import bertrpc
    service = bertrpc.Service('localhost', 9999)

### Make a call:

    response = service.request('call').calc.add(1, 2)
    
Note that the underlying BERT-RPC transaction of the above call is:

    -> {call, calc, add, [1, 2]}
    <- {reply, 3}
    
In this example, the value of the `response` variable is `3`.

### Make a cast:

    service.request('cast').stats.incr()

Note that the underlying BERT-RPC transaction of the above cast is:

    -> {cast, stats, incr, []}
    <- {noreply}

The value of the `response` variable is `None` for all successful cast calls.

Running the unit tests
----------------------

To run the unit tests, execute the following command from the root of the project directory:

    python tests.py

Copyright
---------

Copyright (c) 2009 Michael J. Russo.  See LICENSE for details.