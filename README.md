# Building a phylogenetic tree from whole bacterial genomes with Genome2Tree

This tutorial shows an easiy way to reconstruct a phylogenetic tree from whole genome bacterial genomes. The workflow identifies orthologous single-copy genes shared between several bacteria genomes and constructs an aligned and concated supermatrix from the sequences which is ready to use for phylogenetic reconstruction. All of these steps are merged into one phyton based pipeline which can easily be used to calculate a concated gene supermatrix, which requires only **.fasta or .faa genome sequences** from the user in order to compute. 

The pipeline bases on the following steps/programs:
1. **Identification of orthologs** using [**Orthofinder**](https://github.com/davidemms/OrthoFinder)
2. **Alignment** using [**MAFFT**](https://github.com/GSLBiotech/mafft)
3. **Trimming** using [**ClipKIT**](https://github.com/JLSteenwyk/ClipKIT)
4. **Concatenation** using [**PhyKIT**](https://github.com/JLSteenwyk/PhyKIT)

The pipeline can process nucleotide and amino acid sequences, and bases on the identification of orthologous single-copy genes or gene products shared between submitted .fasta or .faa files. By this usually several hundred or thousand of different shared genes are identified in the submitted genomes. These build the fundation for a robust reconstruction of the phylogenetic relationships of the investigated genomes. While the princple and the underlying programms are well known, the construction of the phylogenetic trees usually requires labour intense reformatting of the outputs from these single programms. I constructed and easy-to-use pipeline which allows the use to construct a concated supermatrix from their input .fasta or .faa files, which can further used for constructed a phylogenetic tree using standard programms like IQ-Tree2

# System Requirements and Initial Setup

This tutorial was created on an **Ubuntu 22.04** machine, and the steps are tailored for use on an Ubuntu system. While it may also work on other platforms, some adaptations might be necessary. **All commands should be typed directly in your terminal and executed there**. 


## Protein vs. Nucleotide Sequences

This tutorial concentrates on **protein sequences**, as they generally provide a more robust estimation of phylogenetic relationships. However, if you are investigating closely related species, using nucleotide sequences is recommended. As mentioned before, the **workflow works for both protein and nucleic acid sequences**.

## Setting Up the Environment

After saving the genomes in a specific folder, you need to create an environment for the analysis. This requires an installation of [**Miniconda**](https://www.anaconda.com/docs/getting-started/miniconda/main) on your system. You may first follow the steps explained under this link to properly install Miniconda on your system. 

We will create a Miniconda environment in which all analyses will be performed to avoid conflicts with existing software. The environment needs to be activated before use. Below is the code to set up and activate the Miniconda environment:

```
conda create -n Genome2Tree python=3.9
conda activate Genome2Tree
conda install -c bioconda orthofinder mafft clipkit phykit
pip install biopython
```
## Running the pipeline
After setting up and activating your miniconda environment you need to **download the python script** (**!!Important!!** ) found in this repository called **Genome2Tree.py**. This script should be saved in a apropriate folder or can also be used directly from its location in your Downloads folder. The script allows the user to specify the **input folder**, where all of the input genomes are stored, and the **output folder** where all results should be saved into. Furthermore the user can specify how many CPU cores are used, which will have influence on the analysis time. With 8 cores expect for ~10 genomes around 10-20 min to complete, while 100 genomes will take several hours. 
```
python /path/to/pythonfile/Genome2Tree.py -i /path/to/input_fastas -o /path/to/output -t 8
```
After the analysis ended you can deactivate your conda environment using 
**conda deactivate**

## Creating the phylogenetic tree
After the analysis completed successfully you will find a file called **supermatrix.fa** which is the overall output from the pipeline. This is a large concated matrix containing all the aligned sequences of all found orthologous genes/proteins of your genomes. This matrix can be used to construct a phylogenetic tree. In the subsequent steps the mode of action to create a phylogenetic tree from this supermatrix is briefly explained. First you need to install an appropriate software to calculate the tree for you, I use [**iqtree2**](https://github.com/iqtree/iqtree2) which can be installed in a separate miniconda environment. 
This can be called in the following way
```
conda activate iqtree_env #(or any other name you gave to your environment)
iqtree2 -s /path/to/your/supermatrixFile/supermatrix.fa -m MFP+MERGE+R --prefix model_test
```
This will run IQ-Tree in modelfinder mode, which will automatically identifiy the optimal substitution model for your supermatrix. After this is complete an output will appear in your terminal window indicating which model was found to be most suitable for your input sequences, alongside with already usuable tree files in various formats. If you want bootstrap support for your phylogenetic tree, the model should be re-run using the following code. Be aware that IQ-Tree in modelfinder mode might take a long time to finish, calculation times can be several days for ~100 genomes on common "standard" laptops. Hence, other programms might also be used to construct a tree from the supermatrix file. 
```
iqtree2 -s  /path/to/your/supermatrixFile/supermatrix.fa -m BEST_MODEL -B 1000 --prefix final_tree
```
With best model being any model, suggested by the modelfinder of IQ-Tree, these models usually look something like this "WAG+F+R7"

## Processing the phylogenetic tree
Once the phylogenetic tree is constructed you might wanna view, adapt and export the tree in a image format. This can easily be done by several software tools, of which I found [**TreeViewer**](https://treeviewer.org/) quite useful. This software can be downloaded under the link and is able to display the different output formats produced by IQ-Tree and export your phylogenetic tree as images as a final output of your analysis. 
