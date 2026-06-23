import argparse
import glob
import os
import pandas
import sys


def annotate_aetiology(dataframe: pandas.DataFrame, aetiologies: pandas.DataFrame):
    """
    Left-joins aetiology annotations onto a signature dataframe by signature ID.

    Args:
        dataframe (pandas.DataFrame): Signature data where the first column contains signature identifiers.
        aetiologies (pandas.DataFrame): Aetiology table with an 'id' column matching the signature identifiers.

    Returns:
        pandas.DataFrame: The input dataframe with aetiology columns appended.
    """
    signature_col = dataframe.columns[0]
    return dataframe.merge(
        aetiologies.rename(columns={'id': signature_col}),
        on=signature_col,
        how='left'
    )


def get_contribution_files(input_path: str):
    """
    Returns a list of SBS contribution file paths from a file or directory.

    Args:
        input_path (str): Path to a single SBS contributions file or a directory containing them.

    Returns:
        list[str]: Sorted list of matching file paths.

    Raises:
        ValueError: If input_path is neither an existing file nor an existing directory.
    """
    if os.path.isfile(input_path):
        return [input_path]
    if os.path.isdir(input_path):
        return sorted(glob.glob(os.path.join(input_path, "*.SBS_contributions.txt")))
    raise ValueError(f"Input path does not exist: {input_path}")


def read_dataframe(file: str):
    """
    Reads a tab-delimited file into a DataFrame.

    Args:
        file (str): Path to the tab-delimited text file.

    Returns:
        pandas.DataFrame: Contents of the file.
    """
    return pandas.read_csv(file, sep='\t')


def remove_trailing_forward_slash(folder: str):
    """
    Strips trailing forward slashes from a folder path.

    Args:
        folder (str): A directory path string.

    Returns:
        str: The path with any trailing '/' characters removed.
    """
    return folder.strip('/') if folder[-1] == '/' else folder


def resolve_output_path(input_file: str, input_path: str, output_path: str):
    """
    Determines the output file path for a given input file.

    When the input is a directory, places the output file in the output directory
    using the same filename. When the input is a single file, uses the output path
    directly as the destination file path.

    Args:
        input_file (str): Path to the specific input file being processed.
        input_path (str): The original --input argument (file or directory).
        output_path (str): The resolved --output argument (file or directory).

    Returns:
        str: Destination file path for the annotated output.
    """
    if os.path.isdir(input_path):
        return os.path.join(output_path, os.path.basename(input_file))
    return output_path


def write_dataframe(dataframe: pandas.DataFrame, output_name: str):
    """
    Writes a DataFrame to a tab-delimited file without the row index.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to write.
        output_name (str): Destination file path.
    """
    dataframe.to_csv(output_name, sep='\t', index=False)


def main(
        contribution_files: list[pandas.DataFrame],
        aetiologies: pandas.DataFrame,
        input_folder: str,
        output_folder: str 
    ):
    
    for contribution_file in contribution_files:
        dataframe = read_dataframe(
            file=contribution_file
        )
        annotated = annotate_aetiology(
            dataframe=dataframe, 
            aetiologies=aetiologies
        )
        destination = resolve_output_path(
            input_file=contribution_file,
            input_path=input_folder,
            output_path=output_folder
        )
        write_dataframe(
            dataframe=annotated, 
            output_name=destination
        )
        print(f"Annotated: {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='annotate_aetiology',
        description='Annotates SBS contribution files with mutational signature aetiologies.'
    )
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='path to a single SBS contributions file or a folder of SBS contributions files'
    )
    parser.add_argument(
        '--aetiologies',
        '-a',
        required=True,
        help='tab-delimited file with signature aetiologies (must have an "id" column)'
    )
    parser.add_argument(
        '--output',
        '-o',
        required=False,
        default=None,
        help='output file (when --input is a file) or output folder (when --input is a folder); '
             'defaults to overwriting the input file(s) in place'
    )
    args = parser.parse_args()

    contribution_files = get_contribution_files(args.input)
    if not contribution_files:
        sys.exit(f"No SBS contributions files found in: {args.input}")
    
    aetiologies = read_dataframe(args.aetiologies)

    output_path = args.output if args.output else args.input
    if os.path.isdir(args.input) and args.output:
        os.makedirs(args.output, exist_ok=True)

    main(
        contribution_files=contribution_files,
        aetiologies=aetiologies,
        input_folder=args.input,
        output_folder=args.output
    )
