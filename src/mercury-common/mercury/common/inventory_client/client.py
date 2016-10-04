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

from mercury.common.exceptions import MercuryCritical
from mercury.common.transport import SimpleRouterReqClient


LOG = logging.getLogger(__name__)


class InventoryClient(SimpleRouterReqClient):
    @staticmethod
    def raise_reply_error(reply):
        raise MercuryCritical('Problem talking to inventory service: message = %s, tb = %s' % (
            reply.get('message'),
            '\n'.join(reply.get('tb', []))
        ))

    def check_and_return(self, reply):
        if reply.get('error'):
            self.raise_reply_error(reply)
        return reply['response']

    def insert_one(self, device_info):
        mercury_id = device_info.get('mercury_id')
        if not mercury_id:
            raise MercuryCritical('device_info is missing mercury_id')

        payload = {
            'endpoint': 'insert_one',
            'args': [device_info]
        }
        return self.check_and_return(self.transceiver(payload))

    def update_one(self, mercury_id, update_data):

        payload = {
            'endpoint': 'update_one',
            'args': [mercury_id],
            'kwargs': {'update_data': update_data}
        }

        return self.check_and_return(self.transceiver(payload))

    def get_one(self, mercury_id, projection=None):
        payload = {
            'endpoint': 'get_one',
            'args': [mercury_id],
            'kwargs': {
                'projection': projection
            }
        }
        return self.check_and_return(self.transceiver(payload))

    def query(self, query_data, projection=None, limit=0, sort_direction=1):
        payload = {
            'endpoint': 'query',
            'args': [query_data],
            'kwargs': {
                'projection': projection,
                'limit': limit,
                'sort_direction': sort_direction
            }
        }
        return self.check_and_return(self.transceiver(payload))

    def delete(self, mercury_id):
        payload = {
            'endpoint': 'delete',
            'args': [mercury_id]
        }
        return self.check_and_return(self.transceiver(payload))

    def count(self, query_data):
        payload = {
            'endpoint': 'count',
            'args': [query_data]
        }
        return self.check_and_return(self.transceiver(payload))

