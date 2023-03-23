import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
import copy
from bs4 import BeautifulSoup
from shapely.geometry import Polygon
from price_parser import Price

from datafiles import getdatamarketcoddir

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")
    

formato = [
           {'name':'data_market','value':pd.DataFrame()},
           {'name':'tiponegocio','value':'Venta'},
           {'name':'vardep','value':'valorventa'},
           {'name':'polygon','value':None},
           {'name':'lastpolygonactive','value':None},
           {'name':'zoom_start','value':13},
           {'name':'latitud','value':4.687215},
           {'name':'longitud','value':-74.056390},
           {'name':'maxinmuebles','value':150},
]
for i in formato:
    if i['name'] not in st.session_state: 
        st.session_state[i['name']] = i['value']
    
if 'venta' in st.session_state.tiponegocio.lower():
    filename                = 'data/data_market_venta_bogota'
    #filename                = r'D:\Dropbox\Empresa\proyecto-data-property\data\data_market_venta_bogota'
    st.session_state.vardep = 'valorventa'

if 'arriendo' in st.session_state.tiponegocio.lower():
    filename                = 'data/data_market_arriendo_bogota'
    #filename                = r'D:\Dropbox\Empresa\proyecto-data-property\data\data_market_arriendo_bogota'
    st.session_state.vardep = 'valorarriendo'
    
data    = getdatamarketcoddir(filename)
formato = [
            {'name':'preciomin','value':f'${int(data[st.session_state.vardep].min()):,.0f}'},
            {'name':'preciomax','value':f'${int(data[st.session_state.vardep].max()):,.0f}'},
            {'name':'areamin','value':int(data['areaconstruida'].min())},
            {'name':'areamax','value':int(data['areaconstruida'].max())},
            {'name':'antiguedamin','value':int(data['antiguedad'].min())},
            {'name':'antiguedamax','value':int(data['antiguedad'].max())},
            {'name':'estratomin','value':int(data['estrato'].min())},
            {'name':'estratomax','value':int(data['estrato'].max())}, 
            {'name':'habitacionmin','value':int(data['habitaciones'].min())},
            {'name':'habitacionmax','value':int(data['habitaciones'].max())}, 
            {'name':'banosmin','value':int(data['banos'].min())},
            {'name':'banosmax','value':int(data['banos'].max())},  
            {'name':'garajesmin','value':int(data['garajes'].min())},
            {'name':'garajesmax','value':int(data['garajes'].max())},     
            {'name':'filterdata','value':'Sin filtrar'},         
        ]

for i in formato:
    if i['name'] not in st.session_state: 
        st.session_state[i['name']] = i['value']    
  
if 'initialdata' not in st.session_state: 
    st.session_state.initialdata = copy.deepcopy(data)
         
def truncatedata():
    if st.session_state.data_market.empty is False and len(st.session_state.data_market)>st.session_state.maxinmuebles:
        st.session_state.data_market = st.session_state.data_market.iloc[0:st.session_state.maxinmuebles,:]

def onchange():

    st.session_state.initialdata.index = range(len(st.session_state.initialdata))
    idd = st.session_state.initialdata.index>=0

    #-------------------------------------------------------------------------#
    # Precio
        # Precio min
    valuemin = Price.fromstring(st.session_state.preciomin).amount_float
    valuemax = Price.fromstring(st.session_state.preciomax).amount_float
    if valuemax<=valuemin: valuemax = valuemin*1.05
    idd = (idd) & (st.session_state.initialdata[st.session_state.vardep]>=valuemin)
    st.session_state.preciomin = f'${valuemin:,.0f}'
    
        # Precio max
    idd = (idd) & (st.session_state.initialdata[st.session_state.vardep]<=valuemax)
    st.session_state.preciomax = f'${valuemax:,.0f}'
    
    #-------------------------------------------------------------------------#
    # Area
        # Area min
    if st.session_state.areamin>=st.session_state.areamax: st.session_state.areamin = st.session_state.areamax-1
    idd = (idd) & (st.session_state.initialdata['areaconstruida']>=st.session_state.areamin)

        # Area max
    idd = (idd) & (st.session_state.initialdata['areaconstruida']<=st.session_state.areamax)

    #-------------------------------------------------------------------------#
    # Antiguedad
        # Antiguedad min
    #if st.session_state.antiguedamin>=st.session_state.antiguedamax: st.session_state.antiguedamin = st.session_state.antiguedamax-1
    #idd = (idd) & ((st.session_state.initialdata['antiguedad']>=st.session_state.antiguedamin) | (st.session_state.initialdata['antiguedad'].isnull()))

        # Antiguedad max
    #idd = (idd) & ((st.session_state.initialdata['antiguedad']<=st.session_state.antiguedamax) | (st.session_state.initialdata['antiguedad'].isnull()))

    #-------------------------------------------------------------------------#
    # Estrato
        # Estrato min
    if st.session_state.estratomin>st.session_state.estratomax: st.session_state.estratomin = copy.deepcopy(st.session_state.estratomax)
    if st.session_state.estratomax<st.session_state.estratomin: st.session_state.estratomax = copy.deepcopy(st.session_state.estratomin)
    idd = (idd) & (st.session_state.initialdata['estrato']>=st.session_state.estratomin)

        # Estrato max
    idd = (idd) & (st.session_state.initialdata['estrato']<=st.session_state.estratomax)
    
    #-------------------------------------------------------------------------#
    # Habitaciones
        # Habitaciones min
    if st.session_state.habitacionmin>st.session_state.habitacionmax: st.session_state.habitacionmin = copy.deepcopy(st.session_state.habitacionmax)
    if st.session_state.habitacionmax<st.session_state.habitacionmin: st.session_state.habitacionmax = copy.deepcopy(st.session_state.habitacionmin)
    idd = (idd) & (st.session_state.initialdata['habitaciones']>=st.session_state.habitacionmin)

        # Habitaciones max
    idd = (idd) & (st.session_state.initialdata['habitaciones']<=st.session_state.habitacionmax)
    
    #-------------------------------------------------------------------------#
    # Baños
        # Baños min
    if st.session_state.banosmin>st.session_state.banosmax: st.session_state.banosmin = copy.deepcopy(st.session_state.banosmax)
    if st.session_state.banosmax<st.session_state.banosmin: st.session_state.banosmax = copy.deepcopy(st.session_state.banosmin)
    idd = (idd) & (st.session_state.initialdata['banos']>=st.session_state.banosmin)

        # Baños max
    idd = (idd) & (st.session_state.initialdata['banos']<=st.session_state.banosmax)
    
    #-------------------------------------------------------------------------#
    # Garajes
        # Garajes min
    if st.session_state.garajesmin>st.session_state.garajesmax: st.session_state.garajesmin = copy.deepcopy(st.session_state.garajesmax)
    if st.session_state.garajesmax<st.session_state.garajesmin: st.session_state.garajesmax = copy.deepcopy(st.session_state.garajesmin)
    idd = (idd) & (st.session_state.initialdata['garajes']>=st.session_state.garajesmin)

        # Garajes max
    idd = (idd) & (st.session_state.initialdata['garajes']<=st.session_state.garajesmax)
        
    #-------------------------------------------------------------------------#
    # Filter data
    st.session_state.data_market = st.session_state.initialdata[idd]
        
        # Filtro por poligono
    if st.session_state.lastpolygonactive is not None:
        st.session_state.zoom_start = 15
        idd  = st.session_state.data_market['geometry'].apply(lambda x: st.session_state.lastpolygonactive.contains(x))
        if sum(idd)>0:
            st.session_state.data_market = st.session_state.data_market[idd]
            st.session_state.latitud     = st.session_state.data_market['latitud'].median()
            st.session_state.longitud    = st.session_state.data_market['longitud'].median()

    truncatedata()
         
def tiponegocio_change():
        
    if 'venta' in st.session_state.tiponegocio.lower():
        filename                = 'data/data_market_venta_bogota'
        #filename                = r'D:\Dropbox\Empresa\proyecto-data-property\data\data_market_venta_bogota'
        st.session_state.vardep = 'valorventa'
    
    if 'arriendo' in st.session_state.tiponegocio.lower():
        filename                = 'data/data_market_arriendo_bogota'
        #filename                = r'D:\Dropbox\Empresa\proyecto-data-property\data\data_market_arriendo_bogota'
        st.session_state.vardep = 'valorarriendo'
        
    data                           = getdatamarketcoddir(filename)
    st.session_state.initialdata   = copy.deepcopy(data)
    st.session_state.preciomin     = f'${int(st.session_state.initialdata[st.session_state.vardep].min()):,.0f}'
    st.session_state.preciomax     = f'${int(st.session_state.initialdata[st.session_state.vardep].max()):,.0f}'
    st.session_state.areamin       = int(st.session_state.initialdata['areaconstruida'].min())
    st.session_state.areamax       = int(st.session_state.initialdata['areaconstruida'].max())
    #st.session_state.antiguedamin = int(st.session_state.initialdata['antiguedad'].min())
    #st.session_state.antiguedamax = int(st.session_state.initialdata['antiguedad'].max())
    st.session_state.estratomin    = int(st.session_state.initialdata['estrato'].min())
    st.session_state.estratomax    = int(st.session_state.initialdata['estrato'].max())
    st.session_state.habitacionmin = int(st.session_state.initialdata['habitaciones'].min())
    st.session_state.habitacionmax = int(st.session_state.initialdata['habitaciones'].max())
    st.session_state.banosmin      = int(st.session_state.initialdata['banos'].min())
    st.session_state.banosmax      = int(st.session_state.initialdata['banos'].max())
    st.session_state.garajesmin    = int(st.session_state.initialdata['garajes'].min())
    st.session_state.garajesmax    = int(st.session_state.initialdata['garajes'].max())
    st.session_state.filterdata    = 'Sin filtrar'
    
    # Estrato
    for i in range(2,7):
        st.session_state[f'estrato{i}'] = True
            
    # Habitacion
    for i in range(1,5):
        st.session_state[f'habitacion{i}'] = True
            
    if st.session_state.lastpolygonactive is not None:
        st.session_state.zoom_start = 15
        idd  = st.session_state.initialdata['geometry'].apply(lambda x: st.session_state.lastpolygonactive.contains(x))
        if sum(idd)>0:
            st.session_state.data_market = copy.deepcopy(st.session_state.initialdata[idd])
            st.session_state.latitud     = st.session_state.data_market['latitud'].median()
            st.session_state.longitud    = st.session_state.data_market['longitud'].median()
            onchange()
            #truncatedata() 

def onfilter():
    if st.session_state.filterdata=='Menor precio':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=[st.session_state.vardep],ascending=True)
    if st.session_state.filterdata=='Mayor precio':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=[st.session_state.vardep],ascending=False)
    if st.session_state.filterdata=='Menor área':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=['areaconstruida'],ascending=True)
    if st.session_state.filterdata=='Mayor área':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=['areaconstruida'],ascending=False)
    if st.session_state.filterdata=='Menor habitaciones':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=['habitaciones'],ascending=True)
    if st.session_state.filterdata=='Mayor habitaciones':
        st.session_state.data_market = st.session_state.data_market.sort_values(by=['habitaciones'],ascending=False)
            
        
#-----------------------------------------------------------------------------#
# Initial Label
col1, col2 = st.columns([4,2])
with col1: 
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Buscar inmuebles por poligono</h1></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Fltro por caracteristicas</h1></div>', unsafe_allow_html=True)


col1, col2, col3 = st.columns([4,1,1])
#-----------------------------------------------------------------------------#
# Mapa
with col1:

    m = folium.Map(location=[st.session_state.latitud, st.session_state.longitud], zoom_start=st.session_state.zoom_start,tiles="cartodbpositron")
    if st.session_state.data_market.empty is False:
        img_style = '''
                <style>               
                    .property-image{
                      flex: 1;
                    }
                    img{
                        width:200px;
                        height:120px;
                        object-fit: cover;
                        margin-bottom: 2px; 
                    }
                </style>
                '''
        for i, inmueble in st.session_state.data_market.iterrows():
            if isinstance(inmueble['imagen_principal'], str) and len(inmueble['imagen_principal'])>20: imagen_principal =  inmueble['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
            url_export     = f"https://agavirja-proyecto-data-property-home-rtjiaw.streamlit.app/Ficha?idcodigo={inmueble['code']}&tiponegocio={st.session_state.tiponegocio}"
            
            if pd.isnull(inmueble['direccion']): direccionlabel = ''
            else: direccionlabel = f'''<b> Direccion: {inmueble['direccion']}</b><br>'''
            if pd.isnull(inmueble['estrato']): estratolabel = ''
            else: estratolabel = f'''<b> Estrato: {int(inmueble['estrato'])}</b><br>'''
            if pd.isnull(inmueble['garajes']): garajeslabel = ''
            else: garajeslabel = f'''<b> Garajes: {int(inmueble['garajes'])}</b><br>''' 
            if pd.isnull(inmueble['antiguedad']): antiguedadlabel = ''
            else: antiguedadlabel = f'''<b> Antiguedad: {int(inmueble['antiguedad'])}</b><br>''' 
                        
            string_popup = f'''
            <!DOCTYPE html>
            <html>
              <head>
                {img_style}
              </head>
              <body>
                  <div>
                  <a href="{url_export}" target="_blank">
                  <div class="property-image">
                      <img src="{imagen_principal}"  alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                  </div>
                  </a>
                  {direccionlabel}
                  <b> Precio: ${inmueble[st.session_state.vardep]:,.0f}</b><br>
                  {estratolabel}
                  <b> Área: {inmueble['areaconstruida']}</b><br>
                  <b> Habitaciones: {int(inmueble['habitaciones'])}</b><br>
                  <b> Baños: {int(inmueble['banos'])}</b><br>
                  {garajeslabel}
                  {antiguedadlabel}
                  </div>
              </body>
            </html>
            '''
            folium.Marker(location=[inmueble["latitud"], inmueble["longitud"]], popup=string_popup).add_to(m)
    
    draw = Draw(
                draw_options={"polyline": False,"marker": False,"circlemarker":False,"rectangle":False,"circle":False},
                edit_options={"poly": {"allowIntersection": False}}
                )
    draw.add_to(m)
    st_map = st_folium(m,width=1200,height=600)

    polygonType = ''
    if 'all_drawings' in st_map and st_map['all_drawings'] is not None:
        if st_map['all_drawings']!=[]:
            if 'geometry' in st_map['all_drawings'][0] and 'type' in st_map['all_drawings'][0]['geometry']:
                polygonType = st_map['all_drawings'][0]['geometry']['type']
        
    if 'point' in polygonType.lower():
        coordenadas   = st_map['last_circle_polygon']['coordinates']
        st.session_state.polygon = Polygon(coordenadas[0])
        
    if 'polygon' in polygonType.lower():
        coordenadas   = st_map['all_drawings'][0]['geometry']['coordinates']
        st.session_state.polygon = Polygon(coordenadas[0])
        
    if st.session_state.polygon is not None:
        st.session_state.lastpolygonactive = copy.deepcopy(st.session_state.polygon)
        st.session_state.zoom_start        = 15
        idd  = st.session_state.initialdata['geometry'].apply(lambda x: st.session_state.polygon.contains(x))
        if sum(idd)>0:
            st.session_state.data_market = copy.deepcopy(st.session_state.initialdata[idd])
            st.session_state.latitud     = st.session_state.data_market['latitud'].median()
            st.session_state.longitud    = st.session_state.data_market['longitud'].median()
            onchange()
        st.session_state.polygon = None
        st.experimental_rerun()

#-----------------------------------------------------------------------------#
# Filtros

with col2:
    tipoinmueblefilter = st.selectbox('Tipo de inmueble',options=['Apartamento'])
    
with col3:
    tiponegociofilter  = st.selectbox('Tipo de Negocio',key='tiponegocio',options=['Venta','Arriendo'], on_change=tiponegocio_change)
    
# Filtro por Precio
with col2:
    preciomin = st.text_input('Precio mínimo',key='preciomin',on_change=onchange)

with col3:
    preciomax = st.text_input('Precio máximo',key='preciomax',on_change=onchange)

# Filtro por area
with col2:
    areamin = st.number_input('Área construida mínima',step=1,key='areamin',on_change=onchange)
with col3:
    areamax = st.number_input('Área construida máxima',step=1,key='areamax',on_change=onchange)

# Filtro por habitaciones
with col2:
    habitacionmin = st.selectbox('Habitaciones mínimas',options=[1,2,3,4,5,6],key='habitacionmin',on_change=onchange)
with col3:
    habitacionmax = st.selectbox('Habitaciones máximas',options=[1,2,3,4,5,6],key='habitacionmax',on_change=onchange)

# Filtro por banos
with col2:
    banosmin = st.selectbox('Baños mínimos',options=[1,2,3,4,5,6],key='banosmin',on_change=onchange)
with col3:
    banosmax = st.selectbox('Baños máximos',options=[1,2,3,4,5,6],key='banosmax',on_change=onchange)

# Filtro por garajes
with col2:
    garajesmin = st.selectbox('Garajes mínimos',options=[0,1,2,3,4,5],key='garajesmin',on_change=onchange)
with col3:
    garajesmax = st.selectbox('Garajes máximos',options=[0,1,2,3,4,5],key='garajesmax',on_change=onchange)

# Filtro por estrato
with col2:
    estratomin = st.selectbox('Estrato mínimo',options=[1,2,3,4,5,6],key='estratomin',on_change=onchange)
with col3:
    estratomax = st.selectbox('Estrato máximo',options=[1,2,3,4,5,6],key='estratomax',on_change=onchange)
        
        
# Filtro por antiguedad    
#with col2:
#    antiguedamin = st.number_input('Antigueda mínima',step=1,key='antiguedamin',on_change=onchange)
#with col3:
#    antiguedamax = st.number_input('Antigueda máxima',step=1,key='antiguedamax',on_change=onchange)


#-------------------------------------------------------------------------#
# Inmuebles
if st.session_state.data_market.empty is False:
    st.write('---') 
    st.markdown('<div style="background-color: #f2f2f2; border: 1px solid #fff; padding: 0px; margin-bottom: 10px;"><h1 style="margin: 0; font-size: 18px; text-align: center; color: #3A5AFF;">Listado de inmuebles</h1></div>', unsafe_allow_html=True)
    col1,col2 = st.columns([1,3])
    with col1:
        filtro = st.selectbox('Filtro por:', options=['Sin filtrar','Menor precio','Mayor precio','Menor área','Mayor área','Menor habitaciones','Mayor habitaciones'],key='filterdata',on_change=onfilter)

    css_format = """
        <style>
          .property-card-left {
            width: 100%;
             /* height: 1600px; */
             /* overflow-y: scroll; */
            text-align: center;
            display: inline-block;
            margin: 0px auto;
          }
    
          .property-block {
            width:32%;
            background-color: white;
            border: 1px solid gray;
            box-shadow: 2px 2px 2px gray;
            padding: 3px;
            margin-bottom: 10px; 
      	    display: inline-block;
      	    float: left;
            margin-right: 10px; 
          }
    
          .property {
            border: 1px solid gray;
            box-shadow: 2px 2px 2px gray;
            padding: 10px;
            margin-bottom: 10px;
          }
          
          .property-image{
            flex: 1;
          }
          .property-info{
            flex: 1;
          }
          
          .price-info {
            font-family: 'Comic Sans MS', cursive;
            font-size: 24px;
            margin-bottom: 1px;
          }
     
          .admon-info {
            font-family: 'Comic Sans MS', cursive;
            font-size: 12px;
            margin-bottom: 5px;
          }
          
          .caracteristicas-info {
            font-size: 16px;
            margin-bottom: 2px;
          }
    
          img{
            max-width: 100%;
            width: 100%;
            height:250px;
            object-fit: cover;
            margin-bottom: 10px; 
          }
        </style>
    """
    
    imagenes = ''
    for i, inmueble in st.session_state.data_market.iterrows():
    
        if isinstance(inmueble['imagen_principal'], str) and len(inmueble['imagen_principal'])>20: imagen_principal =  inmueble['imagen_principal']
        else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
        caracteristicas = f'<strong>{inmueble["areaconstruida"]}</strong> mt<sup>2</sup> | <strong>{int(inmueble["habitaciones"])}</strong> hab | <strong>{int(inmueble["banos"])}</strong> baños | <strong>{int(inmueble["garajes"])}</strong> pq'
        url_export      = f"https://agavirja-proyecto-data-property-home-rtjiaw.streamlit.app/Ficha?idcodigo={inmueble['code']}&tiponegocio={st.session_state.tiponegocio}"
        
        if pd.isnull(inmueble['direccion']): direccionlabel = '<p class="caracteristicas-info">&nbsp</p>'
        else: direccionlabel = f'''<p class="caracteristicas-info">Dirección: {inmueble['direccion'][0:35]}</p>'''
        
        imagenes += f'''
              <div class="property-block">
                <a href="{url_export}" target="_blank">
                <div class="property-image">
                  <img src="{imagen_principal}" alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                </div>
                </a>
                <p class="price-info">${inmueble[st.session_state.vardep]:,.0f}</h3>
                {direccionlabel}
                <p class="caracteristicas-info">{caracteristicas}</p>
              </div>
              '''
    texto = f"""
        <!DOCTYPE html>
        <html>
          <head>
          {css_format}
          </head>
          <body>
        <div class="property-card-left">
        {imagenes}
        </div>
          </body>
        </html>
        """
    texto = BeautifulSoup(texto, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)