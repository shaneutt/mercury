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

"""\
Functions for grabbing a MercuryID

MercuryID or mercury_id meta and hash value


[meta] - 00 = hash generated by interface mac addresses
         01 = hash generated by asset tag and serial number
"""
import hashlib
import logging

from mercury.common.exceptions import MercuryIdException

LOG = logging.getLogger(__name__)

META_TYPE_MAC = '00'
META_TYPE_PRODUCT_UUID = '01'
META_TYPE_CHASSIS_ASSET_SERIAL = '02'
META_TYPE_BOARD_ASSET_SERIAL = '03'


def _build_hash(target, meta_type):
    """Builds hash from target data and meta_type"""
    digest = hashlib.sha1(target.encode('ascii')).hexdigest()
    return meta_type + digest


def _get_embedded(inspected_interfaces):
    """Gets embedded interfaces from inspected interfaces."""
    embedded_interfaces = []
    for interface in inspected_interfaces:
        _biosdevname = interface['predictable_names'].get('biosdevname', '')
        if _biosdevname:
            if 'em' in _biosdevname:
                embedded_interfaces.append(interface)
    return embedded_interfaces


DMI_DISQUALIFIED_STRING = 'To Be Filled By O.E.M.'


def _dmi_methods(dmi):
    """Builds a mercury ID for DMI information if possible.

    :param dmi: A dictionary of DMI information from a system.
    :returns: A string if the right DMI is present, None otherwise.
    """
    product_uuid = dmi.get('product_uuid')
    chassis_asset_tag = dmi.get('chassis_asset_tag')
    chassis_serial = dmi.get('chassis_serial')
    board_asset_tag = dmi.get('board_asset_tag')
    board_serial = dmi.get('board_serial')

    if product_uuid:
        LOG.debug('Generating mercury ID using product_uuid: %s' % product_uuid)
        return _build_hash(product_uuid, META_TYPE_PRODUCT_UUID)

    if DMI_DISQUALIFIED_STRING in [chassis_asset_tag, chassis_serial,
                                   board_asset_tag, board_serial]:
        LOG.debug('Junk in DMI tables: \'%s\'' % DMI_DISQUALIFIED_STRING)
        return

    if chassis_asset_tag and chassis_serial:
        LOG.debug('Generating mercury ID using chassis asset information: tag=%s, asset=%s' % (
            chassis_asset_tag, chassis_serial))
        return _build_hash(chassis_asset_tag + chassis_serial, META_TYPE_CHASSIS_ASSET_SERIAL)

    if board_asset_tag and board_serial:
        LOG.debug('Generating mercury ID using board asset information: tag=%s, asset=%s' % (
                  board_asset_tag, board_serial))
        return _build_hash(board_asset_tag + board_serial, META_TYPE_BOARD_ASSET_SERIAL)


def generate_mercury_id(inspected_dmi, inspected_interfaces):
    """Generates a mercury ID based on gathered system information.

    :param inspected_dmi: A dictionary containing DMI information about
        the system in question.
    :param inspected_interfaces: A dictionary containing information about
        interfaces present in the system.
    :returns: A string representing the mercury ID.
    :raises MercuryIdException: If not enough information is present to
        generate an ID.
    """
    mercury_id = _dmi_methods(inspected_dmi)
    if mercury_id:
        return mercury_id
    else:
        meta_type = META_TYPE_MAC
        embedded = _get_embedded(inspected_interfaces)
        if embedded:
            LOG.debug('Generating mercury ID using embedded interfaces ')
            inspected_interfaces = embedded
        else:
            LOG.debug('Generating mercury ID using all interfaces')

        target = ''
        for interface in inspected_interfaces:
            address = interface.get('address')  # mac address
            if address:
                target += address

    if not target:
        raise MercuryIdException('Could not generate MercuryId')

    return _build_hash(target, meta_type)