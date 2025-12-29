#!/usr/bin/env python3

import os
import pprint

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np

from typing import Optional

from . import basic as basic
from . import constants as const
from .configurator import ConfigReader


## -------------------------------------------------------------------------- ##
## GENERAL CONFIG
## -------------------------------------------------------------------------- ##

config    = ConfigReader(basic.verify_file_path(basic.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))
plot_dir  = config.get("paths", "plot_dir")
skeet_dir = config.get("paths", "skeet_dir")
video_dir = config.get("paths", "video_dir")


## -------------------------------------------------------------------------- ##
## PLOTTING FUNCTIONS
## -------------------------------------------------------------------------- ##

def plot_current_play_against_season(
    current_play: list, 
    all_season_data: list, 
    pitcher_info: list,
    batter_info: list,
    verbose_bool: Optional[bool] = False, 
    plot_dir: Optional[str] = plot_dir
) -> bool:
    game_date        = current_play[0][2]
    season,month,day = game_date.split('-')

    # Extract data for plotting with validation
    x_positions = []
    z_positions = []
    end_speeds  = []
    
    null_warnings = []
    for i, item in enumerate(all_season_data):
        # Check for None or empty values
        if item[6] is None or item[6] == '':
            null_warnings.append(f"Row {i+1}: x_pos is null/empty")
            continue
        if item[7] is None or item[7] == '':
            null_warnings.append(f"Row {i+1}: z_pos is null/empty")
            continue
        if item[5] is None or item[5] == '':
            null_warnings.append(f"Row {i+1}: end_speed is null/empty")
            continue
        
        x_positions.append(float(item[6]))  # x_pos (column 6)
        z_positions.append(float(item[7]))  # z_pos (column 7)
        end_speeds.append(float(item[5]))  # end_speed (column 5)
            
    
    # # Display warnings if any null/empty fields were found
    # if null_warnings:
    #     print(f"   ⚠️  Found {len(null_warnings)} rows with null/empty fields. Skipping that data.")
    
    # Check if we have any valid data to plot
    if not x_positions or not z_positions or not end_speeds:
        print(f"   ❌ No valid data available for plotting after filtering null/empty fields.")
        return False
        
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot home plate with regulation dimensions (17" wide, 8.5" parallel sides, 12" angled sides)
    # Draw home plate with correct shape: rectangle (17"x8.5") + triangle (17" base, 12" sides)
    # Convert inches to feet for consistency with other measurements
    home_plate_width = 1.4167  # 17 inches in feet
    rectangle_height = 0.7083  # 8.5 inches in feet
    triangle_height = np.sqrt(1.0**2 - (home_plate_width/2)**2)  # 12" sides using Pythagoras
    
    # Home plate corners (centered at x=0, top edge at z=0)
    # Top rectangle corners (17" wide, 8.5" tall)
    top_left = (-home_plate_width/2, 0)
    top_right = (home_plate_width/2, 0)
    bottom_right_rect = (home_plate_width/2, -rectangle_height)
    bottom_left_rect = (-home_plate_width/2, -rectangle_height)
    
    # Triangle point (12" sides from rectangle base)
    point = (0, -rectangle_height - triangle_height)
    
    home_plate_corners = [top_left, top_right, bottom_right_rect, point, bottom_left_rect]
    
    # Create home plate polygon (white, no label as requested)
    home_plate = plt.Polygon(home_plate_corners, 
                             closed=True, 
                             fill=True, 
                             facecolor='white',
                             edgecolor='black',
                             linewidth=2.0,
                             zorder=2)  # Draw above dirt but below data points
    ax.add_patch(home_plate)
    
    # Add horizontal line at z=0 (ground level)
    ax.axhline(y=0, color='black', linewidth=1.0, alpha=0.8, zorder=3)
    
    # Add explanatory label for area below z=0
    ax.text(0, -2, 
            "Anything in this area bounced in\nthe dirt before reaching home plate.",
            ha='center', va='center',
            fontsize=10, fontweight='normal',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))
    
    # Home plate label removed as requested
    
    # Plot strike zone box (if batter info contains strike zone data)
    strike_zone_corners = [
        (-0.708, batter_info.get('strike_zone_bot', 1.5)),
        (-0.708, batter_info.get('strike_zone_top', 3.5)),
        (0.708, batter_info.get('strike_zone_top', 3.5)),
        (0.708, batter_info.get('strike_zone_bot', 1.5))
    ]
    
    # Create strike zone box with no fill (outline only)
    strike_zone_box = plt.Polygon(strike_zone_corners, 
                                  closed=True, 
                                  fill=False,  # No fill as requested
                                  edgecolor='black',
                                  linewidth=1.0,
                                  zorder=1)  # Draw underneath scatter points
    ax.add_patch(strike_zone_box)
    
    # Strike zone label removed as requested
    
    # Define color gradient: blue at min speed, green at average speed, red at max speed
    min_speed = min(end_speeds)
    max_speed = max(end_speeds)
    avg_speed = (min_speed + max_speed) / 2
    speed_range = max_speed - min_speed
    
    # Create color array based on speed gradient (blue -> green -> red)
    colors = []
    for speed in end_speeds:
        if speed_range == 0:  # All speeds are the same
            # Use green for all points if no variation
            colors.append((0, 1, 0))  # RGB: green
        else:
            # Calculate position in the range (0 = min, 1 = max)
            position = (speed - min_speed) / speed_range
            
            # Blue to green to red gradient
            if position <= 0.5:  # Blue to green (min to average)
                # Ratio from 0 to 1 in the first half
                ratio = position * 2
                # RGB: blue (0,0,1) to green (0,1,0)
                colors.append((0, ratio, 1 - ratio))
            else:  # Green to red (average to max)
                # Ratio from 0 to 1 in the second half
                ratio = (position - 0.5) * 2
                # RGB: green (0,1,0) to red (1,0,0)
                colors.append((ratio, 1 - ratio, 0))
    
    # Create scatter plot
    scatter = ax.scatter(
        x_positions, 
        z_positions, 
        c=colors, 
        s=50, 
        alpha=0.7,
        edgecolors='black',
        linewidths=0.5
    )
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.jet, norm=plt.Normalize(vmin=min(end_speeds), vmax=max(end_speeds)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Pitch Speed (mph)', rotation=270, labelpad=15)
    
    # Highlight current play if it's in the season data
    try:
        # Validate current play data
        if (current_play[0][6] is None or current_play[0][6] == '' or
            current_play[0][7] is None or current_play[0][7] == '' or
            current_play[0][5] is None or current_play[0][5] == ''):
            print(f"   ⚠️  Current play has null/empty fields, skipping highlight")
            current_in_season = False
        else:
            current_x = float(current_play[0][6])
            current_z = float(current_play[0][7])
            current_speed = float(current_play[0][5])
    except (ValueError, TypeError, IndexError) as e:
        print(f"   ⚠️  Error processing current play data: {e}, skipping highlight")
        current_in_season = False
    
    # Check if current play is in this season's data
    def is_current_play_match(item):
        try:
            if item[6] is None or item[7] is None or item[5] is None:
                return False
            return (
                abs(float(item[6]) - current_x) < 0.01 and 
                abs(float(item[7]) - current_z) < 0.01 and
                abs(float(item[5]) - current_speed) < 0.01
            )
        except (ValueError, TypeError):
            return False
    
    current_in_season = any(is_current_play_match(item) for item in all_season_data)
    
    if current_in_season:
        # Determine color based on current play speed
        # Calculate current play color using the same gradient logic
        if speed_range == 0:  # All speeds are the same
            current_color = (0, 1, 0)  # RGB: green
        else:
            # Calculate position in the range (0 = min, 1 = max)
            position = (current_speed - min_speed) / speed_range
            
            # Blue to green to red gradient
            if position <= 0.5:  # Blue to green (min to average)
                # Ratio from 0 to 1 in the first half
                ratio = position * 2
                # RGB: blue (0,0,1) to green (0,1,0)
                current_color = (0, ratio, 1 - ratio)
            else:  # Green to red (average to max)
                # Ratio from 0 to 1 in the second half
                ratio = (position - 0.5) * 2
                # RGB: green (0,1,0) to red (1,0,0)
                current_color = (ratio, 1 - ratio, 0)
        
        ax.scatter(
            [current_x], 
            [current_z], 
            c=[current_color], 
            s=100,  # Twice as big as regular points (50 -> 100)
            alpha=1.0,
            edgecolors='yellow',  # Changed to thick yellow border as requested
            linewidths=3.0,  # Thick border as requested
            marker='s',  # Square marker as requested
        )
    else:
        return False
    
    # Add title and labels
    # ax.set_title(f'Hit-by-Pitch Events - {season} Season\\nColored by Pitch Speed', fontsize=14, pad=20)
    ax.set_title(f"{pitcher_info['name']} ({pitcher_info['primary_position']}) vs {batter_info['name']} ({batter_info['primary_position']}), {game_date}", fontsize=14, pad=20)
    ax.set_xlabel('X Position (feet from home plate)', fontsize=12)
    ax.set_ylabel('Z Position (feet from ground)', fontsize=12)
    
    # Add grid and legend
    ax.grid(True, alpha=0.3)
    
    # Create legend with data point count
    legend_elements = []
    if current_in_season:
        legend_elements.append(plt.Line2D([0], [0], marker='s', color='w', label=f"Current Play, {current_play[0][5]} mph",
                                         markerfacecolor=current_color, markersize=10, markeredgecolor='yellow', markeredgewidth=3.0))
    
    # Add data point count to legend
    data_point_count = len(x_positions)
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', label=f"{data_point_count} HBP in {season}",
                                     markerfacecolor='gray', markersize=8, markeredgecolor='black', markeredgewidth=0.5))
    
    # Add legend to plot
    ax.legend(handles=legend_elements, fontsize=10, loc='upper right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"{current_play[0][1]}_{current_play[0][0]}_{season}.png"
    plot_path = os.path.join(plot_dir, plot_filename)
    plt.savefig(plot_path, bbox_inches='tight')
    print(f"   🖼️  Saved season plot to: {plot_path}")
    
    plt.close(fig)
    
    return True

