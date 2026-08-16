import numpy as np
import pandas as pd


from bokeh.models import (
    ColorBar,
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
)
from bokeh.models.widgets import Select, Slider
from bokeh.palettes import Plasma256
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row


def lat_lon_to_mercator(lat, lon):
    r_major = 6378137.0
    x = r_major * np.radians(lon)
    scale = x / lon
    y = (
        180.0
        / np.pi
        * np.log(np.tan(np.pi / 4.0 + lat * (np.pi / 180.0) / 2.0))
        * scale
    )
    return x, y


df = pd.read_csv("District_Locations.csv")
df = df.rename(columns={"Long": "lat", "Lat": "lon"})

pop_2024_data = {
    "Colombo": 2375415, "Gampaha": 2436142, "Kalutara": 1305784, "Kandy": 1461895,
    "Matale": 526870, "Nuwaraeliya": 725280, "Galle": 1097372, "Matara": 837889,
    "Hambantota": 671418, "Jaffna": 594751, "Mannar": 123756, "Vavunia": 172312,
    "Mullativu": 122619, "Kilinochchi": 136710, "Batticoloa": 595918, "Ampara": 744551,
    "Trincomalee": 442745, "Kurunegala": 1768156, "Puttalam": 818816, "Anuradhapura": 960080,
    "Polonnaruwa": 447530, "Badulla": 872307, "Moneragala": 527585, "Ratnapura": 1145423,
    "Kegalle": 870476
}

area_data = {
    "Colombo": 699, "Gampaha": 1387, "Kalutara": 1598, "Kandy": 1940, "Matale": 1993,
    "Nuwaraeliya": 1741, "Galle": 1652, "Matara": 1282, "Hambantota": 2609, "Jaffna": 1025,
    "Mannar": 1996, "Vavunia": 1967, "Mullativu": 2617, "Kilinochchi": 1279, "Batticoloa": 2854,
    "Ampara": 4415, "Trincomalee": 2727, "Kurunegala": 4816, "Puttalam": 3072,
    "Anuradhapura": 7179, "Polonnaruwa": 3293, "Badulla": 2861, "Moneragala": 5639,
    "Ratnapura": 3275, "Kegalle": 1693
}

province_data = {
    "Colombo": "Western", "Gampaha": "Western", "Kalutara": "Western",
    "Kandy": "Central", "Matale": "Central", "Nuwaraeliya": "Central",
    "Galle": "Southern", "Matara": "Southern", "Hambantota": "Southern",
    "Jaffna": "Northern", "Kilinochchi": "Northern", "Mannar": "Northern",
    "Vavunia": "Northern", "Mullativu": "Northern", "Batticoloa": "Eastern",
    "Ampara": "Eastern", "Trincomalee": "Eastern", "Kurunegala": "North Western",
    "Puttalam": "North Western", "Anuradhapura": "North Central",
    "Polonnaruwa": "North Central", "Badulla": "Uva", "Moneragala": "Uva",
    "Ratnapura": "Sabaragamuwa", "Kegalle": "Sabaragamuwa"
}

df["population_2024"] = df["District"].map(pop_2024_data)
df["area_sqkm"] = df["District"].map(area_data)
df["province"] = df["District"].map(province_data)
df["density"] = (df["population_2024"] / df["area_sqkm"]).round(2)

x_coords, y_coords = [], []
for lat, lon in zip(df["lat"], df["lon"]):
    x, y = lat_lon_to_mercator(lat, lon)
    x_coords.append(x)
    y_coords.append(y)

df["x"] = x_coords
df["y"] = y_coords
df["size"] = np.sqrt(df["density"]) * 0.9 + 14

sl_min_x, sl_min_y = lat_lon_to_mercator(5.8, 79.2)
sl_max_x, sl_max_y = lat_lon_to_mercator(9.9, 82.2)


source = ColumnDataSource(df)


p = figure(
    title="SRI LANKA POPULATION DENSITY ANALYTICS (2024)",
    x_range=(sl_min_x, sl_max_x),
    y_range=(sl_min_y, sl_max_y),
    x_axis_type="mercator",
    y_axis_type="mercator",
    height=600,
    width=700,
    background_fill_color="#1a1c23",
    border_fill_color="#1a1c23",
    outline_line_color=None,
    tools="pan,wheel_zoom,box_zoom,reset",
)

p.add_tile("OSM")

color_mapper = LinearColorMapper(
    palette=Plasma256, low=df["density"].min(), high=df["density"].max()
)

p.scatter(
    x="x",
    y="y",
    size="size",
    source=source,
    fill_color={"field": "density", "transform": color_mapper},
    fill_alpha=0.85,
    line_color="#ffffff",
    line_width=1.8,
    hover_fill_color="#00ffff",
    hover_line_color="#ffffff",
)

hover_html = """
    <div style="background-color: #262932; padding: 10px; border-radius: 8px; color: #ffffff; font-family: sans-serif;">
        <h3 style="margin: 0 0 5px 0; color: #00e676; border-bottom: 1px solid #444; padding-bottom: 3px;">@District District</h3>
        <p style="margin: 3px 0; font-size: 13px;"><b>Province:</b> <span style="color: #ffb74d;">@province</span></p>
        <p style="margin: 3px 0; font-size: 13px;"><b>Population (2024):</b> @population_2024{0,0}</p>
        <p style="margin: 3px 0; font-size: 13px;"><b>Density:</b> <span style="color: #00e5ff; font-weight: bold;">@density / sq km</span></p>
        <p style="margin: 3px 0; font-size: 12px; color: #aaa;"><b>Area:</b> @area_sqkm sq km</p>
    </div>
"""
p.add_tools(HoverTool(tooltips=hover_html))

color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=12,
    width=14,
    location=(0, 0),
    background_fill_color="#1a1c23",
    major_label_text_color="#ffffff",
    title="Density",
    title_text_color="#ffffff",
)
p.add_layout(color_bar, "right")

p.xaxis.visible = False
p.yaxis.visible = False
p.title.text_color = "#ffffff"
p.title.text_font_size = "14pt"
p.title.text_font_style = "bold"

# Widgets Setup
district_list = ["All"] + sorted(list(df["District"].unique()))
province_list = ["All"] + sorted(list(df["province"].unique()))

select_district = Select(title="Zoom District:", value="All", options=district_list, width=220)
select_province = Select(title="Filter Province:", value="All", options=province_list, width=220)
slider_density = Slider(start=0, end=3500, value=0, step=100, title="Min Density:", width=220)


def update_data(attr, old, new):
    filtered_df = df.copy()

    
    if select_province.value != "All":
        filtered_df = filtered_df[filtered_df["province"] == select_province.value]

   
    filtered_df = filtered_df[filtered_df["density"] >= slider_density.value]

    
    source.data = ColumnDataSource.from_df(filtered_df)

    # Dynamic Zoom Logic
    if select_district.value == "All":
        p.x_range.start = sl_min_x
        p.x_range.end = sl_max_x
        p.y_range.start = sl_min_y
        p.y_range.end = sl_max_y
    else:
        dist_data = df[df["District"] == select_district.value]
        if not dist_data.empty:
            cx = dist_data["x"].values[0]
            cy = dist_data["y"].values[0]
            offset = 35000
            p.x_range.start = cx - offset
            p.x_range.end = cx + offset
            p.y_range.start = cy - offset
            p.y_range.end = cy + offset


select_district.on_change('value', update_data)
select_province.on_change('value', update_data)
slider_density.on_change('value', update_data)


controls_panel = column(select_district, select_province, slider_density, margin=(10, 20, 10, 0))
layout = row(controls_panel, p)


curdoc().add_root(layout)
curdoc().title = "Sri Lanka Geo-Dashboard"