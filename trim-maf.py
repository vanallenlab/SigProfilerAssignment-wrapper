import argparse
import glob
import pandas as pd
import subprocess
import sys


CHROMOSOME = 'chromosome'
START = 'start_position'
END = 'end_position'
REF = 'reference_allele'
ALT1 = 'tumor_seq_allele1'
ALT2 = 'tumor_seq_allele2'
TYPE = 'variant_type'
SAMPLE = 'tumor_sample_barcode'

COLUMN_MAP = {
    CHROMOSOME: 'Chrom',
    START: 'Start',
    END: 'End',
    TYPE: 'Type',
    REF: 'Ref',
    ALT1: 'Alt1',
    ALT2: 'Alt2',
    SAMPLE: 'Tumor_sample'
}

ALL_COLUMNS = [
    'Hugo', 'Entrez', 'Center', 'Genome',
    'Chrom', 'Start', 'End', 'Strand', 'Classification', 'Type', 'Ref', 'Alt1', 'Alt2',
    'dbSNP', 'SNP_Val_status',
    'Tumor_sample'
]

EMPTY_COLUMNS = [column for column in ALL_COLUMNS if column not in COLUMN_MAP.values()]


def create_folder_if_does_not_exist(folder):
    command = f"mkdir -p {folder}"
    subprocess.call(command, shell=True)


def read_file(file):
    df = pd.read_csv(
            file,
            sep='\t',
            comment='#',
            encoding='latin-1',
            usecols=(lambda x: str.lower(str(x)) in COLUMN_MAP.keys())
    )
    df.columns = df.columns.str.lower()
    return df.rename(columns=COLUMN_MAP)


def write_file(dataframe, output_name):
    dataframe.to_csv(output_name, sep='\t', index=False)


def process_file(file, suffix, output_folder):
    df = read_file(file)
    for column in EMPTY_COLUMNS:
        df[column] = '.'
    df = df[ALL_COLUMNS]

    output_name = file.split('/')[-1]
    if suffix:
        output_name = output_name.split('.')[0]
        output_name = f"{output_name}.{suffix.replace('.', '')}"
    if output_folder:
        create_folder_if_does_not_exist(output_folder)
        folder = output_folder.rstrip('/')
        output_name = f"{folder}/{output_name}"

    write_file(df, output_name)


def process_folder(input_folder, suffix, output_folder):
    input_folder = input_folder.rstrip('/')
    files = glob.glob(f"{input_folder}/*")
    for file in files:
        process_file(file, suffix, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Trim MAF',
        description='Trim MAF to minimal columns for use with signature generation'
    )
    parser.add_argument(
        '--mode',
        '-m',
        required=True,
        choices=['file', 'folder'],
        help='Specify if an individual file or folder containing many files should be trimmed'
    )
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='individual MAF file or folder containing at least one MAF file, depending on --mode'
    )
    parser.add_argument(
        '--output-folder',
        '-o',
        default=None,
        help='Will place outputs in specified folder'
    )
    parser.add_argument(
        '--output-suffix',
        '-s',
        default="maf",
        help='Will strip file name suffix and replace with, ".maf"'
    )

    args = parser.parse_args()
    if args.mode == 'file':
        process_file(args.input, args.output_suffix, args.output_folder)
    elif args.mode == 'folder':
        process_folder(args.input, args.output_suffix, args.output_folder)
    else:
        print('Must select "file" or "suffix" as mode')
        sys.exit()
