#===========================================================================
#BIBLIOTECAS 
#===========================================================================
import pandas as pd 
import re 
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np
from folium.plugins import MarkerCluster
#===========================================================================


#===========================================================================
#DEFININDO O ENQUANDRO DA PAGINA 
#===========================================================================
st.set_page_config( 
   page_title="Home",
   page_icon="📊",
   layout="wide"
)

#===========================================================================
#FUNÇÕES: 
#===========================================================================
#Criando a coluna com nomes nomes de países:
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]
#==============================================================

#Criando uma coluna com os tipos de acordo com a coluna price_range
def create_price_tye(price_range): 
   if price_range == 1:
       return "cheap"
   elif price_range == 2:
       return "normal"
   elif price_range == 3:
       return "expensive"
   else:
       return "gourmet"
#==============================================================

CURRENCY = {
    'Botswana Pula(P)': 0.076,
    'Brazilian Real(R$)': 0.19,
    'Dollar($)': 1,
    'Emirati Diram(AED)': 0.27,
    'Indian Rupees(Rs.)': 0.012,
    'Indonesian Rupiah(IDR)': 0.000065,
    'NewZealand($)': 0.61,
    'Pounds(£)': 1.20,
    'Qatari Rial(QR)': 0.27,
    'Rand(R)': 0.055,
    'Sri Lankan Rupee(LKR)': 0.0031,
    'Turkish Lira(TL)': 0.059 
}

def convert_dollar(cc):
    return CURRENCY[cc]
#==============================================================

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code] 
#___________________________________________________________________________
#funções dos codigos
#___________________________________________________________________________

def clean_code (df):
    #alterando nome das colunas:
    df = df.rename(columns={'Restaurant ID': 'restaurant_id' , 'Restaurant Name':'restaurant_name', 'Country Code':'country_code', 'City': 'city', 'Address': 'address',
        'Locality':'locality', 'Locality Verbose':'locality_verbose' , 'Longitude':'longitude', 'Latitude':'latitude', 'Cuisines': 'cuisines',
        'Average Cost for two':'cost_for_two', 'Currency':'currency', 'Has Table booking':'has_table_booking',
        'Has Online delivery':'has_online_delivery', 'Is delivering now':'is_delivering_now', 'Switch to order menu':'switch_to_order_menu',
        'Price range':'price_range', 'Aggregate rating':'aggregate_rating', 'Rating color':'rating_color', 'Rating text':'rating_text',
        'Votes':'votes'})


    # 0. tirando os valores vazios (NaN) das colunas selecionadas("~" inverte o isnull e pega so as que nao sao nulas):
    linhas_sem_nulos = ~df['cuisines'].isnull()
    df = df.loc[linhas_sem_nulos, :].copy() 
   

    #Apagando uma linha onde o preço do restaurante está errado:
    df = df.drop(df[df.cost_for_two == 25000017.0].index)

    #Limpar a coluna de "Tipo de Culinária"
    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    #Criar a coluna "country_name", nome dos países.
    df['country_name'] = df['country_code'].apply(lambda x: country_name(x))

    df['cost_for_two'] = df['cost_for_two']*df['currency'].apply(lambda x: convert_dollar(x))

    df['name_color'] = df['rating_color'].apply(lambda x: color_name(x))

    pd.set_option('display.max_columns', None) 

    return df

#Mapa

def create_map(df):
    map_ = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=3, tiles='OpenStreetMap')

    marker_cluster = MarkerCluster().add_to(map_)

    for lat, lon, name, cuisine in zip(df['latitude'], df['longitude'], df['restaurant_name'], df['cuisines']):
        folium.Marker(
            location=[lat, lon],
            popup=f"{name}\n{cuisine}",
            icon=folium.Icon(icon='pushpin')
        ).add_to(marker_cluster)

    return map_

#===========================================================================
#IMPORTANDO O DATAFRAME E LIMPANDO OS DADOS
#===========================================================================
df_row = pd.read_csv('dataset/zomato.csv') 
df = df_row.copy()

df = clean_code (df)



#=====================================================================================
#BARRA LATERAL E FILTROS
#===================================================================================== 

#textos
st.title( "📌Fome Zero!" ) 
st.markdown("# O Melhor lugar para encontrar seu restaurante favorito!")
st.markdown("##### O ícone (>) no canto superior, abre a barra lateral com as outras páginas")
st.markdown("""---""")
st.markdown("### Temos as seguintes marcas dentro da nossa plataforma:")


#imagem
image = Image.open( 'imagem2.png' )
st.sidebar.image( image, width=40 ) 

st.sidebar.markdown('### Fome Zero!')



traffic_options = st.sidebar.multiselect('#### Fltros dos Países:',
['Philippines', 'Brazil', 'Australia', 'United States of America',
'Canada', 'Singapure', 'United Arab Emirates', 'India',
'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
'Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'England', 'South Africa',] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by William Moura')



# #===========================================================================
# # PERGUNTAS DO PROJETO GERAL
# #===========================================================================
with st.container():
    col1, col2, col3, col4, col5 = st.columns( 5, gap='large')

#### 1. Restaurantes Cadastrados
    with col1:
        rest_cadast = ( df['restaurant_id'].nunique() ) 
        col1.metric("Restaurantes Cadastrados", f'{rest_cadast:,.0f}')

#### 2. Países Cadastrados
    with col2:
        paises_cadast = df['country_code'].nunique()
        col2.metric("Países Cadastrados", paises_cadast)

#### 3. Cidades Cadastradas
    with col3:
        cidad_cadast = df['city'].nunique()
        col3.metric("Cidades Cadastradas", f'{cidad_cadast:,.0f}')


#### 4. Avaliações feitas na plataforma
    with col4:
        aval_da_plat = df['votes'].sum()
        col4.metric("Avaliações feitas na plataforma",  f'{aval_da_plat:,.0f}')

#### 5. Tipos de culinárias oferecidas
    with col5:
        tipos_culinaria = ( df['cuisines'].nunique()) 
        col5.metric("Tipos de Culinária", tipos_culinaria)



# #===========================================================================
# MAPA
with st.container():
    
    with st.spinner("Carregando o mapa, aguarde para não ficar perdido..."):
        map_ = create_map(df)
        folium_static(map_, width=1024, height=600 )
    