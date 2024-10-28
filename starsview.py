#!/usr/bin/env python
# coding: utf-8

# In[1]:


import geopandas as gpd
import requests
import json
import folium
import fiona
from folium.plugins import Search


# In[2]:


# ls -l


# In[3]:


#check layer yang ada di dalam geodatabase file

list_layer = fiona.listlayers("astronomyData/astronomyWGS84.gdb")
list_layer


# In[4]:


#simpan data ke dalam bentuk geodataframe untuk layer yang ingin digunakan
#data memiliki sumbu Z jika ingin digunakan untuk visualisasi 3D

data_stars = gpd.read_file("astronomyData/astronomyWGS84.gdb", layer='StarsNamed2')
constellations = gpd.read_file("astronomyData/astronomyWGS84.gdb", layer='Constellations')
asterism = gpd.read_file("astronomyData/astronomyWGS84.gdb", layer='asterism')
graticul = gpd.read_file("astronomyData/astronomyWGS84.gdb", layer='graticul')
refline = gpd.read_file("astronomyData/astronomyWGS84.gdb/", layer='refline')
milkyway = gpd.read_file("astronomyData/astronomyWGS84.gdb/", layer='MilkyWay')
constell = gpd.read_file("astronomyData/astronomyWGS84.gdb/", layer='constell')


# In[5]:


#tambah basemap. ada beberapa basemap yang bisa digunakan, silahkan cek dokumentasi folium

m = folium.Map(location=(5, 5), zoom_start=3, tiles='cartodbdark_matter')
m


# In[6]:


#tambahkan layer constellation. layer yang ditambahkan pertama akan jadi layer yang paling belakang

constell_lyr = folium.GeoJson(
    constell,
     style_function=lambda feature: {
        "fillColor": "#00008B",
        "weight": 0.5,
         "fillOpacity": 0.1
    },
    name="Constell",
    tooltip=folium.GeoJsonTooltip(
        fields=["NAME"], aliases=["GENITIVE"], localize=True
    )
).add_to(m)
m


# In[7]:


# tambahkan layer graticul

graticul_lyr = folium.GeoJson(
    graticul,
     style_function=lambda x: {
        "color": "#BF0000",
        "weight": 0.5,
        'fillOpacity': 0.001
       },
    name="Graticul"
).add_to(m)
m


# In[8]:


#tambahkan layer milkyway. gunakan dua warna untuk membedakan inner dan outer

folium.GeoJson(
    milkyway,
    name = "Milkyway",
    style_function=lambda feature: {
        "fillColor": "#091057"
        if "outer" in feature["properties"]["type"].lower()
        else "#608BC1",
        "color": "white",
        "weight":0.01
    },
).add_to(m)

m


# In[9]:


refline["TYPE"]


# In[10]:


#gunakan 2 bentuk untuk membedakan garis equator dan ecpliptic

folium.GeoJson(
    refline,
     style_function=lambda feature: {
         "color": "#DD761C",
         "dashArray": "5, 5"
        if "ecliptic" in feature["properties"]["TYPE"].lower()
        else "#7C93C3",
        "weight":1
       },
    name="Refline"
).add_to(m)
m


# In[11]:


#tambahkan column untuk link referensi ke wikipedia

asterism["tempname"] = asterism["CONSNAME"].str.replace(" ", "_")+'_(constellation)'
asterism["reference"]= '<a href="https://en.wikipedia.org/wiki/'+asterism.tempname+'" target=_blank>'+ asterism["CONSNAME"]+"</a>"
asterism.head()

#tambahkan layer asterism beserta widget search untuk mencari constellation yang ada di layer asterism 

search_group = folium.FeatureGroup(
    control=False
).add_to(m)

asterism_lyr = folium.GeoJson(
    asterism,
    name="Asterism",
     style_function=lambda feature: {
        "fillColor": "#0080FF",
        "weight": 1,
        "dashArray": "5, 5",
    },
    tooltip=folium.GeoJsonTooltip(fields=["CONSNAME", "reference"]),
    popup=folium.GeoJsonPopup(fields=["CONSNAME", "DESCRIPT","reference"])
).add_to(m).add_to(search_group)
m


# Untuk layer stars saya bagi menjadi dua untuk keperluan render. Salah satu kelemahan folium yaitu tidak bisa digunakan ketika data terlalu banyak, sehingga saya membagi menjadi dua dataframe.
# dataframe 1: berisi data stars yang memiliki nama, ada sekitar 150. layer ini akan diberi pop-up & tooltip
# dataframe 2: berisi data stars yang belum memiliki nama, ada sekitar 8000an. data ini hanya untuk view saja.

# In[12]:


stars = data_stars[data_stars["Stars_Named_COMNAME"].isnull()==False]
stars.shape


# In[13]:


stars = stars.reset_index()


# In[14]:


stars["Stars_Named_VMAG"] = stars.Stars_Named_VMAG.astype(float)
stars['longitude']= stars.get_coordinates().x
stars['latitude']= stars.get_coordinates().y


# In[15]:


starss = data_stars[data_stars['Stars_Named_COMNAME'].isnull()==True]
starss.shape


# In[16]:


starss["Stars_Named_VMAG"] = starss.Stars_Named_VMAG.astype(float)
starss['longitude']= starss.get_coordinates().x
starss['latitude']= starss.get_coordinates().y


# In[17]:


starss.shape


# In[18]:


starssz = starss[:1500]
starssx = starss[1500:]


# In[19]:


for index, row in starssz.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['Stars_Named_VMAG'],
        color="white",
        weight=0.01,
        fill=True,
        fill_color="white",
        fill_opacity=0.2
    ).add_to(m)

for index, row in starssx.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['Stars_Named_VMAG']*0.01,
        color="white",
        weight=0.01,
        fill=True,
        fill_color="white",
        fill_opacity=0.5
    ).add_to(m)

m


# In[20]:


#menambahkan layer stars yang sudah memiliki nama
stars_lyr = folium.GeoJson(
    stars,
    name="Stars",
    marker=folium.Circle(radius=3, fill_color="white", fill_opacity=0.4, color="white", weight=1),
    tooltip=folium.GeoJsonTooltip(fields=["Stars_Named_CommonName", "longitude", "latitude"]),
    popup=folium.GeoJsonPopup(fields=["Stars_Named_CommonName", "longitude", "latitude",]),
    highlight_function=lambda x: {"fillOpacity": 0.8},
    zoom_on_click=True,
).add_to(m)
m


# In[21]:


#tambahkan widget search untuk mencari constellation & stars

conssearch = Search(
    layer=search_group,
    geom_type="PolyLine",
    placeholder="Search for a Constellation",
    collapsed=True,
    search_label="CONSNAME",
    weight=1,
).add_to(m)

starssearch = Search(
    layer=stars_lyr,
    geom_type="Point",
    placeholder="Search for a Star",
    collapsed=True,
    search_label="Stars_Named_COMNAME",
).add_to(m)


# In[22]:


#tambahkan widget untuk layer list, default ada di sebelah kanan atas
folium.LayerControl().add_to(m)

m


# In[ ]:





# In[23]:


#save semua hasil visualisasi dalam html

m.save("starsview.html")


# In[ ]:




