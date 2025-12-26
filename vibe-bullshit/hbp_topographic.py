#!/usr/bin/env python3
"""
hbp_topographic.py - A script to generate topographic plots from HBP data.

This script creates two topographic plots:
1. end_speed (x-axis) vs z_pos (y-axis) with function: end_speed / z_pos
2. z_pos (x-axis) vs end_speed (y-axis) with function: z_pos / end_speed

All plots are saved in the 'plots/' directory.
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.interpolate import griddata

def read_hbp_data(db_path='database/hbpdata.db'):
    """
    Read HBP data from the SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        tuple: (end_speed, z_pos) arrays
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read all data from the hbpdata table
    cursor.execute('SELECT end_speed, z_pos FROM hbpdata WHERE end_speed IS NOT NULL AND z_pos IS NOT NULL AND z_pos != 0 AND end_speed != 0')
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No valid data found in the database.")
        return None, None
    
    # Extract columns
    end_speed = np.array([row[0] for row in data])
    z_pos = np.array([row[1] for row in data])
    
    return end_speed, z_pos

def create_topographic_plots(end_speed, z_pos, output_dir='plots/'):
    """
    Create two topographic plots as specified.
    
    Args:
        end_speed (array): end speed data
        z_pos (array): z position data
        output_dir (str): Directory to save the plots
    """
    # Create figure for both plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: end_speed (x-axis) vs z_pos (y-axis) with function end_speed / z_pos
    # Create grid for interpolation
    speed_min, speed_max = min(end_speed), max(end_speed)
    z_min, z_max = min(z_pos), max(z_pos)
    
    # Create grid points
    speed_grid = np.linspace(speed_min, speed_max, 100)
    z_grid = np.linspace(z_min, z_max, 100)
    SPEED, Z = np.meshgrid(speed_grid, z_grid)
    
    # Calculate function: end_speed / z_pos
    function1 = end_speed / z_pos
    
    # Interpolate for smooth topographic plot
    function1_grid = griddata((end_speed, z_pos), function1, (SPEED, Z), method='cubic', fill_value=0)
    
    # Plot topographic contour
    contour1 = ax1.contourf(SPEED, Z, function1_grid, levels=20, cmap='terrain')
    fig.colorbar(contour1, ax=ax1, label='end_speed / z_pos')
    ax1.set_xlabel('End Speed (mph)', fontsize=12)
    ax1.set_ylabel('Z Position (feet)', fontsize=12)
    ax1.set_title('Topographic: end_speed / z_pos', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: z_pos (x-axis) vs end_speed (y-axis) with function z_pos / end_speed
    function2 = z_pos / end_speed
    
    # Interpolate for smooth topographic plot
    function2_grid = griddata((z_pos, end_speed), function2, (Z, SPEED), method='cubic', fill_value=0)
    
    # Plot topographic contour
    contour2 = ax2.contourf(Z, SPEED, function2_grid, levels=20, cmap='terrain')
    fig.colorbar(contour2, ax=ax2, label='z_pos / end_speed')
    ax2.set_xlabel('Z Position (feet)', fontsize=12)
    ax2.set_ylabel('End Speed (mph)', fontsize=12)
    ax2.set_title('Topographic: z_pos / end_speed', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # Save combined plot
    os.makedirs(output_dir, exist_ok=True)
    combined_path = os.path.join(output_dir, 'hbp_topographic_combined.png')
    fig.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined topographic plots saved to: {combined_path}")
    
    # Save individual plots
    fig, ax = plt.subplots(figsize=(10, 8))
    contour1 = ax.contourf(SPEED, Z, function1_grid, levels=20, cmap='terrain')
    fig.colorbar(contour1, ax=ax, label='end_speed / z_pos')
    ax.set_xlabel('End Speed (mph)', fontsize=12)
    ax.set_ylabel('Z Position (feet)', fontsize=12)
    ax.set_title('Topographic: end_speed / z_pos', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    output_path1 = os.path.join(output_dir, 'hbp_topographic_speed_z_ratio.png')
    fig.savefig(output_path1, dpi=300, bbox_inches='tight')
    print(f"Topographic plot 1 saved to: {output_path1}")
    plt.close()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    contour2 = ax.contourf(Z, SPEED, function2_grid, levels=20, cmap='terrain')
    fig.colorbar(contour2, ax=ax, label='z_pos / end_speed')
    ax.set_xlabel('Z Position (feet)', fontsize=12)
    ax.set_ylabel('End Speed (mph)', fontsize=12)
    ax.set_title('Topographic: z_pos / end_speed', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    output_path2 = os.path.join(output_dir, 'hbp_topographic_z_speed_ratio.png')
    fig.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"Topographic plot 2 saved to: {output_path2}")
    plt.close()

def main():
    """
    Main function to execute the topographic plotting pipeline.
    """
    print("Starting HBP topographic visualization...")
    
    # Read data from database
    print("Reading data from database...")
    end_speed, z_pos = read_hbp_data()
    
    if end_speed is None:
        print("No valid data found. Exiting.")
        return
    
    print(f"Found {len(end_speed)} data points")
    print(f"End speed range: {min(end_speed):.2f} to {max(end_speed):.2f} mph")
    print(f"Z position range: {min(z_pos):.2f} to {max(z_pos):.2f} feet")
    
    # Create topographic plots
    print("\nCreating topographic plots...")
    try:
        create_topographic_plots(end_speed, z_pos)
    except ImportError:
        print("scipy not available. Cannot create topographic plots.")
    except Exception as e:
        print(f"Error creating topographic plots: {e}")
    
    print("\nTopographic plots created successfully!")

if __name__ == '__main__':
    main()