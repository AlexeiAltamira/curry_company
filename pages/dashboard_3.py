#Import libraries
from haversine import haversine
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
from pathlib import Path

import pandas as pd
from datetime import datetime
import numpy as np

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#Import Dataset
BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "dataset" / "train.csv")

#====
#Tratemanto dos dados
#===

#=====
#Barra lateral
#=====

st.header('Marketplace - Visão Restaurante')

image = Image.open(BASE_DIR / "Delivery.jpg")
st.sidebar.image(image, width=120)

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'New 1', 'New 2'])

with tab1:
    with st.container():
        st.title('One')
        col1, col2, col3, col4, col5, col6 = st.columns(6) 
        with col1:
            #st.markdown('###### Número de entregadores')
            entregador_unico = df["Delivery_person_ID"].nunique()
            col1.metric('Nº entregadores', entregador_unico)
            
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distancia'] = df.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distancia = df['distancia'].mean()
            col2.metric('A distancia média das entregas:', avg_distancia)

        with col3:
            df['Time_taken(min)'] = df['Time_taken(min)'].str.extract('(\d+)')
            df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
            festival = df[df['Festival'] =='Yes ']
            festival_mean = festival['Time_taken(min)'].mean()
            col3.metric('A tempo médio durantes Festivais:', festival_mean, 'minutos.')

        with col4:
            festival_std = festival['Time_taken(min)'].std()
            col4.metric('A desvio padrão durantes Festivais:', festival_std, 'minutos.')

        with col5:
            festival = df[df['Festival'] =='No ']
            not_festival_mean = festival['Time_taken(min)'].mean()
            col5.metric('A tempo médio fora Festivais:', not_festival_mean, 'minutos.')

        with col6:
            not_festival_std = festival['Time_taken(min)'].std()
            col6.metric('A desvio padrão durantes Festivais:', not_festival_std, 'minutos.')


    st.sidebar.markdown("""---""")

    with st.container():
        st.title('Tempo médio entregas por cidade')
        col1, col2 = st.columns(2) 
        with col1:
            df_aux = df.groupby('City').agg({'Time_taken(min)':['mean', 'std']}).reset_index()
            df_aux.columns = ['City', 'avg_time', 'std_time']
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control',
                                    x = df_aux['City'],
                                    y = df_aux['avg_time'],
                                    error_y=dict(type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

        with col2:
            st.dataframe(df.groupby(['City', 'Type_of_order']).agg(Media_Entregas=('Time_taken(min)', 'mean'), Desvio_Padrao=('Time_taken(min)', 'std')).reset_index())



    with st.container():
        st.title('Tempo médio entregas por cidade')
        col1, col2 = st.columns(2) 
        with col1:
            avg_distancia_city = df.loc[:, ['City', 'distancia']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distancia_city['City'], values=avg_distancia_city['distancia'], pull=[0.1, 0.1, 0.1, 0.1])])
            st.plotly_chart(fig)

        with col2:
            df_aux = df.groupby(['City', 'Road_traffic_density']).agg(Media_Entregas=('Time_taken(min)', 'mean'),
            Desvio_Padrao=('Time_taken(min)', 'std')
            ).reset_index()
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Media_Entregas', 
                              color='Desvio_Padrao', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['Desvio_Padrao']))
            st.plotly_chart(fig)