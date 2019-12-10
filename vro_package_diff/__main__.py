#!/usr/bin/env python
"""Provide a table-formated diff of two VMware vRealize Orchestrator packages.
"""

import zipfile, sys, os, logging

# external modules
from terminaltables import SingleTable, AsciiTable
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


def _stylize(text: str, color: str="", colorized: bool=True):
    """Print colored or uncolored text.

    Args:
        text (str): Text to print
        color (str): Color to use
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    if not colorized:
        return text
    else:
        return stylize(text, color)


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


def legend_print(ascii: bool=False, colorized: bool=True):
    """Print a legend at the end of diff table

    Args:
        ascii (bool): Use ASCII for output or not?
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    data = [["Legend", '']]
    pretty_table = SingleTable(data)
    legend = ""
    symbol_mode = "symbol_ascii"
    list_bullet = "*"  # •
    for loi in OUTPUT_SETUP.keys():
        legend += "{} {}  {}\n".format(
            list_bullet,
            _stylize(
                OUTPUT_SETUP[loi].get(symbol_mode),
                OUTPUT_SETUP[loi].get('color'),
                colorized
            ),
            OUTPUT_SETUP[loi].get('legend')
        )
    legend += "\nFor items with conflict:\n"
    legend += "   ‣ Check that the version in file A is lower than in the file B.\n"
    legend += "   ‣ If versions are the same, the content is not. Upgrade version on\n"
    legend += "     file B to overwrite item during the import process.\n"
    max_width = pretty_table.column_max_width(1)
    pretty_table.table_data[0][1] = legend
    print("\n%s" % pretty_table.table)


def table_pprint(lists_of_items_by_state: dict, ascii: bool=False, colorized: bool=True):
    """Generate and print a pretty table for output information.

    Args:
        lists_of_items_by_state (dict of VROElementMetadata[]): A dict of items, stored by
            import state
        ascii (bool): Use ASCII for output or not?
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    data = []
    title = "Diff betwenn packages"
    # Headers
    data.append(["ID", "Name", "Type", "Version B", "Result", "Version A"])
    symbol_mode = "symbol_utf8"
    if ascii:
        symbol_mode = "symbol_ascii"
    for loi in OUTPUT_SETUP.keys():
        for x in lists_of_items_by_state.get(loi, []):
            data.append([
                x.id, x.name, x.type,
                x.version, # Version B
                _stylize(
                    OUTPUT_SETUP[loi].get(symbol_mode),
                    OUTPUT_SETUP[loi].get('color'),
                    colorized
                ),
                x.comp_version # Version A
            ])
    if ascii:
        print(AsciiTable(data, title).table)
    else:
        print(SingleTable(data, title).table)


def diff_vro_items(items_src, items_dst, ascii: bool=False, colorized: bool=True):
    """Compare two vRO items lists

    Args:
        items_src (VROElementMetadata[]): Original list of vRO items
        items_dst (VROElementMetadata[]): Destination list of vRO items
        ascii (bool): Use ASCII for output or not?
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    lists_of_items_by_state = {
        'no_upgrade': [],
        'upgrade': [],
        'conflict': [],
        'new': [],
        'unsupported': []
    }
    for idst in items_dst:
        found = False
        if idst.type not in SUPPORTED_ELEMENT_TYPES:
            lists_of_items_by_state['unsupported'].append(idst)
        else:
            for isrc in items_src:
                if isrc.id == idst.id:
                    logger.debug("%s is IN source package" % idst)
                    found = True
                    idst.comp_version = isrc.version
                    if idst.version == "n/a":
                        lists_of_items_by_state['unsupported'].append(idst)
                    elif idst.version > isrc.version:
                        lists_of_items_by_state['upgrade'].append(idst)
                    elif idst.version < isrc.version:
                        logger.warning("Conflict detected on item: %s"  % idst)
                        lists_of_items_by_state['conflict'].append(idst)
                    elif idst.version == isrc.version:
                        if idst.checksum == isrc.checksum:
                            lists_of_items_by_state['no_upgrade'].append(idst)
                        else:
                            logger.warning("Conflict detected on item: %s" % idst)
                            lists_of_items_by_state['conflict'].append(idst)
            if (not found) and (idst.type in SUPPORTED_ELEMENT_TYPES):
                logger.debug("%s is NOT IN source package" % idst)
                lists_of_items_by_state['new'].append(idst)
    logger.info("File A: %d elements" % len(items_src))
    logger.info("File B: %d elements" % len(items_dst))
    logger.info("Items to upgrade:\t\t%d" % len(lists_of_items_by_state['upgrade']))
    logger.info("Items without upgrade:\t%d" % len(lists_of_items_by_state['no_upgrade']))
    logger.info("Items in upgrade conflict:\t%d" % len(lists_of_items_by_state['conflict']))
    logger.info("New items:\t\t\t%d" % len(lists_of_items_by_state['new']))
    logger.warning("Unsupported items:\t\t%d"% len(lists_of_items_by_state['unsupported']))
    total = (
        len(lists_of_items_by_state['unsupported'])
        +len(lists_of_items_by_state['upgrade'])
        +len(lists_of_items_by_state['no_upgrade'])
        +len(lists_of_items_by_state['conflict'])
        +len(lists_of_items_by_state['new'])
    )
    logger.info("Total items:\t\t\t%s" % total)
    table_pprint(lists_of_items_by_state, ascii=ascii, colorized=colorized)
    return len(lists_of_items_by_state['conflict'])


@click.command(context_settings=CLI_CONTEXT_SETTINGS)
@click.option('-l', '--legend', is_flag=True, help="Display the legend after the diff table")
@click.option('-t', '--test', is_flag=True,
    help="Exit with `0` if package can be safely imported. Else, returns the number of errors")
@click.option('-a', '--ascii', is_flag=True, help="Only use ASCII symbols to display results")
@click.option('-b', '--no_color', is_flag=True, help="Do not colorized the output")
@click.argument('reference_package', type=click.File('rb')) #, help="Reference package")
@click.argument('compared_package', type=click.File('rb')) #, help="Package to compare with")
def cli(reference_package: str, compared_package: str, legend: bool,
        test: bool, ascii: bool, no_color: bool):
    """Start a diff operation between two vRO packages.

    REFERENCE_PACKAGE is the package you want to use as source
    COMPARED_PACKAGE is the one you want to compare with reference one
    """
    logger.info("Reading items from the source package")
    vro_items_src = get_vroitems_from_package(reference_package)
    logger.info("Reading items from the destination package")
    vro_items_dst = get_vroitems_from_package(compared_package)
    logger.info("Starting the comparison of both contents")
    exit_code = diff_vro_items(vro_items_src, vro_items_dst, ascii=ascii, colorized=not no_color)
    if legend:
        logger.info("Legend display was requested.")
        legend_print(ascii=ascii, colorized=not no_color)
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
