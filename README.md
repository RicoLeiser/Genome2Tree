# Building-a-Phylogenetic-Tree-from-Whole-Genome-Comparisons

This tutorial explains how to construct a phylogenetic tree based on whole-genome comparisons of bacterial isolates. It bases on the following steps:
1. **Identification of orthologs** using [**Orthofinder**](https://github.com/davidemms/OrthoFinder)
2. **Alignment** using [**MAFFT**](https://github.com/GSLBiotech/mafft)
3. **Trimming** using [**ClipKIT**](https://github.com/JLSteenwyk/ClipKIT)
4. **Concatenation** using [**PhyKIT**](https://github.com/JLSteenwyk/PhyKIT)

The pipeline can process nucleotide and amino acid sequences, and bases on the identification of orthologous single-copy genes or gene products shared between submitted .fasta or .faa files. By this usually several hundred or thousand of different shared genes are identified in the submitted genomes. These build the fundation for a robust reconstruction of the phylogenetic relationships of the investigated genomes. While the princple and the underlying programms are well known, the construction of the phylogenetic trees usually requires labour intense reformatting of the outputs from these single programms. I constructed and easy-to-use pipeline which allows the use to construct a concated supermatrix from their input .fasta or .faa files, which can further used for constructed a phylogenetic tree using standard programms like IQ-Tree2

# System Requirements and Initial Setup

This tutorial was created on an **Ubuntu 22.04** machine, and the steps are tailored for use on an Ubuntu system. While it may also work on other platforms, some adaptations might be necessary.

## Storing Genomes of Interest

In the first step, genomes of interest should be stored in an accessible folder. For example, I uploaded the genomes of all known type strains from the bacterial genus *Paenarthrobacter*, along with an outgroup genome belonging to *Arthrobacter oryzae*. 

Using an outgroup genome, which can be placed in the same folder as the genomes of interest, is highly recommended as it allows for proper tree rooting.

The files found in the `prots` folder of this repository can be downloaded and stored in a directory like this:

```
/home/USERNAME/TutorialWholeGenomeComparison/prots
```

## Protein vs. Nucleotide Sequences

As you may have noticed, this tutorial uses **protein sequences**, as they generally provide a more robust estimation of phylogenetic relationships. However, if you are investigating closely related species, using nucleotide sequences is recommended. They can be organized in a similar folder structure as explained above. As mentioned before, the **workflow works for both protein and nucleic acid sequences**.

## Setting Up the Environment

After saving the genomes in a specific folder, you need to create an environment for the analysis. This requires an installation of [**Miniconda**](https://www.anaconda.com/docs/getting-started/miniconda/main) on your system. You may first follow the steps explained under this link to properly install Miniconda on your system. 

We will create a Miniconda environment in which all analyses will be performed to avoid conflicts with existing software. The environment needs to be activated before use. Below is the code to set up and activate the Miniconda environment:

```
conda create -n supermatrix_pipeline python=3.9
conda activate supermatrix_pipeline
conda install -c bioconda orthofinder mafft clipkit phykit
pip install biopython
```

