#!/usr/bin/env python3
"""
plothbp_simple.py - A simplified script to visualize HBP data without scipy dependency.

This script reads data from 'database/hbpdata.db' and creates:
1. A scatter plot of x_pos vs z_pos (y_pos) with color coding by end_speed
2. A hexbin plot showing density of end_speed / x_pos ratios
3. A hexbin plot showing density of end_speed / z_pos ratios

All plots are saved in the 'plots/' directory.
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import os

def read_hbp_data(db_path='database/hbpdata.db'):
    """
    Read HBP data from the SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        tuple: (x_pos, z_pos, end_speed) arrays
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read all data from the hbpdata table
    cursor.execute('SELECT x_pos, z_pos, end_speed FROM hbpdata WHERE x_pos IS NOT NULL AND z_pos IS NOT NULL AND end_speed IS NOT NULL')
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No valid data found in the database.")
        return None, None, None
    
    # Extract columns
    x_pos = np.array([row[0] for row in data])
    z_pos = np.array([row[1] for row in data])
    end_speed = np.array([row[2] for row in data])
    
    return x_pos, z_pos, end_speed

def create_scatter_plot(x_pos, z_pos, end_speed, output_dir='plots/'):
    """
    Create a scatter plot of x_pos vs z_pos with color coding by end_speed.
    
    Args:
        x_pos (array): x position data
        z_pos (array): z position data (y-axis equivalent)
        end_speed (array): end speed data for color coding
        output_dir (str): Directory to save the plot
    """
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create scatter plot with color gradient from blue (low speed) to red (high speed)
    scatter = plt.scatter(x_pos, z_pos, c=end_speed, cmap='coolwarm', 
                         alpha=0.7, edgecolors='w', linewidths=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('End Speed (mph)', rotation=270, labelpad=15)
    
    # Add labels and title
    plt.xlabel('X Position (feet)', fontsize=12)
    plt.ylabel('Z Position (feet)', fontsize=12)
    plt.title('HBP Scatter Plot: X Position vs Z Position by End Speed', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save plot
    output_path = os.path.join(output_dir, 'hbp_scatter_plot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Scatter plot saved to: {output_path}")
    
    plt.close()

def create_ratio_plots(x_pos, z_pos, end_speed, output_dir='plots/'):
    """
    Create hexbin plots for end_speed ratios using matplotlib's hexbin functionality.
    
    Args:
        x_pos (array): x position data
        z_pos (array): z position data (y-axis equivalent)
        end_speed (array): end speed data
        output_dir (str): Directory to save the plots
    """
    # Calculate ratios
    x_ratio = end_speed / x_pos
    z_ratio = end_speed / z_pos
    
    # Create figure for both plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: end_speed / x_pos ratio using hexbin
    hex1 = ax1.hexbin(x_pos, z_pos, C=x_ratio, gridsize=30, cmap='viridis', 
                      bins='log', mincnt=1)
    fig.colorbar(hex1, ax=ax1, label='End Speed / X Position Ratio')
    ax1.set_xlabel('X Position (feet)')
    ax1.set_ylabel('Z Position (feet)')
    ax1.set_title('Hexbin: End Speed / X Position Ratio')
    
    # Plot 2: end_speed / z_pos ratio using hexbin
    hex2 = ax2.hexbin(x_pos, z_pos, C=z_ratio, gridsize=30, cmap='plasma', 
                      bins='log', mincnt=1)
    fig.colorbar(hex2, ax=ax2, label='End Speed / Z Position Ratio')
    ax2.set_xlabel('X Position (feet)')
    ax2.set_ylabel('Z Position (feet)')
    ax2.set_title('Hexbin: End Speed / Z Position Ratio')
    
    # Save plots
    os.makedirs(output_dir, exist_ok=True)
    
    # Save combined plot
    combined_path = os.path.join(output_dir, 'hbp_ratio_plots_combined.png')
    fig.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined ratio plots saved to: {combined_path}")
    
    # Save individual plots
    fig, ax = plt.subplots(figsize=(10, 8))
    hex1 = ax.hexbin(x_pos, z_pos, C=x_ratio, gridsize=30, cmap='viridis', 
                    bins='log', mincnt=1)
    fig.colorbar(hex1, ax=ax, label='End Speed / X Position Ratio')
    ax.set_xlabel('X Position (feet)')
    ax.set_ylabel('Z Position (feet)')
    ax.set_title('Hexbin: End Speed / X Position Ratio')
    
    output_path1 = os.path.join(output_dir, 'hbp_hexbin_x_ratio.png')
    fig.savefig(output_path1, dpi=300, bbox_inches='tight')
    print(f"X ratio hexbin plot saved to: {output_path1}")
    plt.close()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    hex2 = ax.hexbin(x_pos, z_pos, C=z_ratio, gridsize=30, cmap='plasma', 
                    bins='log', mincnt=1)
    fig.colorbar(hex2, ax=ax, label='End Speed / Z Position Ratio')
    ax.set_xlabel('X Position (feet)')
    ax.set_ylabel('Z Position (feet)')
    ax.set_title('Hexbin: End Speed / Z Position Ratio')
    
    output_path2 = os.path.join(output_dir, 'hbp_hexbin_z_ratio.png')
    fig.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"Z ratio hexbin plot saved to: {output_path2}")
    plt.close()

def main():
    """
    Main function to execute the plotting pipeline.
    """
    print("Starting HBP data visualization...")
    
    # Read data from database
    print("Reading data from database...")
    x_pos, z_pos, end_speed = read_hbp_data()
    
    if x_pos is None:
        print("No valid data found. Exiting.")
        return
    
    print(f"Found {len(x_pos)} data points")
    print(f"X position range: {min(x_pos):.2f} to {max(x_pos):.2f}")
    print(f"Z position range: {min(z_pos):.2f} to {max(z_pos):.2f}")
    print(f"End speed range: {min(end_speed):.2f} to {max(end_speed):.2f}")
    
    # Create scatter plot
    print("\nCreating scatter plot...")
    create_scatter_plot(x_pos, z_pos, end_speed)
    
    # Create ratio plots using hexbin
    print("\nCreating ratio plots...")
    create_ratio_plots(x_pos, z_pos, end_speed)
    
    print("\nAll plots created successfully!")

if __name__ == '__main__':
    main()