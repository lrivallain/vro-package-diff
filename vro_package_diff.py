#!/usr/bin/env python
"""Provide a table-formated diff of two vRealize Orchestrator packages.

Requirements: Python 3 and pip
"""

import zipfile, sys, os, hashlib, io, logging
import xml.etree.ElementTree as ET
from datetime import datetime
from textwrap import wrap

# external modules
from terminaltables import SingleTable
import colored
from colored import stylize

# Configure logger
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    filename='diff.log',
                    filemode='w',
                    level=logging.INFO)

# Currently support is limited to the following types of items
supported_element_types = [
    "Workflow",
    "ScriptModule", "Action",
    "ResourceElement",
    "ConfigurationElement"
]

# define output colors
_color_conflict    = colored.fg("red_1")
_color_noupgrade   = colored.fg("turquoise_2")
_color_upgrade     = colored.fg("chartreuse_2a")
_color_new         = colored.fg("yellow_1")
_color_nosupported = colored.fg("grey_78")



class VROElementMetadata:
    """
        VROElementMetadata is an abstract class to represent vRealize Orchestrator elements extracted
          from a vRO package.
    """
    def __init__(self, id, xml_info, data_content, xml_history):
        """Build a new VROElementMetadata object from id, xml_info, data_content, xml_history.

        id: the object ID (from the folder name in zip-package file).

        xml_info: info file content (XML).

        data_content: data file content (could be a nested zip file or an XML one).

        xml_history: version-history file content (XML).
        """
        self.id = id
        self.type = self.get_item_type(xml_info)
        self.checksum = hashlib.sha1(data_content).hexdigest()
        self.comp_version = None
        if self.type in supported_element_types:
            self.read_data(data_content)

    def __str__(self):
        return "[%s]%s" % (self.type, self.id)

    def get_item_type(self, xml_str):
        root = ET.fromstring(xml_str)
        for x in root.findall('entry'):
            if x.get('key') == "type":
                raw_type = x.text
        if raw_type in supported_element_types:
            if raw_type == 'ScriptModule':
                return "Action" # rename scriptmodule --> action
            return raw_type
        else:
            logging.warning("Unsupported element type for item: %s (%s)" % (self.id, raw_type))
            return "Unsupported"

    def u_decode_plain_content(self, data):
        """UTF-16 or UTF-8 decoding of plain files.

        data: content of a plain text file (XML/TXT...).
        """
        try:
            dec_data = data.decode('utf-16-be')
            logging.debug("UTF-16 decoding for item %s" % self.id)
        except UnicodeDecodeError:
            dec_data = data.decode('utf-8')
            logging.debug("UTF-8 decoding failed for item %s" % self.id)
        except:
            logging.error("UTF-XX decoding failed for item %s" % self.id)
            dec_data = None
        return dec_data

    def read_data(self, data_content):
        """Read data content to extract object name.

        data_content: data file content (could be a nested zip file or an XML one).
        """
        self.name = "NotSupported:%s" % self.type
        self.version = "n/a"
        # specific case of nested zip file for resourcesElements
        if self.type == "ResourceElement":
            with zipfile.ZipFile(io.BytesIO(data_content),'r') as zip_data:
                with zip_data.open(os.path.join('VSO-RESOURCE-INF','attribute_name'),'r') as name_file:
                    self.name = name_file.read().decode('utf-8')
        elif self.type in supported_element_types:
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


def get_vroitems_from_package(package):
    vro_items_id, vro_items = [], []
    with zipfile.ZipFile(package,'r') as zip_ref:
        for x in zip_ref.namelist():
            if x.startswith("elements"):
                item_id = os.path.basename(os.path.split(x)[0])
                if item_id not in vro_items_id:
                    with zip_ref.open(os.path.join('elements',item_id, 'info'),'r') as xml_info_file:
                        xml_info = xml_info_file.read()
                    with zip_ref.open(os.path.join('elements',item_id, 'data'),'r') as data_file:
                        data = data_file.read()
                    with zip_ref.open(os.path.join('elements',item_id, 'version-history'),'r') as xml_history_file:
                        xml_history = xml_history_file.read()
                    vro_item = VROElementMetadata(item_id, xml_info, data, xml_history)
                    vro_items.append(vro_item)
                    vro_items_id.append(item_id)
                    logging.info("New item %s" % vro_item)
    return vro_items


def legend_print():
    data = [["Legend", '']]
    pretty_table = SingleTable(data)
    legend = ("•%s  Items with no upgrade required"                % stylize(" ⇄ ", _color_noupgrade),
              "•%s  Items ignored in the vRO merge process"        % stylize(" ⇄ ", _color_nosupported),
              "•%s  New items (will be imported)"                  % stylize(" + ", _color_new),
              "•%s  Items that will be upgraded in import process" % stylize(" ⇉ ", _color_upgrade),
              "•%s  Items with a version conflict"                 % stylize(" ≠ ", _color_conflict),
              "       For items with conflict:",
              "       ‣ Check that the version in file A is lower than in the file B.",
              "       ‣ If versions are the same, the content is not. Upgrade version on file B to overwrite",
              "         item during the import process.")
    max_width = pretty_table.column_max_width(1)
    wrapped_legend = '\n'.join(legend)
    pretty_table.table_data[0][1] = wrapped_legend
    print("\n%s" % pretty_table.table)


def table_print(items_with_simple_upgrade, items_without_upgrade,
                items_with_conflict, new_items, ignored_items):
    """Pretty table formatter for output information.

    items_with_simple_upgrade: list of items detected as upgradable.

    items_without_upgrade: list of items detected as similar.

    items_with_conflict: list of items detected with a version conflict.

    new_items: list of items not present in source package.

    ignored_items: list of package without import strategy.
    """
    data = []
    data.append(["ID", "Name", "Type", "Version B", "Result", "Version A"])
    for x in items_without_upgrade:
        data.append([x.id, x.name, x.type, x.version, stylize("  ⇄   ", _color_noupgrade),   x.comp_version])
    for x in ignored_items:
        data.append([x.id, x.name, x.type, "",        stylize("  ⇄   ", _color_nosupported), ""])
    for x in new_items:
        data.append([x.id, x.name, x.type, x.version, stylize("  +   ", _color_new),         ""])
    for x in items_with_simple_upgrade:
        data.append([x.id, x.name, x.type, x.version, stylize("  ⇉   ", _color_upgrade),     x.comp_version])
    for x in items_with_conflict:
        data.append([x.id, x.name, x.type, x.version, stylize("  ≠   ", _color_conflict),    x.comp_version])
    pretty_table = SingleTable(data, title="Diff betwenn packages")
    print(pretty_table.table)
    legend_print()


def diff_vro_items(items_src, items_dst):
    items_with_simple_upgrade = []
    items_without_upgrade = []
    items_with_conflict = []
    new_items = []
    ignored_items = []
    unknown_items = []
    for idst in items_dst:
        found = False
        if idst.type not in supported_element_types:
            unknown_items.append(idst)
        else:
            for isrc in items_src:
                if isrc.id == idst.id:
                    logging.debug("%s is IN source package" % idst)
                    found = True
                    idst.comp_version = isrc.version
                    if idst.version == "n/a":
                        ignored_items.append(idst)
                    elif idst.version > isrc.version:
                        items_with_simple_upgrade.append(idst)
                    elif idst.version < isrc.version:
                        logging.warning("Conflict detected on item: %s"  % idst)
                        items_with_conflict.append(idst)
                    elif idst.version == isrc.version:
                        if idst.checksum == isrc.checksum:
                            items_without_upgrade.append(idst)
                        else:
                            logging.warning("Conflict detected on item: %s" % idst)
                            items_with_conflict.append(idst)
            if (not found) and (idst.type in supported_element_types):
                logging.debug("%s is NOT IN source package" % idst)
                new_items.append(idst)
    logging.info("File A: %d elements" % len(items_src))
    logging.info("File B: %d elements" % len(items_dst))
    logging.info("Items to upgrade:\t\t%d" % len(items_with_simple_upgrade))
    logging.info("Items without upgrade:\t%d" % len(items_without_upgrade))
    logging.info("Items in upgrade conflict:\t%d" % len(items_with_conflict))
    logging.info("New items:\t\t\t%d" % len(new_items))
    logging.warning("Unknown items:\t\t%d"% len(unknown_items))
    total = (len(unknown_items)
            +len(items_with_simple_upgrade)
            +len(items_without_upgrade)
            +len(items_with_conflict)
            +len(new_items)
            +len(ignored_items))
    logging.info("Total items:\t\t\t%s" % total)
    table_print(items_with_simple_upgrade,
                items_without_upgrade,
                items_with_conflict,
                new_items,
                ignored_items)

def usage():
    print("Usage:")
    print("    %s vropackageA.package vropackageB.package" % sys.argv[0])


def main():
    if len(sys.argv) != 3:
        print("Invalid parameters!\n")
        usage()
        exit(-1)
    vro_items_src = get_vroitems_from_package(sys.argv[1])
    vro_items_dst = get_vroitems_from_package(sys.argv[2])
    diff_vro_items(vro_items_src, vro_items_dst)
    exit()

if __name__ == '__main__':
    main()
