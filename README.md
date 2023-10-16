# SigProfilerAssignment wrapper
**Please [read their preprint](), review their [GitHub repository](https://github.com/AlexandrovLab/SigProfilerAssignment/tree/main), [official documentation](https://osf.io/mz79v/wiki/home/), and [COSMIC's mutational signatures page](https://cancer.sanger.ac.uk/signatures/) before using code in this repository**. 

This repository contains code that is a wrapper around [SigProfilerAssignment](https://github.com/AlexandrovLab/SigProfilerAssignment/tree/main), an algorithm that enabling the assignment of previously known mutational signatures to individual samples and individual somatic mutations, by the [Alexandrov Lab at UCSD](https://alexandrov.cloud.ucsd.edu/). As of this writing, SigProfilerAssignment has not yet been published in a peer review journal and the GitHub repository continues to be developed. So, while the [requirements](requirements.txt) file specifies a release, the code in this repository may eventually break as the authors make updates. 

SigProfilerAssignment does [not currently work in containers](https://github.com/AlexandrovLab/SigProfilerAssignment/issues/78) :(  

## Installation and set up
This repository uses **Python 3.11**. To use code in this repository, [download this software from GitHub](#download-this-software-from-github), [install Python dependencies](#install-python-dependencies) within a virtual environment, and [install a reference genome](#install-reference-genome). 

### Download this software from GitHub
This repository can be downloaded through GitHub on the website or by using terminal. To download on the website, navigate to the top of this page, click the green `Clone or download` button, and select `Download ZIP`. This will download this repository in a compressed format. To install using GitHub on terminal, type 

```bash
git clone https://github.com/vanallenlab/SigProfilerAssignment.git
cd SigProfilerAssignment
```

### Install Python dependencies
This repository uses Python 3.11. We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) and running Python with either [Anaconda](https://www.anaconda.com/download/) or  [Miniconda](https://conda.io/miniconda.html). 

To create a virtual environment and install dependencies with Anaconda or Miniconda, run the following from this repository's directory:
```bash
conda create -y -n SigProfilerAnalyzer python=3.11
conda activate SigProfilerAnalyzer
pip install -r requirements.txt
```

If you are using base Python, you can create a virtual environment and install dependencies by running:
```bash
virtualenv venv_SigProfilerAnalyzer
source activate venv_SigProfilerAnalyzer/bin/activate
pip install -r requirements.txt
```

### Install reference genome
SigProfilerAssignment uses [SigProfilerMatrixGenerator](https://github.com/AlexandrovLab/SigProfilerMatrixGenerator) for matrix generation, which requires a reference genome to be installed in the virtual environment. The script `install-reference-genome.py` will install a reference genome for use. 

This script uses SigProfilerMatrixGenerator and it will produce a warning that this step takes 40+ minutes, but it has never taken more than 5-10 minutes using either my home or Dana-Farber internet. 

Required arguments:
```
    --reference     <string>    reference genome to install; default=GRCh37; choices=GRCh38, GRCh37, mm9, mm10, rn6
```

Example:
```bash
python install-reference-genome.py --reference GRCh37
```

## Running SigProfilerAssignment
[SigProfiler tools](https://cancer.sanger.ac.uk/signatures/tools/) require passing a folder containing input files, rather than an individual file itself. Additionally, their [expected input for Mutation Annotation Format (MAF) files](https://osf.io/s93d5/wiki/3.%20Using%20the%20Tool%20-%20SBS%2C%20ID%2C%20DBS%20Input/) does not follow either [NCI](https://docs.gdc.cancer.gov/Data/File_Formats/MAF_Format/) or [TCGA](https://docs.gdc.cancer.gov/Encyclopedia/pages/Mutation_Annotation_Format_TCGAv2/) MAF specifications. Thus, to use this repository, we recommend,
1. Placing input files within an input directory
2. [Trim the MAF files](#trimming-maf-files) using `trim_maf.py`
3. [Run SigProfilerAssignment](#running-sigprofilerassignment) using `sig_profiler_assignment.py`

### Trimming MAF files
`trim_maf.py` will trim either a single MAF file or folder containing MAF files to the specification set by SigProfilerMatrixGenerator. 

Required arguments:
```
    --mode, -m      <string>    specify if input is a file or folder, choices: file, folder
    --input, -i     <string>    input file or folder
```

Optional arguments:
```
    --output-folder, -o     <string>    path to output folder, will be created if it does not exist
    --output-suffix, -s     <string>    string of new output suffix, if you want to strip file names
```

Example for file input:
```bash
python trim_maf.py \
  --mode file \
  --input example.oncotated.validated.annotated.final.maf \
  --output-folder trimmed-mafs \
  --output-suffix "maf"
```

### Running SigProfilerAssignment
The script `sig_profiler_assignment.py` is a wrapper around SigProfilerAssignment's `cosmic_fit` function. Additionally, the script will compute the contribution (or weight) per SBS signature per sample. Input MAFs should be [trimmed and formatted beforehand](#trimming-maf-files). 

This wrapper contains three required arguments and then largely mimics SigProfilerAssignment's [additional parameters](https://github.com/AlexandrovLab/SigProfilerAssignment#-main-parameters), with the exception of `--do-not-export-probabilities` and `--disable-plotting` as wrappers around `export_probabilities` and `make_plots`, respectively. The default values for both of these arguments are `True`, so the behavior for this wrapper is to disable them if you do not want the default functionality.

Required arguments:
```
    --input-folder, -i          <string>    folder containing input MAF files, after processing with `trim_maf.py`
    --output-folder, -f         <string>    folder to write outputs to
    --write-results-per-sample  <boolean>   if separate output files should be created for each sample
```

Optional arguments, see [their official documentation](https://osf.io/mz79v/wiki/3.Using%20the%20Tool%20-%20Input/):
```
    --input-type
    --context-type
    --version
    --exome
    --genome-build
    --signature-database
    --exclude-signature-subgroups
    --do-not-export-probabilities
    --export-probabilities-per-mutation
    --disable-plotting
    --sample-reconstruction-plots-format
    --verbose
```

Example:
```
python sig_profiler_assignment.py -i trimmed-mafs -o outputs --write-results-per-sample --verbose
```

The flow of this script is a bit odd, it performs the following sequence,
1. Copies input MAF files to the output directory and sets the output directory as the input directory
2. Runs SigProfilerAssignment
3. Remove copies of input files from output directory
4. Calculates contributions per sample for all samples and writes to `{output-folder}/SBS_contributions.txt`
5. Writes a table per sample to `{output-folder}/SBS_sample_contributions/`, if `--write-results-per-sample` is passed

The copying and removing of inputs from the output directory is because the current version of SigProfilerMatrixGenerator writes outputs to the input directory. Thus, this is performed to keep all outputs from SigProfilerAssignment in the outputs folder specified, leaving the inputs folder untouched. This definitely was not the case in prior versions of the tool, but I cannot find the changes in their release notes. Maybe I will open an Issue on their GitHub repository to try to find out if it was an intentional change or not.  

### Outputs
There are outputs generated from both SigProfilerMatrixGenerator and SigProfilerAssignment. Detailed descriptions of outputs can be found within the official documentation for [SigProfilerMatrixGenerator](https://osf.io/s93d5/wiki/home/) and [SigProfilerAssignment](https://osf.io/mz79v/wiki/4.%20Using%20the%20Tool%20-%20Output/). 

Outputs found in the `{output-folder}/` are as follows,
- `Assignment_Solution/`, outputs from SigProfilerAssignment
- `input/` a copy of the inputs used
- `Matrix_Generator_output/`, outputs from SigProfilerMatrixGenerator
- `SBS_sample_contributions/`, SBS contributions by sample, generated if `--write-results-per-sample` is passed
- `JOB_METADATA_SPA.TXT`, log file from SigProfilerAssignment
- `SBS_contributions.txt`, calculated contributions per sample for each SBS signature 
