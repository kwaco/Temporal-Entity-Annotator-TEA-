

from subprocess import Popen, PIPE, STDOUT

from py4j.java_collections import JavaArray
from py4j.java_gateway import JavaGateway

import re
import os
import time
import sys

from gateway import GateWayServer

class IXATokenizer:

    def __init__(self):

        print "calling constructor"

        #launches java gateway server.
        GateWayServer.launch_gateway()

        print "attempting to connect to py4j gateway"
        time.sleep(120)

        self.gateway = JavaGateway(eager_load=True)

        self.tokenizer = self.gateway.entry_point.getIXATokenizer()

    def tokenize(self, text):

        return self.tokenizer.tokenize(text)

if __name__ == "__main__":
    pass