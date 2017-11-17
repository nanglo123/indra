"""Read a list of files located in your local directory."""
from __future__ import absolute_import, print_function, unicode_literals
from builtins import dict, str

import logging
import pickle
import random
from os import path, getcwd

from indra.tools.reading.readers import _get_dir, get_readers
from indra.tools.reading.script_tools import get_parser, make_statements

logger = logging.getLogger('file_reader')


def read_files(files, readers, **kwargs):
    """Read the files in `files` with the reader objects in `readers`."""
    output_list = []
    for reader in readers:
        res_list = reader.read(files, **kwargs)
        if res_list is None:
            logger.info("Nothing read by %s." % reader.name)
        else:
            logger.info("Successfully read %d content entries with %s."
                        % (len(res_list), reader.name))
            output_list += res_list
    logger.info("Read %s text content entries in all." % len(output_list))
    return output_list


if __name__ == '__main__':
    parser = get_parser(
        __doc__,
        ('A file containing a list of files to be input into reach. These'
         'should be nxml or txt files. Cannot be used in conjunction with'
         ' -i/--id_file. For safest use, files should be given by '
         'absolute paths.')
        )
    args = parser.parse_args()
    if args.debug and not args.quiet:
        logger.setLevel(logging.DEBUG)

    with open(args.file_file, 'r') as f:
        input_lines = f.readlines()
    logger.info("Found %d files." % len(input_lines))
    for ftype in ['nxml', 'txt']:
        logger.debug('%d are %s' % (
            len([f for f in input_lines if f.endswith(ftype)]), ftype
            ))

    # Select only a sample of the lines, if sample is chosen.
    if args.sample is not None:
        input_lines = random.sample(input_lines, args.sample)

    # If a range is specified, only use that range.
    if args.in_range is not None:
        start_idx, end_idx = [int(n) for n in args.in_range.split(':')]
        input_lines = input_lines[start_idx:end_idx]

    # Create a single base directory
    base_dir = _get_dir('run_%s' % ('_and_'.join(args.readers)))

    # Set the verbosity. The quiet argument overrides the verbose argument.
    verbose = args.verbose and not args.quiet

    # Get the readers objects.
    readers = [reader_class(base_dir=base_dir, n_proc=args.num_procs)
               for reader_class in get_readers()
               if reader_class.name.lower() in args.readers]

    # Read the files.
    outputs = read_files(input_lines, readers, verboes=verbose)
    reading_out_path = path.join(getcwd(), 'file_reading_outputs.pkl')
    with open(reading_out_path, 'wb') as f:
        pickle.dump([output.make_tuple() for output in outputs], f)
    print("Reading outputs stored in %s." % reading_out_path)

    stmt_data_list = make_statements(outputs)
    stmts_pkl_path = path.join(getcwd(), 'file_reading_stmts.pkl')
    with open(stmts_pkl_path, 'wb') as f:
        pickle.dump([sd.statement for sd in stmt_data_list], f)
        print("Statements pickled in %s." % stmts_pkl_path)
