# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
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


# POC - single threaded ROUTER / REQ pattern
# TODO: Early code, needs cleaning

import logging
import msgpack
import zmq

from mercury.inventory.dispatch import Dispatcher

log = logging.getLogger(__name__)


class Server(object):
    # TODO: Use common.transport.SimpleRouterREQ
    def __init__(self, bind_address='tcp://0.0.0.0:9000'):
        self.bind_address = bind_address
        self.context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.socket = self.context.socket(zmq.ROUTER)
        self.bound = False
        self.dispatcher = Dispatcher()

    def bind(self):
        self.socket.bind(self.bind_address)
        log.info('Bound: %s' % self.bind_address)
        self.bound = True

    def receive(self):
        multipart = self.socket.recv_multipart()

        if len(multipart) != 3:
            log.error('Recieved request from wrong socket type, use REQ')

        address, empty, packed_message = multipart
        try:
            message = msgpack.unpackb(packed_message)
        except TypeError as type_error:
            self.send_error(address, 'Recieved unpacked, non-string type: %s : %s' % (type(packed_message), type_error))
            return
        except msgpack.UnpackException as unpack_exception:
            self.send_error(address, 'Received invalid request: %s' % str(unpack_exception))
            return

        return address, message

    def send_error(self, address, message):
        data = {'error': True, 'message': message}
        log.error(message)
        self.send(address, data)

    def send(self, address, message):
        self.socket.send_multipart([address, '', msgpack.packb(message)])

    def destroy(self):
        self.context.destroy()

    def start(self):
        if not self.bound:
            self.bind()

        while True:
            try:
                data = self.receive()
            except KeyboardInterrupt:
                break

            if not data:
                continue

            address, message = data
            log.debug('Request: %s' % address.encode('hex'))

            response = self.dispatcher.dispatch(message)
            log.debug('Response: %s' % address.encode('hex'))
            self.send(address, response)

        self.destroy()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = Server()
    s.bind()
    s.start()
