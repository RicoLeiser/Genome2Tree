#!/usr/bin/env python3
import os
import subprocess
import argparse
import logging
from pathlib import Path
import glob

def setup_logging(output_dir):
    """Set up logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(output_dir, 'supermatrix_pipeline.log')),
            logging.StreamHandler()
        ]
    )

def find_orthofinder_results(ortho_dir):
    """Find the latest OrthoFinder results directory with date suffix."""
    results_dirs = glob.glob(os.path.join(ortho_dir, "Results_*"))
    if not results_dirs:
        return None
    # Get the most recent directory (sorted by modification time)
    latest_dir = max(results_dirs, key=os.path.getmtime)
    return latest_dir

def run_orthofinder(input_dir, output_dir, threads=12, is_dna=False, force=False):
    """Run OrthoFinder to identify single-copy orthologs if needed."""
    ortho_dir = os.path.join(output_dir, "orthofinder_results")
    
    # Check if we should skip OrthoFinder
    if not force:
        existing_results = find_orthofinder_results(ortho_dir)
        if existing_results:
            logging.info(f"Found existing OrthoFinder results at {existing_results}, skipping...")
            return ortho_dir
    
    logging.info("Running OrthoFinder...")
    
    cmd = [
        "orthofinder",
        "-f", input_dir,
        "-o", ortho_dir,
        "-t", str(threads),
        "-a", str(threads)
    ]
    
    if is_dna:
        cmd.append("-d")
    
    try:
        subprocess.run(cmd, check=True)
        logging.info("OrthoFinder completed successfully.")
        return ortho_dir
    except subprocess.CalledProcessError as e:
        logging.error(f"OrthoFinder failed: {e}")
        raise

def get_single_copy_orthologs(ortho_dir):
    """Get path to single copy ortholog sequences with dynamic results directory."""
    results_dir = find_orthofinder_results(ortho_dir)
    if not results_dir:
        raise FileNotFoundError(f"No OrthoFinder results found in {ortho_dir}")
    
    single_copy_dir = os.path.join(
        results_dir,
        "Single_Copy_Orthologue_Sequences"
    )
    
    if not os.path.exists(single_copy_dir):
        raise FileNotFoundError(f"Single copy orthologs directory not found at {single_copy_dir}")
    
    return single_copy_dir

def align_sequences(input_dir, output_dir, threads=1):
    """Align sequences using MAFFT."""
    logging.info(f"Aligning sequences in {input_dir}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for fasta_file in glob.glob(os.path.join(input_dir, "*.fa")):
        output_file = os.path.join(
            output_dir,
            os.path.basename(fasta_file).replace(".fa", "_aligned.fa")
        )
        
        cmd = [
            "mafft",
            "--auto",
            "--thread", str(threads),
            "--inputorder",
            fasta_file
        ]
        
        try:
            with open(output_file, 'w') as outfile:
                subprocess.run(cmd, stdout=outfile, check=True)
            logging.info(f"Aligned {os.path.basename(fasta_file)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"MAFFT failed on {fasta_file}: {e}")
            raise

def trim_alignments(input_dir, output_dir):
    """Trim alignments using ClipKIT."""
    logging.info(f"Trimming alignments in {input_dir}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for aligned_file in glob.glob(os.path.join(input_dir, "*.fa")):
        output_file = os.path.join(output_dir, os.path.basename(aligned_file))
        
        cmd = [
            "clipkit",
            aligned_file,
            "-o", output_file
        ]
        
        try:
            subprocess.run(cmd, check=True)
            logging.info(f"Trimmed {os.path.basename(aligned_file)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"ClipKIT failed on {aligned_file}: {e}")
            raise

def create_name_list(input_dir, output_file):
    """Create a text file with original FASTA filenames."""
    logging.info(f"Creating name list from {input_dir}...")
    
    fasta_files = sorted(glob.glob(os.path.join(input_dir, "*.faa")) + 
                        glob.glob(os.path.join(input_dir, "*.fna")))
    
    if not fasta_files:
        raise FileNotFoundError(f"No FASTA files found in {input_dir}")
    
    with open(output_file, 'w') as f:
        for fasta in fasta_files:
            # Get filename without extension
            name = os.path.splitext(os.path.basename(fasta))[0]
            f.write(name + "\n")
    
    logging.info(f"Saved name list to {output_file}")

def rename_sequences(input_dir, output_dir, name_file):
    """Rename sequences in alignment files."""
    logging.info(f"Renaming sequences in {input_dir} using {name_file}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read replacement names
    with open(name_file, 'r') as f:
        replacement_names = [line.strip() for line in f]
    
    for trimmed_file in glob.glob(os.path.join(input_dir, "*.fa")):
        output_file = os.path.join(output_dir, os.path.basename(trimmed_file))
        
        with open(trimmed_file, 'r') as infile, open(output_file, 'w') as outfile:
            name_index = 0
            for line in infile:
                if line.startswith('>'):
                    if name_index >= len(replacement_names):
                        raise ValueError("More sequence headers than replacement names")
                    outfile.write(f">{replacement_names[name_index]}\n")
                    name_index += 1
                else:
                    outfile.write(line)
        
        logging.info(f"Renamed sequences in {os.path.basename(trimmed_file)}")

def verify_complete_sequences(input_dir, output_dir, name_file):
    """Verify all sequences are complete."""
    logging.info(f"Verifying complete sequences in {input_dir}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read required names
    with open(name_file, 'r') as f:
        required_names = set(line.strip() for line in f)
    
    for renamed_file in glob.glob(os.path.join(input_dir, "*.fa")):
        with open(renamed_file, 'r') as f:
            present_names = set()
            for line in f:
                if line.startswith('>'):
                    present_names.add(line[1:].strip())
        
        if present_names == required_names:
            output_file = os.path.join(output_dir, os.path.basename(renamed_file))
            with open(renamed_file, 'r') as infile, open(output_file, 'w') as outfile:
                outfile.write(infile.read())
            logging.info(f"{os.path.basename(renamed_file)} has all required sequences")
        else:
            logging.warning(f"{os.path.basename(renamed_file)} is missing some sequences")

def create_supermatrix(input_dir, output_dir, prefix):
    """Create supermatrix using PhyKIT."""
    logging.info("Creating supermatrix...")
    
    # First create file with paths to all alignments
    file_list = os.path.join(output_dir, "alignment_paths.txt")
    with open(file_list, 'w') as f:
        for alignment in glob.glob(os.path.join(input_dir, "*.fa")):
            f.write(alignment + "\n")
    
    # Run PhyKIT
    output_prefix = os.path.join(output_dir, prefix)
    cmd = [
        "phykit",
        "create_concat",
        "-a", file_list,
        "-p", output_prefix
    ]
    
    try:
        subprocess.run(cmd, check=True)
        logging.info(f"Supermatrix created at {output_prefix}.phylip and {output_prefix}.partitions")
    except subprocess.CalledProcessError as e:
        logging.error(f"PhyKIT failed: {e}")
        raise
    except FileNotFoundError:
        logging.error("PhyKIT not found. Is it installed and in your PATH?")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline to create a supermatrix from FASTA files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", required=True,
                        help="Directory containing input FASTA files (.faa or .fna)")
    parser.add_argument("-o", "--output", required=True,
                        help="Output directory for all results")
    parser.add_argument("-p", "--prefix", default="supermatrix",
                        help="Prefix for output supermatrix files")
    parser.add_argument("-t", "--threads", type=int, default=4,
                        help="Number of threads to use")
    parser.add_argument("--dna", action="store_true",
                        help="Input files are DNA (.fna) instead of protein (.faa)")
    parser.add_argument("--force", action="store_true",
                        help="Force rerun of OrthoFinder even if results exist")
    
    args = parser.parse_args()
    
    # Create output directory structure
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    setup_logging(output_dir)
    
    try:
        # Step 1: Run OrthoFinder (or use existing results)
        ortho_dir = run_orthofinder(
            args.input,
            output_dir,
            threads=args.threads,
            is_dna=args.dna,
            force=args.force
        )
        
        # Step 2: Get single copy orthologs (with dynamic path handling)
        single_copy_dir = get_single_copy_orthologs(ortho_dir)
        
        # Step 3: Align sequences
        aligned_dir = output_dir / "aligned"
        align_sequences(single_copy_dir, aligned_dir, threads=args.threads)
        
        # Step 4: Trim alignments
        trimmed_dir = output_dir / "trimmed"
        trim_alignments(aligned_dir, trimmed_dir)
        
        # Step 5: Create name list from original FASTA files
        name_file = output_dir / "original_names.txt"
        create_name_list(args.input, name_file)
        
        # Step 6: Rename sequences
        renamed_dir = output_dir / "renamed"
        rename_sequences(trimmed_dir, renamed_dir, name_file)
        
        # Step 7: Verify complete sequences
        complete_dir = output_dir / "complete"
        verify_complete_sequences(renamed_dir, complete_dir, name_file)
        
        # Step 8: Create supermatrix
        create_supermatrix(complete_dir, output_dir, args.prefix)
        
        logging.info("Pipeline completed successfully!")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
