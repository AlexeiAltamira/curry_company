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
import numpy as np

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#Import Dataset
BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "dataset" / "train.csv")

#====
#Tratemanto dos dados
#===
df_idade = df.copy()
df_idade['Delivery_person_Age'] = df['Delivery_person_Age'].replace('NaN ', np.nan)
df_idade.dropna(subset=['Delivery_person_Age'], inplace=True)
df_idade['Delivery_person_Age'] = df_idade['Delivery_person_Age'].astype(int)

#=====
#Barra lateral
#=====

st.header('Marketplace - Visão cliente')

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
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            maior_idade = df_idade["Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            menor_idade = df_idade["Delivery_person_Age"].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            melhor_veic = df["Vehicle_condition"].max()
            col3.metric('Melhor veiculo', melhor_veic)

        with col4:
            pior_veic = df["Vehicle_condition"].min()
            col4.metric('Pior veiculo', pior_veic)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliaçã media por Entregador')
            df_aux = df.copy() #Uso DF original. Sem deleções feitas anteriores.
            df_aux['Delivery_person_Ratings'] = df_aux['Delivery_person_Ratings'].replace('NaN ', np.nan)
            df_aux.dropna(subset=['Delivery_person_Ratings'], inplace=True)
            df_aux['Delivery_person_Ratings'] = df_aux['Delivery_person_Ratings'].astype(float)
            media_entregadores = df_aux.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean()
            st.dataframe(media_entregadores)

        with col2:
            st.subheader('Avaliação media por Transito')
            media_por_trans = df_aux.groupby('Road_traffic_density')['Delivery_person_Ratings'].mean()
            st.dataframe(media_por_trans)

            st.subheader('Avaliação media por Clima')
            media_por_clima = df_aux.groupby('Weatherconditions')['Delivery_person_Ratings'].mean()
            st.dataframe(media_por_clima)


    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top Entregadores mais rápidos por cidade')
            df['Time_taken(min)'] = df['Time_taken(min)'].str.extract('(\d+)')
            df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
            # 1. Ordena todo o DataFrame do menor tempo para o maior
            df_ordenado = df.sort_values(by='Time_taken(min)', ascending=True)

            # 2. Agrupa por cidade e pega as primeiras 10 linhas de cada uma (que serão as mais rápidas)
            tabela_top10 = df_ordenado.groupby('City').head(10)

            # 3. Filtra a tabela final para mostrar apenas as colunas que você quer ver
            colunas_desejadas = ['City', 'Delivery_person_ID', 'Time_taken(min)']
            tabela_top10 = tabela_top10[colunas_desejadas]

            # 4. Reseta o índice para a tabela ficar limpa
            tabela_top10 = tabela_top10.reset_index(drop=True)

            st.dataframe(tabela_top10.sort_values('City'))

        with col2:
            st.subheader('Top Entregadores mais lentos por cidade')
            # 1. Ordena todo o DataFrame do menor tempo para o maior
            df_ordenado_lento = df.sort_values(by='Time_taken(min)', ascending=False)

            # 2. Agrupa por cidade e pega as primeiras 10 linhas de cada uma (que serão as mais rápidas)
            tabela_top10_lento = df_ordenado_lento.groupby('City').head(10)

            # 3. Filtra a tabela final para mostrar apenas as colunas que você quer ver
            colunas_desejadas_lento = ['City', 'Delivery_person_ID', 'Time_taken(min)']
            tabela_top10_lento = tabela_top10_lento[colunas_desejadas]

            # 4. Reseta o índice para a tabela ficar limpa
            tabela_top10_lento = tabela_top10_lento.reset_index(drop=True)

            st.dataframe(tabela_top10_lento.sort_values('City'))