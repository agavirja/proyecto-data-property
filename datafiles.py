import streamlit as st
import pandas as pd

#@st.experimental_memo
@st.cache(allow_output_mutation=True)
def getdatamarketcoddir(filename,fcoddir=None):
    data = pd.read_pickle(filename,compression='gzip')
    if fcoddir is not None and fcoddir!="":
        data = data[data['coddir']==fcoddir]
    return data

@st.experimental_memo
def getdatamarketsimilar(filename,inputvar):
    data = pd.read_pickle(filename,compression='gzip')
    idd  = True
    if 'areaconstruida' in inputvar and inputvar['areaconstruida']>0:
        areamin = inputvar['areaconstruida']*0.8
        areamax = inputvar['areaconstruida']*1.2
        idd     = (idd) & (data['areaconstruida']>=areamin)  & (data['areaconstruida']<=areamax)
    if 'habitaciones' in inputvar and inputvar['habitaciones']>0:
        idd     = (idd) & (data['habitaciones']>=inputvar['habitaciones'])
    if 'banos' in inputvar and inputvar['banos']>0:
        idd     = (idd) & (data['banos']>=inputvar['banos'])
    if 'garajes' in inputvar and inputvar['garajes']>0:
        idd     = (idd) & (data['garajes']>=inputvar['garajes'])
    if 'estrato' in inputvar and inputvar['estrato']>0:
        idd     = (idd) & (data['estrato']==inputvar['estrato'])
    data = data[idd]
    return data

@st.experimental_memo
def getdatacatastro(filename):
    data = pd.read_pickle(filename,compression='gzip')
    if 'geometry' in data: del data['geometry']
    return data