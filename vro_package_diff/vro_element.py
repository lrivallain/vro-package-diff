#!/usr/bin/env python
"""Define VROElementMetadata object class
"""

import zipfile, sys, os, hashlib, io, logging
import xml.etree.ElementTree as ET

# local imports
from .config import *

logger = logging.getLogger(__name__)



class VROElementMetadata():
    """Abstract class to represent vRealize Orchestrator elements extracted from a vRO package.
    """

    def __init__(self, id: str, xml_info: bytes, data_content: bytes,
                xml_history: bytes):
        """Build a new VROElementMetadata object from id, xml_info, data_content, xml_history.

        Args:
            id (str): Object ID (from the folder name in zip-package file).
            xml_info (bytes): info file content.
            data_content (bytes): data file content (could be a nested zip file or an XML one).
            xml_history (bytes): version-history file content (XML).
        """
        self.name = None # populated with self.read_data later
        self.type = None # populated with self.read_data later
        self.version = None # populated with self.read_data later
        self.id = id
        self.type = self.get_item_type(xml_info)
        self.checksum = hashlib.sha1(data_content).hexdigest()
        self.comp_version = None
        if self.type in SUPPORTED_ELEMENT_TYPES:
            self.read_data(data_content)

    def __str__(self):
        """Define the string representation for object VROElementMetadata

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
        root = ET.fromstring(xml_str)
        for x in root.findall('entry'):
            if x.get('key') == "type":
                raw_type = x.text
        if raw_type in SUPPORTED_ELEMENT_TYPES:
            if raw_type == 'ScriptModule':
                return "Action" # rename scriptmodule --> action
            return raw_type
        else:
            logger.warning("Unsupported element type for item: %s (%s)" % (self.id, raw_type))
            return "Unsupported"

    def u_decode_plain_content(self, data: bytes):
        """UTF-16 or UTF-8 decoding of plain files.

        Args:
            data (bytes): content of a plain text file (XML/TXT...).

        Returns:
            str: a decoded version of the input data.
        """
        try:
            dec_data = data.decode('utf-16-be')
            logger.debug("UTF-16 decoding for item %s" % self.id)
        except UnicodeDecodeError:
            dec_data = data.decode('utf-8')
            logger.debug("UTF-8 decoding failed for item %s" % self.id)
        except:
            logger.error("Both UTF-16 and UTF-8 decoding failed for item %s" % self.id)
            dec_data = None
        return dec_data

    def read_data(self, data_content: bytes):
        """Read data content to extract object name.

        Populate self.name, self.version and self.type.

        Args:
            data_content (bytes): data file content (could be a nested zip file or an XML one).
        """
        self.name = "Unsupported: %s" % self.type # default value
        self.version = "n/a" # default value
        # specific case of nested zip file for resourcesElements
        if self.type == "ResourceElement":
            with zipfile.ZipFile(io.BytesIO(data_content),'r') as zip_data:
                with zip_data.open(os.path.join('VSO-RESOURCE-INF','attribute_name'),'r') as name_file:
                    self.name = name_file.read().decode('utf-8')
        elif self.type in SUPPORTED_ELEMENT_TYPES:
            dec_data_content = self.u_decode_plain_content(data_content)
            root = ET.fromstring(dec_data_content)
            self.version = root.get('version')
            if self.type == 'Workflow':
                namespaces = {'workflow': 'http://vmware.com/vco/workflow'}
                self.name = root.find('workflow:display-name', namespaces).text
            elif self.type == 'Action' or self.type == "ScriptModule":
                self.name = root.get('name')
            elif self.type == 'ConfigurationElement':
                self.name = root.find('display-name').text