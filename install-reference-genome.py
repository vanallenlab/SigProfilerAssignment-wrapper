import argparse
from SigProfilerMatrixGenerator import install as genInstall


def main(reference_genome):
    genInstall.install(reference_genome)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Install reference genome',
        description='Reference genome installation for SigProfilerAnalyzer'
    )
    parser.add_argument(
        '--reference',
        default='GRCh37',
        choices=['GRCh37', 'GRCh38', 'mm9', 'mm10', 'rn6']
    )
    args = parser.parse_args()
    main(args.reference)
