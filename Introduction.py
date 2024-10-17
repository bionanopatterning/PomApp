import streamlit as st
import json
import os
import copy
from PIL import Image
import pandas as pd
import numpy as np
from render import parse_feature_library, FeatureLibraryFeature
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Introduction",
    layout='wide'
)

with open("project_configuration.json", 'r') as f:
    project_configuration = json.load(f)


feature_library = parse_feature_library("feature_library.txt")
df = pd.read_excel(os.path.join(project_configuration["root"], "summary.xlsx"), index_col=0)
df = df.dropna(axis=0)


with open("project_configuration.json", 'r') as f:
    project_configuration = json.load(f)


def get_image(tomo, image):
    image_dir = image.split("_")[0]
    img_path = os.path.join("images", image_dir, f"{tomo}_{image}.png")
    if os.path.exists(img_path):
        return Image.open(img_path)
    else:
        return Image.fromarray(np.zeros((128, 128)), mode='L')


def recolor(color, style=0):
    if style == 0:
        return (np.array(color) / 2.0 + 0.5)
    if style == 1:
        return (np.array(color) / 8 + 0.875)
    else:
        return color


def ontology_summary(df, ontology):
    odf = copy.deepcopy(df)
    to_drop = project_configuration["macromolecules"] + project_configuration["soft_ignore_in_summary"]
    if ontology in to_drop:
        to_drop.remove(ontology)
    odf.drop(columns=to_drop)
    best_n = 20
    st.header(f"{ontology}")
    # get highest and lowest valued images fo r this ontolgyo.
    o_in_top3 = df.apply(lambda row: ontology in row.nlargest(5).index, axis=1).sum()
    st.markdown(f"**{ontology.capitalize()}** is a top 5  component in **{o_in_top3}** tomograms, with the total {ontology.lower()} volume in the full dataset equivalent to approximately **{df[ontology].sum() / 100.0:.0f}** original tomogram volumes.")

    sorted_df = odf.sort_values(by=ontology, ascending=False)
    tomo_top = sorted_df.head(best_n).sample(n=1).index[0]
    tomo_bot = sorted_df.tail(best_n).sample(n=1).index[0]
    c1, c2 = st.columns(2)
    with c1:
        top_caption_link = f"/Browse_tomograms?tomo_id={tomo_top}"
        st.image(get_image(tomo_top, "density").transpose(Image.FLIP_TOP_BOTTOM), caption=f"High {ontology} content:", use_column_width=True)
        st.markdown(f"<p style='text-align: center;margin-top: -20px;font-size: 13px;'><a href='{top_caption_link}'>{tomo_top}</a></p>", unsafe_allow_html=True)
    with c2:
        bot_caption_link = f"/Browse_tomograms?tomo_id={tomo_bot}"
        st.image(get_image(tomo_bot, "density").transpose(Image.FLIP_TOP_BOTTOM), caption=f"Low {ontology} content:", use_column_width=True)
        st.markdown(f"<p style='text-align: center;margin-top: -20px;font-size: 13px;'><a href='{bot_caption_link}'>{tomo_bot}</a></p>", unsafe_allow_html=True)



c1, c2, c3 = st.columns([0.2, 0.6, 0.2])
with c2:
    st.title("Introduction")
    macromolecules = project_configuration["macromolecules"]
    if "Density" in macromolecules:
        macromolecules.remove("Density")

    ontologies = project_configuration["ontologies"]
    n_volumes = len(df) * (len(macromolecules) + len(ontologies) + 2)

    st.text(f"{len(df)} tomograms, {len(macromolecules)} macromolecules, {len(ontologies) + 1} ontologies, {n_volumes} volumes.")

    #st.markdown(f"**What do we do when the volume of data becomes unmanagable?**")

    st.markdown(f"_**P**roject **O**ntology **M**etasegmentation (**Pom**)_ is an attempt at summarizing and organising large electron cryo-tomography (cryoET) datasets "
                f"_via_ semi-supervised segmentation of a relatively large number of _macromolecules_ and _ontologies_, using the amazing **data by Ron Kelley and Sagar Khavnekar et al.** of FIB-milled Chlamydomonas reinhardtii tomograms, available via the [CZI's CryoET Data Portal.](https://cryoetdataportal.czscience.com/datasets/10302)")

    st.markdown(f"All segmentations, visualizations, and other data shared on these pages, including this summary report, were generated using Pom - a _work-in-progress_ Python cli module for making sense of large datasets.")

    st.text("")
    st.markdown(f'<div style="text-align: center;"><b>At a glance: ensemble composition of {len(df)} tomograms</b></div>', unsafe_allow_html=True)
    st.text("")
    pie_data = dict()
    for k in df.columns:
        if k in project_configuration["ontologies"] + ["Unknown"] and not k in project_configuration["soft_ignore_in_summary"]:
            pie_data[k] = df[k].sum()
    pie_data = sorted(pie_data.items(), key= lambda x: x[1], reverse=True)
    rearranged_pie_data = []
    for i in range(len(pie_data) // 2):
        rearranged_pie_data.append(pie_data[i])
        rearranged_pie_data.append(pie_data[-(i + 1)])
    if len(pie_data) % 2 == 1:
        rearranged_pie_data.append(pie_data[len(pie_data) // 2])
    # Unpack the rearranged data into separate lists
    pie_data = dict()
    for l, v in rearranged_pie_data:
        pie_data[l] = v

    pie_colours = [recolor(feature_library[label].colour) for label in pie_data]

    fig, ax = plt.subplots()
    ax.pie(
        pie_data.values(),  # Values for pie chart
        labels=pie_data.keys(),  # Labels for pie chart
        colors=pie_colours,  # Custom colors for each slice
        autopct='%1.1f%%',  # Show percentage
        startangle=90,  # Start angle for better alignment
        explode=[0.0] * len(pie_data),
        textprops={'fontsize': 6}
    )
    # Equal aspect ratio ensures the pie is drawn as a circle.
    ax.axis('equal')

    # Display the pie chart in Streamlit
    st.pyplot(fig)

    ontologies = project_configuration["ontologies"]
    if "Void" in ontologies:
        ontologies.remove("Void")
        ontologies.append("Void")

    ontologies.append("Unknown")
    for o in ontologies:
        ontology_summary(df, o)
