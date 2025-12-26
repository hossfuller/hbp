#!/usr/bin/env python3
"""
plothbp.py - A script to visualize HBP (Hit By Pitch) data from the database.

This script reads data from 'database/hbpdata.db' and creates:
1. A scatter plot of x_pos vs z_pos (y_pos) with color coding by end_speed
2. A contour plot of the ratio of end_speed to x_pos
3. A contour plot of the ratio of end_speed to z_pos (y_pos)

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

def create_contour_plots(x_pos, z_pos, end_speed, output_dir='plots/'):
    """
    Create contour plots for end_speed ratios.
    
    Args:
        x_pos (array): x position data
        z_pos (array): z position data (y-axis equivalent)
        end_speed (array): end speed data
        output_dir (str): Directory to save the plots
    """
    # Create grid for contour plots
    x_min, x_max = min(x_pos), max(x_pos)
    z_min, z_max = min(z_pos), max(z_pos)
    
    # Create grid points
    x_grid = np.linspace(x_min, x_max, 100)
    z_grid = np.linspace(z_min, z_max, 100)
    X, Z = np.meshgrid(x_grid, z_grid)
    
    # Calculate ratios for each point
    # Ratio: end_speed / position
    # We'll use interpolation to create smooth contours
    
    # Create figure for both contour plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: end_speed / x_pos ratio
    # Create a grid of ratios by interpolating the data
    from scipy.interpolate import griddata
    
    # Calculate actual ratios from the data
    x_ratio = end_speed / x_pos
    z_ratio = end_speed / z_pos
    
    # Interpolate for smooth contours
    x_ratio_grid = griddata((x_pos, z_pos), x_ratio, (X, Z), method='cubic', fill_value=0)
    z_ratio_grid = griddata((x_pos, z_pos), z_ratio, (X, Z), method='cubic', fill_value=0)
    
    # Plot end_speed / x_pos contour
    contour1 = ax1.contourf(X, Z, x_ratio_grid, levels=20, cmap='viridis')
    fig.colorbar(contour1, ax=ax1, label='End Speed / X Position Ratio')
    ax1.set_xlabel('X Position (feet)')
    ax1.set_ylabel('Z Position (feet)')
    ax1.set_title('Contour: End Speed / X Position Ratio')
    
    # Plot end_speed / z_pos contour
    contour2 = ax2.contourf(X, Z, z_ratio_grid, levels=20, cmap='plasma')
    fig.colorbar(contour2, ax=ax2, label='End Speed / Z Position Ratio')
    ax2.set_xlabel('X Position (feet)')
    ax2.set_ylabel('Z Position (feet)')
    ax2.set_title('Contour: End Speed / Z Position Ratio')
    
    # Save plots
    os.makedirs(output_dir, exist_ok=True)
    
    # Save individual plots
    output_path1 = os.path.join(output_dir, 'hbp_contour_x_ratio.png')
    output_path2 = os.path.join(output_dir, 'hbp_contour_z_ratio.png')
    
    # Save the combined figure
    combined_path = os.path.join(output_dir, 'hbp_contour_plots_combined.png')
    fig.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined contour plots saved to: {combined_path}")
    
    # Save individual plots
    fig, ax = plt.subplots(figsize=(10, 8))
    contour1 = ax.contourf(X, Z, x_ratio_grid, levels=20, cmap='viridis')
    fig.colorbar(contour1, ax=ax, label='End Speed / X Position Ratio')
    ax.set_xlabel('X Position (feet)')
    ax.set_ylabel('Z Position (feet)')
    ax.set_title('Contour: End Speed / X Position Ratio')
    fig.savefig(output_path1, dpi=300, bbox_inches='tight')
    print(f"X ratio contour plot saved to: {output_path1}")
    plt.close()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    contour2 = ax.contourf(X, Z, z_ratio_grid, levels=20, cmap='plasma')
    fig.colorbar(contour2, ax=ax, label='End Speed / Z Position Ratio')
    ax.set_xlabel('X Position (feet)')
    ax.set_ylabel('Z Position (feet)')
    ax.set_title('Contour: End Speed / Z Position Ratio')
    fig.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"Z ratio contour plot saved to: {output_path2}")
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
    
    # Create contour plots
    print("\nCreating contour plots...")
    try:
        create_contour_plots(x_pos, z_pos, end_speed)
    except ImportError:
        print("scipy not available. Skipping contour plots.")
    except Exception as e:
        print(f"Error creating contour plots: {e}")
    
    print("\nAll plots created successfully!")

if __name__ == '__main__':
    main()