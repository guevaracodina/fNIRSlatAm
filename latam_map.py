import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import LineString
import numpy as np
from matplotlib.collections import LineCollection

# Load connectivity matrix from CSV
conn_df = pd.read_csv('latam_conn.csv', index_col=0)

# Load world shapefile (assumes file is in the working directory)
world = gpd.read_file('ne_110m_admin_0_countries.shp')

def get_centroid(country_name, world_df):
    row = world_df[world_df['NAME'].str.lower() == country_name.lower()]
    if not row.empty:
        return row.iloc[0].geometry.centroid
    alt_names = {
        'usa': 'United States of America',
        'united states': 'United States of America'
    }
    alt = alt_names.get(country_name.lower())
    if alt:
        row = world_df[world_df['NAME'].str.lower() == alt.lower()]
        if not row.empty:
            return row.iloc[0].geometry.centroid
    return None

def create_arc(p0, p2, curvature=0.2, num_points=200):
    # Generate a quadratic Bézier curve from p0 to p2.
    x0, y0 = p0.x, p0.y
    x2, y2 = p2.x, p2.y
    xm, ym = (x0 + x2) / 2, (y0 + y2) / 2
    dx, dy = x2 - x0, y2 - y0
    perp_x, perp_y = -dy, dx
    length = np.hypot(perp_x, perp_y)
    if length == 0:
        return LineString([p0, p2])
    perp_x, perp_y = perp_x / length, perp_y / length
    dist = np.hypot(dx, dy)
    offset = dist * curvature
    control = (xm + perp_x * offset, ym + perp_y * offset)
    
    t_vals = np.linspace(0, 1, num_points)
    points = [((1-t)**2 * x0 + 2*(1-t)*t*control[0] + t**2*x2,
               (1-t)**2 * y0 + 2*(1-t)*t*control[1] + t**2*y2)
              for t in t_vals]
    return LineString(points)

def plot_variable_width_curve(ax, line, count, transform,
                              base_width=0.05, max_width=1.0, sigma=0.2):
    """
    Splits the curve into segments and draws them with a Gaussian profile
    (thin at the ends, thick in the middle) multiplied by the connection count.
    """
    x, y = line.xy
    segments = []
    lw_list = []
    n = len(x)
    for i in range(n - 1):
        t = (i + 0.5) / (n - 1)
        lw = base_width + (max_width - base_width) * np.exp(-((t - 0.5)**2)/(2*sigma**2))
        lw_list.append(lw * count)
        segments.append(((x[i], y[i]), (x[i+1], y[i+1])))
    lc = LineCollection(segments, linewidths=lw_list, colors='red', alpha=0.1,
                          joinstyle='round', capstyle='round', transform=transform)
    ax.add_collection(lc)

# Build arc data (skip self connections)
arc_data = []
for latam_country, row in conn_df.iterrows():
    source_centroid = get_centroid(latam_country, world)
    if source_centroid is None:
        print(f"Centroid for {latam_country} not found, skipping.")
        continue
    for target_country, count in row.items():
        if pd.notnull(count) and count > 0:
            if latam_country.lower() == target_country.lower():
                continue  # Skip self connections
            target_centroid = get_centroid(target_country, world)
            if target_centroid is None:
                print(f"Centroid for {target_country} not found, skipping.")
                continue
            arc = create_arc(source_centroid, target_centroid, curvature=0.2, num_points=200)
            arc_data.append({
                'source': latam_country,
                'target': target_country,
                'count': int(count),
                'geometry': arc
            })

# ---------------------------
# Figure 1: Original Projection
# ---------------------------
proj = ccrs.Orthographic(central_longitude=-60, central_latitude=15)
fig = plt.figure(figsize=(15, 10))
ax = plt.axes(projection=proj)
ax.set_global()
ax.add_feature(cfeature.LAND, facecolor='lightgrey')
ax.add_feature(cfeature.OCEAN, facecolor='white')
ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)

for arc_item in arc_data:
    geom = arc_item['geometry']
    count = arc_item['count']
    plot_variable_width_curve(ax, geom, count, transform=ccrs.PlateCarree(),
                              base_width=0.05, max_width=1.0, sigma=0.2)

plt.title('Country Connectivity Map (Orthographic Projection)')
plt.savefig('country_connectivity_map_variable_width_solid.png', dpi=300)
plt.show(block=False)

# ---------------------------
# Figure 2: Other Side of the Earth
# ---------------------------
proj_other = ccrs.Orthographic(central_longitude=120, central_latitude=-15)
fig2 = plt.figure(figsize=(15, 10))
ax2 = plt.axes(projection=proj_other)
ax2.set_global()
ax2.add_feature(cfeature.LAND, facecolor='lightgrey')
ax2.add_feature(cfeature.OCEAN, facecolor='white')
ax2.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.5)
ax2.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)

for arc_item in arc_data:
    geom = arc_item['geometry']
    count = arc_item['count']
    plot_variable_width_curve(ax2, geom, count, transform=ccrs.PlateCarree(),
                              base_width=0.05, max_width=1.0, sigma=0.2)

plt.title('Country Connectivity Map (Other Side of the Earth)')
plt.savefig('country_connectivity_map_other_side.png', dpi=300)
plt.show(block=False)
