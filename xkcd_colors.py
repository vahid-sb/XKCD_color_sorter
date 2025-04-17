#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 10:50:12 2025

@author: Vahid S. Bokharaie
"""

import pandas as pd
import colorsys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors as rl_colors

def draw_colors_to_page(c, df_chunk, page_num, param):
    """Save colors, their names and HSV value in a pdf file."""
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 770, f"XKCD colors (HSV - Sorted by {param}) - Page {page_num + 1}")

    # Layout grid settings
    columns = 4
    rows = 15
    total_per_page = columns * rows

    swatch_width = 40
    swatch_height = 20
    cell_width = 140
    cell_height = 50

    x_margin = 40
    y_start = 740

    c.setFont("Helvetica", 8)

    for i, (_, row) in enumerate(df_chunk.iterrows()):
        if i >= total_per_page:
            break  # safety check

        row_idx, col_idx = divmod(i, columns)
        x = x_margin + col_idx * cell_width
        y = y_start - row_idx * cell_height

        hex_val = row["RGBHex"]
        name = row["ColorName"]
        h, s, v = row["HSV"]

        # Color swatch
        try:
            c.setFillColor(rl_colors.HexColor(hex_val))
        except:
            c.setFillColor(rl_colors.black)
        c.rect(x, y, swatch_width, swatch_height, fill=1, stroke=0)

        # Text
        c.setFillColor(rl_colors.black)
        c.drawString(x + swatch_width + 5, y + swatch_height - 2, name[:20])
        c.drawString(x + swatch_width + 5, y - 8, f"({h:.3f}, {s:.3f}, {v:.3f})")

def hex_to_hsv(hex_color):
    """Convert RGB colors to HSV coordinates."""
    if not isinstance(hex_color, str):
        return (0.0, 0.0, 0.0)  # Or return None, depending on your preference
    hex_color = hex_color.strip().lstrip('#')
    if len(hex_color) != 6:
        return (0.0, 0.0, 0.0)
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return round(h, 3), round(s, 3), round(v, 3)
    except ValueError:
        return (0.0, 0.0, 0.0)    
  
if __name__ == "__main__":
    
    # Step 1: Load rgb.txt, skip the header
    df = pd.read_csv("rgb.txt", sep="\t", header=None, skiprows=1,
                     index_col=False, names=["ColorName", "RGBHex"])
    
    # Step 2: Convert RGB hex to HSV
    df["HSV"] = df["RGBHex"].apply(hex_to_hsv)
    df = df[df["HSV"].notnull()]
    
    from itertools import permutations
    
    # Step 3: Extract HSV components
    df["Hue"] = df["HSV"].apply(lambda x: x[0])
    df["Saturation"] = df["HSV"].apply(lambda x: x[1])
    df["Value"] = df["HSV"].apply(lambda x: x[2])
    
    # Step 4: Sort by combinations of two fixed HSV values
    pairs = [("Hue", "Saturation", "Value"),
             ("Hue", "Value", "Saturation"),
             ("Saturation", "Value", "Hue")]
    
    for fixed1, fixed2, varying in pairs:
        # Round fixed values to group similar colors (e.g., to 1 decimal point)
        df["Fixed1"] = df[fixed1].round(1)
        df["Fixed2"] = df[fixed2].round(1)
    
        df_sorted = df.sort_values(by=["Fixed1", "Fixed2", varying]).reset_index(drop=True)
    
        chunk_size = 60
        chunks = [df_sorted.iloc[i:i + chunk_size] for i in range(0, len(df_sorted), chunk_size)]
    
        output_pdf = f"all_xkcd_colors_sorted_by_{varying}_within_{fixed1}_and_{fixed2}.pdf"
        c = canvas.Canvas(output_pdf, pagesize=letter)
    
        for i, chunk in enumerate(chunks):
            draw_colors_to_page(c, chunk.reset_index(drop=True), i, f"{varying} (Grouped by {fixed1}, {fixed2})")
            c.showPage()
    
        c.save()
        print(f"Saved: {output_pdf}")