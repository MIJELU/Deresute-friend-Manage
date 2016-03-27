#!/usr/bin/python
# -*- coding: utf-8 -*-
from drst import create_app
#import hashlib
#######################################

#print(hashlib.sha256(b"test").hexdigest())
#######################################

app = create_app()

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
