import streamlit as st
from PIL import Image
from pathlib import Path

st.set_page_config(
    page_title='Home',
    page_icon="AAA"
)

BASE_DIR = Path(__file__).resolve().parent
image = Image.open(BASE_DIR / "Delivery.jpg")
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Cury Company Greowth Dashboard')

st.markdown(
    'Growth Dasgboard foi construído para acampanhar as métricas de crescimento dos Entregadores e Restaurantes.\n'
    '### Como utilizar esse Growth Dashboard?\n'
    '- Visão Empresa:\n'
    '    - Visão Gerente: Métricas gerais de comportamento.\n'
    '    - Visão Tática: Omdocadores semanais de crescimento.\n'
    '    - Visão Geográfica: Insights de geolocalização.\n'
    '- Visão Empregador:\n'
    '    - Acompanhamento dos Indicadores de crescimento dos restaurantes.\n'
    '- Visão Restautantes:\n'
    '    - Indicadores semanais de crescimento dos restaurantes\n'
    '### Ask for Help\n'
    '- Times de Data Science no Discord\n'
    '    - @meigarom'
    
)
