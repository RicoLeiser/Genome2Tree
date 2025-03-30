# Building-a-Phylogenetic-Tree-from-Whole-Genome-Comparisons

This tutorial explains how to construct a phylogenetic tree based on whole-genome comparisons of bacterial isolates. It bases on the following steps:
1. **Identification of orthologs** using [**Orthofinder**]((https://github.com/davidemms/OrthoFinder)
2. **Alignment** using [**MAFFT**](https://github.com/GSLBiotech/mafft)
3. **Trimming** using [**ClipKIT**](https://github.com/JLSteenwyk/ClipKIT)
4. **Concatenation** using [**PhyKIT**](https://github.com/JLSteenwyk/PhyKIT)

The pipeline can process nucleotide and amino acid sequences, and bases on the identification of orthologous single-copy genes or gene products shared between submitted .fasta or .faa files. By this usually several hundred or thousand of different shared genes are identified in the submitted genomes. These build the fundation for a robust reconstruction of the phylogenetic relationships of the investigated genomes. While the princple and the underlying programms are well known, the construction of the phylogenetic trees usually requires labour intense reformatting of the outputs from these single programms. I constructed and easy-to-use pipeline which allows the use to construct a concated supermatrix from their input .fasta or .faa files, which can further used for constructed a phylogenetic tree using standard programms like IQ-Tree2

The tutorial was constructed on a Ubuntu 22.04 machine, hence the steps are adapted to use at an Ubuntu system. While it might also work on other platforms, this will require adaptive steps.

In the first step genomes of interest should be stored in a accesible folder, as example I uploaded the genomes of all known type-strains from the bacterial Genus \textit{Paenarthrobacter} alongside with an outgroup genome belonging to the species Arthrobacter oryzae. Using an outgroup genomes which can be placed just in the same folder as the genomes of interest is highly recommended, as it allows the rooting of the tree afterwards.
