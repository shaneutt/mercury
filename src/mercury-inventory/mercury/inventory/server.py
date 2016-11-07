# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import logging

from mercury.common import transport
from mercury.inventory.dispatch import Dispatcher

log = logging.getLogger(__name__)


class InventoryServer(transport.SimpleRouterReqService):
    def __init__(self, bind_address):
        super(InventoryServer, self).__init__(bind_address)

        self.dispatcher = Dispatcher()

    def process(self, message):
        return self.dispatcher.dispatch(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = InventoryServer('tcp://0.0.0.0:9000')
    s.bind()
    s.start()
