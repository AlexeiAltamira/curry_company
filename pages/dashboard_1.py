#Import libraries
from haversine import haversine
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from pathlib import Path

import pandas as pd
from datetime import datetime

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#Import Dataset
BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "dataset" / "train.csv")

#docs.streamlit.io
#https://docs.streamlit.io/develop/api-reference/text/st.header


#=====
#Barra lateral
#=====

st.header('Marketplace - Visão cliente')

image = Image.open(BASE_DIR / "Delivery.jpg")
st.sidebar.image(image, width=120)

#st.sidebar.markdown('# Cury Company') #Níveis do título
#st.sidebar.markdown('## Cury Company')
#st.sidebar.markdown('### Cury Company')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Data limite')
date_slider = st.sidebar.slider('Até qual valor?', value=datetime(2022, 4, 13),
                                min_value=datetime(2022, 2, 11),
                                max_value=datetime(2022, 4, 6),
                                format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições de transito:', ['High ', 'Jam ', 'Low ', 'Medium '],
                                          default=['High ', 'Jam ', 'Low ', 'Medium '])

st.sidebar.markdown("""---""")

#Filtro de datas
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtros de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#=====
#Layout no Streamlit
#=====

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
 #Visão empresa
 # Quantidade de pedidos por dia
  with st.container():
    st.markdown('Orders by Day')
    cols = ['ID', 'Order_Date']

    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
  # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    st.plotly_chart(fig, use_container_width=True)
 
  with st.container():
    col1, col2 = st.columns(2)
  
    with col1:
      st.markdown('Traffic Order Share')
      columns = ['ID', 'Road_traffic_density']
      df_aux = df.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
      df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
# gráfico
      fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
      st.plotly_chart(fig, use_container_width=True)

    with col2:
      st.markdown('Traffic Order City')
      columns = ['ID', 'City', 'Road_traffic_density']
      df_aux = df.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
      df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
# gráfico
      fig = px.bar( df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
      st.plotly_chart(fig, use_container_width=True)

with tab2:
  with st.container():
    st.markdown('Order by Week')

  # Quantidade de pedidos por Semana
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    df2 = df.copy()
    df2['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    df_aux = df2.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
  # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    st.plotly_chart(fig, use_container_width=True)

  with st.container():
    st.markdown('Order Share by Week')
  # Quantidade de pedidos por entregador por Semana
  # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df2.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df2.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
 # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
  st.markdown('Country Maps')
#Visão Geográfica
  columns = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
  columns_groupby = ['City', 'Road_traffic_density']
  data_plot = df2.loc[:, columns].groupby( columns_groupby ).median().reset_index()
  data_plot = data_plot[data_plot['City'] != 'NaN']
  data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']

 # Desenhar o mapa
  map_ = folium.Map( zoom_start=11 )
  for index, location_info in data_plot.iterrows():
    folium.Marker( [location_info['Delivery_location_latitude'],
    location_info['Delivery_location_longitude']],
    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
  folium_static(map_, width=1024, height=600)
