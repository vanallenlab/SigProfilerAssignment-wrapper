import argparse
import glob
import os
import pandas
import shutil
from typing import Optional

from SigProfilerAssignment import Analyzer as Analyze


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
    merged = dataframe.merge(
        aetiologies.rename(columns={'id': signature_col}),
        on=signature_col,
        how='left'
    )
    return merged


def calculate_contributions(samples_stats: pandas.DataFrame, activities: pandas.DataFrame):
    """
    Divides each sample's signature activities by its total mutation count to produce fractional contributions.

    Args:
        samples_stats (pandas.DataFrame): Sample-level stats with 'Sample Names' and 'Total Mutations' columns.
        activities (pandas.DataFrame): Signature activity counts with a 'Samples' column and one column per signature.

    Returns:
        pandas.DataFrame: Fractional signature contributions indexed by sample name.
    """
    return (
        activities
        .set_index('Samples')
        .divide(
            samples_stats
            .set_index('Sample Names')
            .loc[:, 'Total Mutations'],
            axis=0
        )
    )


def copy_inputs(input_folder: str, output_folder: str):
    """
    Copies all MAF files from the input folder into the output folder.

    Args:
        input_folder (str): Path to the directory containing source MAF files.
        output_folder (str): Path to the destination directory.
    """
    for file in glob.glob(os.path.join(input_folder, "*.maf")):
        shutil.copy2(file, output_folder)


def read_dataframe(file: str):
    """
    Reads a tab-delimited file into a DataFrame.

    Args:
        file (str): Path to the tab-delimited text file.

    Returns:
        pandas.DataFrame: Contents of the file.
    """
    return pandas.read_csv(file, sep='\t')


def remove_inputs(folder: str):
    """
    Deletes all MAF files in the given folder.

    Args:
        folder (str): Path to the directory from which MAF files will be removed.
    """
    for file in glob.glob(os.path.join(folder, "*.maf")):
        os.remove(file)


def remove_trailing_forward_slash(folder: str):
    """
    Strips trailing forward slashes from a folder path.

    Args:
        folder (str): A directory path string.

    Returns:
        str: The path with any trailing '/' characters removed.
    """
    return folder.strip('/') if folder[-1] == '/' else folder


def rename_matrix_generator_output_folder(folder: str):
    """
    Reorganizes SigProfilerMatrixGenerator output directories under a single named subdirectory.
    Moves 'output/' to 'Matrix_Generator_output/' and relocates 'logs/' inside it.

    Args:
        folder (str): Path to the root output directory containing the 'output' and 'logs' subdirectories.
    """
    os.rename(
        os.path.join(folder, "output"), 
        os.path.join(folder, "Matrix_Generator_output")
    )
    os.rename(
        os.path.join(folder, "logs"), 
        os.path.join(folder, "Matrix_Generator_output", "logs")
    )


def run_assignment(
    input_folder: str,
    output_folder: str,
    input_type: str = "vcf",
    context_type: str = "96",
    version: float = 3.3,
    exome: bool = False,
    genome_build: str = 'GRCh37',
    signature_database: Optional[str] = None,
    exclude_signature_subgroups: Optional[str] = None,
    export_probabilities: bool = True,
    export_probabilities_per_mutation: bool = False,
    make_plots: bool = True,
    sample_reconstruction_plots: Optional[str] = None,
    verbose: bool = False
):
    """
    Runs SigProfilerAssignment's cosmic_fit to assign COSMIC mutational signatures to samples.

    Args:
        input_folder (str): Path to the directory containing input sample files.
        output_folder (str): Path to the directory where results will be written.
        input_type (str): Format of input files — 'vcf', 'seg:TYPE', or 'matrix' (default: 'vcf').
        context_type (str): Mutational context to analyze — '96', '288', '1536', 'DINUC', or 'ID' (default: '96').
        version (float): COSMIC signature version to use (default: 3.3).
        exome (bool): If True, restrict analysis to exonic regions (default: False).
        genome_build (str): Reference genome build — 'GRCh37', 'GRCh38', 'mm9', 'mm10', or 'rn6' (default: 'GRCh37').
        signature_database (str or None): Path to a custom signature database file (default: None).
        exclude_signature_subgroups (str or None): Comma-separated signature subgroups to exclude (default: None).
        export_probabilities (bool): If True, export per-sample signature probabilities (default: True).
        export_probabilities_per_mutation (bool): If True, export per-mutation probabilities; only applies to 'vcf' input (default: False).
        make_plots (bool): If True, generate output plots (default: True).
        sample_reconstruction_plots (str or None): Format for reconstruction plots — 'pdf', 'png', 'both', or None (default: None).
        verbose (bool): If True, print verbose output (default: False).
    """
    Analyze.cosmic_fit(
        samples=input_folder,
        output=output_folder,
        input_type=input_type,
        context_type=context_type,
        cosmic_version=version,
        exome=exome,
        genome_build=genome_build,
        signature_database=signature_database,
        exclude_signature_subgroups=exclude_signature_subgroups,
        export_probabilities=export_probabilities,
        export_probabilities_per_mutation=export_probabilities_per_mutation,
        make_plots=make_plots,
        sample_reconstruction_plots=sample_reconstruction_plots,
        verbose=verbose
    )


def write_dataframe(file: pandas.DataFrame, output_name: str):
    """
    Writes a DataFrame to a tab-delimited file without the row index.

    Args:
        file (pandas.DataFrame): The DataFrame to write.
        output_name (str): Destination file path.
    """
    file.to_csv(output_name, sep='\t', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='SigProfilerAssignment',
        description='Runs SigProfilerAssignment, see their official documentation for more argument details.'
    )
    parser.add_argument(
        '--write-results-per-sample',
        action='store_true',
        help='Produce additional output of signature contributions for each sample'
    )
    parser.add_argument(
        '--input-folder',
        '-i',
        required=True,
        help='equivalent to `samples` parameter'
    )
    parser.add_argument(
        '--output-folder',
        '-o',
        required=True,
        help='equivalent to `output` parameter'
    )
    parser.add_argument(
        '--input-type',
        default='vcf',
        choices=['vcf', "seg:TYPE", "matrix"],
        help='equivalent to `input_type` parameter'
    )
    parser.add_argument(
        '--context-type',
        default='96',
        choices=['96', '288', '1536', 'DINUC', 'ID'],
        help='equivalent to `context_type` parameter'
    ) 
    parser.add_argument(
        '--version',
        default=3.3,
        choices=[1, 2, 3, 3.1, 3.2, 3.3],
        help='equivalent to `cosmic_version` parameter'
    )
    parser.add_argument(
        '--exome',
        action='store_true',
        help='equivalent to `exome` parameter'
    )
    parser.add_argument(
        '--genome-build',
        default='GRCh37',
        choices=['GRCh37', 'GRCh38', 'mm9', 'mm10', 'rn6'],
        help='equivalent to `genome_build` parameter'
    )
    parser.add_argument(
        '--signature-database',
        help='equivalent to `signature_database` parameter'
    )
    parser.add_argument(
        '--exclude-signature-subgroups',
        default=None,
        help='equivalent to `exclude_signature_subgroups` parameter'
    )
    parser.add_argument(
        '--do-not-export-probabilities',
        action='store_true',
        help='equivalent to `export_probabilities` parameter, probabilities are exported by default'
    )
    parser.add_argument(
        '--export-probabilities-per-mutation',
        action='store_true',
        help='equivalent to `export_probabilities_per_mutation` parameter, applicable to `vcf` `input_type`'
    )
    parser.add_argument(
        '--disable-plotting',
        action='store_true',
        help='used for `make_plots` parameter, plots are generated by default'
    )
    parser.add_argument(
        '--sample-reconstruction-plots-format',
        default=None,
        choices=['pdf', 'png', 'both', None],
        help='specify format for `sample_reconstruction_plots` parameter'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='equivalent to `verbose` parameter'
    )
    parser.add_argument(
        '--aetiology',
        '-a',
        required=False,
        help='tab delimited text file of mutational signatures and their aetiology'
    )

    # add argument to split up outputs by sample
    args = parser.parse_args()

    args.input_folder = remove_trailing_forward_slash(args.input_folder)
    args.output_folder = remove_trailing_forward_slash(args.output_folder)
    print(args.input_folder, args.output_folder)

    os.makedirs(args.output_folder, exist_ok=True)
    # There is a bug(?) with SigProfilerAnalyzer 0.0.32 and/or SigProfilerMatrixGenerator v.1.2.18
    # where some outputs are placed in the input folder. This was not the case previously
    # but I cannot find documentation in their release notes. Maybe I was doing something wrong! So, hence this dance
    # of copy inputs to output folder > run with both input_folder and output_folder arguments pointing to the output
    # folder, and then remove the copied set of input files.
    copy_inputs(args.input_folder, args.output_folder)
    run_assignment(
        input_folder=args.output_folder,
        output_folder=args.output_folder,
        input_type=args.input_type,
        context_type=args.context_type,
        version=args.version,
        exome=args.exome,
        genome_build=args.genome_build,
        signature_database=args.signature_database,
        exclude_signature_subgroups=args.exclude_signature_subgroups,
        export_probabilities=False if args.do_not_export_probabilities else True,
        export_probabilities_per_mutation=args.export_probabilities_per_mutation,
        make_plots=False if args.disable_plotting else True,
        sample_reconstruction_plots=args.sample_reconstruction_plots_format,
        verbose=args.verbose
    )
    remove_inputs(args.output_folder)

    solution_samples_stats_file = "Assignment_Solution/Solution_Stats/Assignment_Solution_Samples_Stats.txt"
    solution_samples_stats = read_dataframe(f"{args.output_folder}/{solution_samples_stats_file}")

    solution_activities_file = "Assignment_Solution/Activities/Assignment_Solution_Activities.txt"
    solution_activities = read_dataframe(f"{args.output_folder}/{solution_activities_file}")

    signature_contributions = calculate_contributions(solution_samples_stats, solution_activities)
    write_dataframe(signature_contributions, f'{args.output_folder}/SBS_contributions.txt')
    
    if args.aetiology:
        aetiologies = read_dataframe(file=args.aetiology)
    else:
        aetiologies = pandas.DataFrame(columns=['id', 'aetiology'])

    if args.write_results_per_sample:
        os.makedirs(os.path.join(args.output_folder, "SBS_sample_contributions"), exist_ok=True)
        for sample in signature_contributions.index:
            sample_output = signature_contributions.loc[sample, :].to_frame().reset_index()
            sample_output = annotate_aetiology(dataframe=sample_output, aetiologies=aetiologies)
            sample_output.columns = ['signature', 'contribution', 'aetiology']
            sample_output_name = f"{args.output_folder}/SBS_sample_contributions/{sample}.SBS_contributions.txt"
            write_dataframe(sample_output, output_name=sample_output_name)

    rename_matrix_generator_output_folder(args.output_folder)
