#!/usr/bin/env python
"""Provide a table-formated diff of two VMware vRealize Orchestrator packages."""

# default python modules
import logging
import os
import platform
import zipfile
from difflib import unified_diff

# external modules
import click

from terminaltables import AsciiTable, SingleTable

# local imports
from .config import CLI_CONTEXT_SETTINGS, LOGGING_FILE, LOGGING_LEVEL_FILE, OUTPUT_SETUP, SUPPORTED_ELEMENT_TYPES
from .vro_element import VROElementMetadata

# Windows trick: no colored output
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

# Configure logger
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    filename=LOGGING_FILE,
                    filemode='w',
                    level=LOGGING_LEVEL_FILE)
logger = logging.getLogger(__name__)


def _stylize(text: str, color: str = "", colorized: bool = True):
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
    with zipfile.ZipFile(package, 'r') as zip_ref:
        for x in zip_ref.namelist():
            if x.startswith("elements"):
                item_id = os.path.basename(os.path.split(x)[0])
                if item_id not in vro_items_id:
                    with zip_ref.open('elements/' + item_id + '/info', 'r') as xml_info_file:
                        xml_info = xml_info_file.read()
                    with zip_ref.open('elements/' + item_id + '/data', 'r') as data_file:
                        data = data_file.read()
                    vro_item = VROElementMetadata(item_id, xml_info, data)
                    vro_items.append(vro_item)
                    vro_items_id.append(item_id)
                    logger.info("New item %s" % vro_item)
    return vro_items


def legend_print(ascii: bool = False, colorized: bool = True):
    """Print a legend at the end of diff table.

    Args:
        ascii (bool): Use ASCII for output or not? Defaults to False.
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    data = [["Legend", '']]
    pretty_table = SingleTable(data)
    legend = ""
    symbol_mode = "symbol_utf8"
    if ascii:
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
    legend += "   ‣ Version in package file is lower than in the reference package.\n"
    legend += "   ‣ If versions are the same, the content is not. Upgrade version on\n"
    legend += "     compared package to overwrite item during the import process.\n"
    pretty_table.table_data[0][1] = legend
    print("\n%s" % pretty_table.table)


def table_pprint(lists_of_items_by_state: dict, ascii: bool = False, colorized: bool = True):
    """Generate and print a pretty table for output information.

    Args:
        lists_of_items_by_state (dict of VROElementMetadata[]): A dict of items, stored by
            import state
        ascii (bool): Use ASCII for output or not? Defaults to False.
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    data = []
    title = "Diff betwenn packages"
    # Headers
    data.append(["ID", "Name", "Type", "Reference", "Package", "Result"])
    symbol_mode = "symbol_utf8"
    if ascii:
        symbol_mode = "symbol_ascii"
    for loi in OUTPUT_SETUP.keys():
        for element in lists_of_items_by_state.get(loi, []):
            data.append([
                element.id,
                element.name,
                element.type,
                element.comp_version,  # Reference version
                element.version,  # Package version
                _stylize(
                    OUTPUT_SETUP[loi].get(symbol_mode),
                    OUTPUT_SETUP[loi].get('color'),
                    colorized
                )
            ])
    if ascii:
        print(AsciiTable(data, title).table)
    else:
        print(SingleTable(data, title).table)


def unexpected_values_pprint(lists_of_items_by_state: dict, ascii: bool = False):
    """Generate and print a pretty table for output information.

    Args:
        lists_of_items_by_state (dict of VROElementMetadata[]): A dict of items, stored by
            import state
        ascii (bool): Use ASCII for output or not? Defaults to False.
        colorized (bool, optional): Use color or not?. Defaults to True.
    """
    if not lists_of_items_by_state['unexpected_values']:
        return
    data = []
    title = "Unexpected values in configurationElements"
    # Headers
    data.append(["ID", "Name", "Type", "Package", "Nb values"])
    for element in lists_of_items_by_state.get('unexpected_values', []):
        data.append([
            element.id,
            element.name,
            element.type,
            element.version,
            element.valued_items
        ])
    if ascii:
        print("\n" + AsciiTable(data, title).table)
    else:
        print("\n" + SingleTable(data, title).table)


def create_diff_file(src_elt: bytes, dst_elt: bytes, src_name: str, dst_name: str, diff_folder: str, state: str):
    """Create a diff file between two versions of element data_content.

    Args:
        src_elt (VROElementMetadata): Primary content.
        dst_elt (VROElementMetadata): Destination content.
        src_name (str): Name of the source content.
        dst_name (str): Name of the destination content.
        diff_folder (str): Destination folder to store diff files.
        state (str): State of the current item (used for sub folder)
    """
    if not (src_elt.dec_data_content and dst_elt.dec_data_content):
        logger.info("Ignoring (binary?) content for element with ID: %s" % src_elt.id)
        return
    logger.info("Creating a new diff file for element ID: %s" % src_elt.id)
    new_file_name = src_elt.id + ".diff"
    diff_folder_target = os.path.join(diff_folder, state, src_elt.type.lower())
    if not os.path.isdir(diff_folder_target):
        logger.debug("Creating a missing diff target folder: %s" % diff_folder_target)
        os.makedirs(diff_folder_target, exist_ok=True)
    with open(os.path.join(diff_folder_target, new_file_name), 'w', encoding='utf-8') as output_f:
        for line in unified_diff(
                src_elt.dec_data_content.splitlines(keepends=True),
                dst_elt.dec_data_content.splitlines(keepends=True),
                fromfile="%s - %s: %s (%s)" % (src_name, src_elt.type, src_elt.name, src_elt.version),
                tofile="%s - %s: %s (%s)" % (dst_name, dst_elt.type, dst_elt.name, dst_elt.version),
                n=3,
                lineterm='\n'):
            output_f.write(line)
    logger.info("End of diff file generation for the element with ID: %s" % src_elt.id)


def diff_vro_items(items_src,
                   items_dst,
                   reference_package: str,
                   compared_package: str,
                   ascii: bool = False,
                   colorized: bool = True,
                   diff_folder: bool = None,
                   empty_config: bool = True):
    """Compare two vRO items lists.

    Args:
        items_src (VROElementMetadata[]): Original list of vRO items.
        items_dst (VROElementMetadata[]): Destination list of vRO items.
        reference_package (str): package to use as source.
        compared_package (str): package to compare with reference one.
        ascii (bool): Use ASCII for output or not? Defaults to False.
        colorized (bool, optional): Use color or not?. Defaults to True.
        diff_folder (str, optional): Generate unified diff files output. Defaults to None.
    """
    lists_of_items_by_state = {
        'no_upgrade': [],
        'upgrade': [],
        'conflict': [],
        'new': [],
        'unsupported': [],
        'unexpected_values': []
    }
    for idst in items_dst:
        found = False
        if idst.type not in SUPPORTED_ELEMENT_TYPES:
            state = 'unsupported'
        else:
            for isrc in items_src:
                if isrc.id == idst.id:
                    logger.debug("%s is IN source package" % idst)
                    found = True
                    idst.comp_version = isrc.version
                    if idst.version == "n/a":
                        state = 'unsupported'
                    elif idst.version > isrc.version:
                        state = 'upgrade'
                    elif idst.version < isrc.version:
                        state = 'conflict'
                        logger.warning("Conflict detected on item: %s" % idst)
                    elif idst.version == isrc.version:
                        if idst.checksum == isrc.checksum:
                            state = 'no_upgrade'
                        else:
                            state = 'conflict'
                            logger.warning("Conflict detected on item: %s" % idst)
                    if diff_folder:
                        create_diff_file(
                            isrc,
                            idst,
                            src_name=reference_package,
                            dst_name=compared_package,
                            diff_folder=diff_folder,
                            state=state
                        )
            if (not found) and (idst.type in SUPPORTED_ELEMENT_TYPES):
                logger.debug("%s is NOT IN source package" % idst)
                state = 'new'
            if idst.type == "ConfigurationElement" and empty_config:
                if idst.count_values_from_configuration_elt():
                    lists_of_items_by_state['unexpected_values'].append(idst)
        lists_of_items_by_state[state].append(idst)
    logger.info("File A: %d elements" % len(items_src))
    logger.info("File B: %d elements" % len(items_dst))
    logger.info("Items to upgrade:\t\t%d" % len(lists_of_items_by_state['upgrade']))
    logger.info("Items without upgrade:\t%d" % len(lists_of_items_by_state['no_upgrade']))
    logger.info("Items in upgrade conflict:\t%d" % len(lists_of_items_by_state['conflict']))
    logger.info("New items:\t\t\t%d" % len(lists_of_items_by_state['new']))
    logger.info("ConfigurationElements with values:\t\t\t%d" % len(lists_of_items_by_state['unexpected_values']))
    logger.warning("Unsupported items:\t\t%d" % len(lists_of_items_by_state['unsupported']))
    total = (
        len(lists_of_items_by_state['unsupported'])
        + len(lists_of_items_by_state['upgrade'])
        + len(lists_of_items_by_state['no_upgrade'])
        + len(lists_of_items_by_state['conflict'])
        + len(lists_of_items_by_state['new'])
    )
    logger.info("Total items:\t\t\t%s" % total)
    table_pprint(lists_of_items_by_state, ascii=ascii, colorized=colorized)
    return lists_of_items_by_state


@click.command(context_settings=CLI_CONTEXT_SETTINGS)
@click.option('-r', '--reference_package',
              help="Reference package to compare your package with.",
              type=click.File('rb'),
              required=True)
@click.argument('compared_package',
                type=click.File('rb'))
@click.option('-l', '--legend',
              is_flag=True,
              help="Display the legend after the diff table")
@click.option('-t', '--test',
              is_flag=True,
              help="Exit with `0` if package can be safely imported. Else, returns the number of errors")
@click.option('-a', '--ascii',
              is_flag=True,
              help="Only use ASCII symbols to display results")
@click.option('-b', '--no_color',
              is_flag=True,
              help="Do not colorized the output")
@click.option('-d', '--diff',
              type=click.Path(dir_okay=True, resolve_path=True),
              help="A folder where to generate unified diff files output")
@click.option('-e', '--empty-config',
              is_flag=True,
              help="Check for values in the configuration elements: if so, exit with failure status.")
def cli(reference_package: str, compared_package: str, legend: bool = False,
        test: bool = False, ascii: bool = False, no_color: bool = False, diff: str = None,
        empty_config: bool = False):
    """Compare two vRealize Orchestrator packages.

    Use the [-r/--reference_package] option to specify the reference package.
    """
    logger.info("Reading items from the source package")
    vro_items_src = get_vroitems_from_package(reference_package)
    logger.info("Reading items from the destination package")
    vro_items_dst = get_vroitems_from_package(compared_package)
    logger.info("Starting the comparison of both contents")
    lists_of_items_by_state = diff_vro_items(
        vro_items_src,
        vro_items_dst,
        ascii=ascii,
        colorized=not no_color,
        diff_folder=diff,
        reference_package=reference_package.name,
        compared_package=compared_package.name
    )
    if legend:
        logger.info("Legend display was requested.")
        legend_print(ascii=ascii, colorized=not no_color)
    if diff:
        logger.info("Unified diff files are stored in: %s" % diff)
        print("Unified diff files are stored in: %s" % diff)
    exit_code = 0
    if test:
        logger.info("Exiting with number of conflicts:" + str(len(lists_of_items_by_state['conflict'])))
        exit_code += len(lists_of_items_by_state['conflict'])
    if empty_config:
        unexpected_values_pprint(lists_of_items_by_state, ascii=ascii)
        logger.info("Exiting with number of values in configurationElements")
        exit_code += len(lists_of_items_by_state['unexpected_values'])
    logger.info("End of execution of the diff tool for vRO packages.")
    exit(exit_code)


def main():
    """Start the main diff process."""
    logger.info("Starting the diff tool for vRO packages.")
    cli(obj={})


if __name__ == '__main__':
    main()
