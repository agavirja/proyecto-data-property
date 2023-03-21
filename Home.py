import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
import copy
import mysql.connector as sql
from bs4 import BeautifulSoup
from shapely.geometry import Polygon,Point
from price_parser import Price

st.set_page_config(layout="wide")


# streamlit run D:\Dropbox\Empresa\proyecto-data-property\Home.py
# https://streamlit.io/
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\proyecto-data-property"
