#!/usr/bin/env python
"""Provide a table-formated diff of two VMware vRealize Orchestrator packages.
"""

import zipfile, sys, os, logging

# external modules
from terminaltables import SingleTable
import click

# Windows trick: no colored output
import platform
if platform.system().lower() == "windows":
    def stylize(text: str, color: str):
        """No color for windows users: sorry.

        Args:
            text (str): Text to print
            color (str): Unused color for text

        Returns:
            str: Text from input
        """
        return text
else:
    from colored import stylize

# local imports
from .config import *
from .vro_element import VROElementMetadata

# Configure logger
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    filename='diff.log',
                    filemode='w',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_vroitems_from_package(package):
    """Get all the items from the vRO Package.

    Args:
        package (str): Path to a package file.

    Returns:
        VROElementMetadata[]: a list of VROElementMetadata.
    """
    vro_items_id, vro_items = [], []
    with zipfile.ZipFile(package,'r') as zip_ref:
        for x in zip_ref.namelist():
            if x.startswith("elements"):
                item_id = os.path.basename(os.path.split(x)[0])
                if item_id not in vro_items_id:
                    with zip_ref.open('elements/' + item_id + '/info','r') as xml_info_file:
                        xml_info = xml_info_file.read()
                    with zip_ref.open('elements/' + item_id + '/data','r') as data_file:
                        data = data_file.read()
                    with zip_ref.open('elements/' + item_id + '/version-history','r') as xml_history_file:
                        xml_history = xml_history_file.read()
                    vro_item = VROElementMetadata(item_id, xml_info, data, xml_history)
                    vro_items.append(vro_item)
                    vro_items_id.append(item_id)
                    logger.info("New item %s" % vro_item)
    return vro_items


def legend_print():
    """Print a legend at the end of diff table
    """
    data = [["Legend", '']]
    pretty_table = SingleTable(data)
    legend = ("•%s  Items with no upgrade required"                % stylize(" ⇄ ", COLOR_NO_UPGRADE),
              "•%s  Items ignored in the vRO merge process"        % stylize(" ⇄ ", COLOR_UNSUPPORTED),
              "•%s  New items (will be imported)"                  % stylize(" + ", COLOR_NEW),
              "•%s  Items that will be upgraded in import process" % stylize(" ⇉ ", COLOR_UPGRADE),
              "•%s  Items with a version conflict"                 % stylize(" ≠ ", COLOR_CONFLICT),
              "       For items with conflict:",
              "       ‣ Check that the version in file A is lower than in the file B.",
              "       ‣ If versions are the same, the content is not. Upgrade version on",
              "         file B to overwrite item during the import process.")
    max_width = pretty_table.column_max_width(1)
    wrapped_legend = '\n'.join(legend)
    pretty_table.table_data[0][1] = wrapped_legend
    print("\n%s" % pretty_table.table)


def table_pprint(items_with_simple_upgrade, items_without_upgrade,
                items_with_conflict, new_items, ignored_items):
    """Generate and print a pretty table for output information.

    Args:
        items_with_simple_upgrade VROElementMetadata[]): list of items detected as upgradable.
        items_without_upgrade (VROElementMetadata[]): list of items detected as similar.
        items_with_conflict (VROElementMetadata[]): list of items detected with a version conflict.
        new_items (VROElementMetadata[]): list of items not present in source package.
        ignored_items (VROElementMetadata[]): list of package without import strategy.
    """
    data = []
    data.append(["ID", "Name", "Type", "Version B", "Result", "Version A"])
    for x in items_without_upgrade:
        data.append([x.id, x.name, x.type, x.version, stylize("  ⇄   ", COLOR_NO_UPGRADE),   x.comp_version])
    for x in ignored_items:
        data.append([x.id, x.name, x.type, "",        stylize("  ⇄   ", COLOR_UNSUPPORTED), ""])
    for x in new_items:
        data.append([x.id, x.name, x.type, x.version, stylize("  +   ", COLOR_NEW),         ""])
    for x in items_with_simple_upgrade:
        data.append([x.id, x.name, x.type, x.version, stylize("  ⇉   ", COLOR_UPGRADE),     x.comp_version])
    for x in items_with_conflict:
        data.append([x.id, x.name, x.type, x.version, stylize("  ≠   ", COLOR_CONFLICT),    x.comp_version])
    pretty_table = SingleTable(data, title="Diff betwenn packages")
    print(pretty_table.table)


def diff_vro_items(items_src, items_dst):
    """Compare two vRO items lists

    Args:
        items_src (VROElementMetadata[]): Original list of vRO items
        items_dst (VROElementMetadata[]): Destination list of vRO items
    """
    items_with_simple_upgrade = []
    items_without_upgrade = []
    items_with_conflict = []
    new_items = []
    ignored_items = []
    unknown_items = []
    for idst in items_dst:
        found = False
        if idst.type not in SUPPORTED_ELEMENT_TYPES:
            unknown_items.append(idst)
        else:
            for isrc in items_src:
                if isrc.id == idst.id:
                    logger.debug("%s is IN source package" % idst)
                    found = True
                    idst.comp_version = isrc.version
                    if idst.version == "n/a":
                        ignored_items.append(idst)
                    elif idst.version > isrc.version:
                        items_with_simple_upgrade.append(idst)
                    elif idst.version < isrc.version:
                        logger.warning("Conflict detected on item: %s"  % idst)
                        items_with_conflict.append(idst)
                    elif idst.version == isrc.version:
                        if idst.checksum == isrc.checksum:
                            items_without_upgrade.append(idst)
                        else:
                            logger.warning("Conflict detected on item: %s" % idst)
                            items_with_conflict.append(idst)
            if (not found) and (idst.type in SUPPORTED_ELEMENT_TYPES):
                logger.debug("%s is NOT IN source package" % idst)
                new_items.append(idst)
    logger.info("File A: %d elements" % len(items_src))
    logger.info("File B: %d elements" % len(items_dst))
    logger.info("Items to upgrade:\t\t%d" % len(items_with_simple_upgrade))
    logger.info("Items without upgrade:\t%d" % len(items_without_upgrade))
    logger.info("Items in upgrade conflict:\t%d" % len(items_with_conflict))
    logger.info("New items:\t\t\t%d" % len(new_items))
    logger.warning("Unknown items:\t\t%d"% len(unknown_items))
    total = (len(unknown_items)
            +len(items_with_simple_upgrade)
            +len(items_without_upgrade)
            +len(items_with_conflict)
            +len(new_items)
            +len(ignored_items))
    logger.info("Total items:\t\t\t%s" % total)
    table_pprint(items_with_simple_upgrade,
                items_without_upgrade,
                items_with_conflict,
                new_items,
                ignored_items)
    return len(items_with_conflict)


@click.command(context_settings=CLI_CONTEXT_SETTINGS)
@click.option('-l', '--legend', is_flag=True, help="Display the legend after the diff table")
@click.option('-t', '--test', is_flag=True,
    help="Exit with `0` if package can be safely imported. Else, returns the number of errors")
@click.argument('reference_package', type=click.File('rb')) #, help="Reference package")
@click.argument('compared_package', type=click.File('rb')) #, help="Package to compare with")
def cli(reference_package: str, compared_package: str, legend: bool, test: bool):
    """Start a diff operation between two vRO packages.

    REFERENCE_PACKAGE is the package you want to use as source
    COMPARED_PACKAGE is the one you want to compare with reference one
    """
    logger.info("Reading items from the source package")
    vro_items_src = get_vroitems_from_package(reference_package)
    logger.info("Reading items from the destination package")
    vro_items_dst = get_vroitems_from_package(compared_package)
    logger.info("Starting the comparison of both contents")
    exit_code = diff_vro_items(vro_items_src, vro_items_dst)
    if legend:
        logger.info("Legend display was requested.")
        legend_print()
    if test:
        logger.info("Exiting with number of conflicts:" + str(exit_code))
        exit(exit_code)
    logger.info("End of execution of the diff tool for vRO packages.")


def main():
    """Start the main diff process.
    """
    logger.info("Starting the diff tool for vRO packages.")
    cli(obj={})


if __name__ == '__main__':
    main()
