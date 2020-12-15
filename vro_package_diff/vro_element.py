#!/usr/bin/env python
"""Define VROElementMetadata object class."""

# default python modules
import hashlib
import io
import logging
import xml.etree.ElementTree as Etree
import zipfile

# third Party
from packaging import version

# local imports
from .config import SUPPORTED_ELEMENT_TYPES


logger = logging.getLogger(__name__)


class VROElementMetadata():
    """Abstract class to represent vRealize Orchestrator elements extracted from a vRO package."""

    def __init__(self, id: str, xml_info: bytes, data_content: bytes):
        """Build a new VROElementMetadata object from id, xml_info, data_content.

        Args:
            id (str): Object ID (from the folder name in zip-package file).
            xml_info (bytes): info file content.
            data_content (bytes): data file content (could be a nested zip file or an XML one).
        """
        self.name = None  # populated with self.read_data later
        self.type = None  # populated with self.read_data later
        self.version = version.parse("0.0.0")  # populated with self.read_data later
        self.dec_data_content = None  # populated with self.read_data later
        self.valued_items = 0  # populated in count_values_from_configuration_elt later
        self.id = id
        self.type = self.get_item_type(xml_info)
        self.comp_version = None
        if self.type in SUPPORTED_ELEMENT_TYPES:
            self.data_content = data_content
            self.read_data()
            self.checksum = hashlib.sha1(data_content).hexdigest()

    def __str__(self):
        """Define the string representation for object VROElementMetadata.

        Returns:
            str: string representation
        """
        return "[%s]%s" % (self.type, self.id)

    def get_item_type(self, xml_str: bytes):
        """Get the item type.

        Args:
            xml_str (bytes): The XML content for item info.

        Returns:
            str: The type name.
        """
        root = Etree.fromstring(xml_str)
        for x in root.findall('entry'):
            if x.get('key') == "type":
                raw_type = x.text
        if raw_type in SUPPORTED_ELEMENT_TYPES:
            if raw_type == 'ScriptModule':
                return "Action"  # rename scriptmodule --> action
            return raw_type
        else:
            logger.warning("Unsupported element type for item: %s (%s)" % (self.id, raw_type))
            return "Unsupported"

    def u_decode_plain_content(self):
        """UTF-16 or UTF-8 decoding of plain files.

        Returns:
            str: a decoded version of the input data.
        """
        try:
            dec_data = self.data_content.decode('utf-16-be')
            logger.debug("UTF-16 decoding for item %s" % self.id)
        except UnicodeDecodeError:
            try:
                dec_data = self.data_content.decode('utf-8')
                logger.debug("UTF-8 decoding failed for item %s" % self.id)
            except UnicodeDecodeError:
                logger.error("Both UTF-16 and UTF-8 decoding failed for item %s" % self.id)
                dec_data = None
        return dec_data

    def read_data(self):
        """Read data content to extract object name.

        Populate self.name, self.version and self.type.
        """
        self.name = "Unsupported: %s" % self.type  # default value
        self.version = "n/a"  # default value
        # specific case of nested zip file for resourcesElements
        if self.type == "ResourceElement":
            with zipfile.ZipFile(io.BytesIO(self.data_content), 'r') as zip_data:
                with zip_data.open('VSO-RESOURCE-INF/attribute_name', 'r') as name_file:
                    self.name = name_file.read().decode('utf-8')
                try:
                    with zip_data.open('VSO-RESOURCE-INF/attribute_version', 'r') as version_file:
                        _version = version_file.read().decode('utf-8')
                except KeyError:
                    _version = "0.0.0"
                self.version = version.parse(_version)
                with zip_data.open('VSO-RESOURCE-INF/data', 'r') as data_file:
                    self.data_content = data_file.read()
                    self.dec_data_content = self.u_decode_plain_content()
        elif self.type in SUPPORTED_ELEMENT_TYPES:
            self.dec_data_content = self.u_decode_plain_content()
            root = Etree.fromstring(self.dec_data_content)
            _version = root.get('version', "0.0.0")
            if self.type == 'Workflow':
                namespaces = {'workflow': 'http://vmware.com/vco/workflow'}
                self.name = root.find('workflow:display-name', namespaces).text
            elif self.type == 'Action' or self.type == "ScriptModule" or self.type == "PolicyTemplate":
                self.name = root.get('name')
            elif self.type == 'ConfigurationElement':
                self.name = root.find('display-name').text
            self.version = version.parse(_version)

    def count_values_from_configuration_elt(self):
        """Count the number of values found in a configurationElement.

        Returns:
            int: number of values found in the configurationElement items.
        """
        if not self.type == 'ConfigurationElement':
            logger.warn("Invalid type to count values in")
            return 0
        self.dec_data_content = self.u_decode_plain_content()
        root = Etree.fromstring(self.dec_data_content)
        atts = root.find('atts')
        for att in atts.findall('att'):
            if att.find('value') is not None:
                self.valued_items += 1
        logger.debug("Found %d values in %s" % (self.valued_items, self.name))
        return self.valued_items
