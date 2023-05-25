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

#===========================================================================
#DEFININDO O ENQUANDRO DA PAGINA 
#===========================================================================
st.set_page_config( 
   page_title="🏙️Cidades",
   layout="wide",
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
#==============================================================

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
    #### Verificar se há nulos
    #### Identificar valores nulos em todas as colunas
    #valores_vazios = df.isnull()
    #### Contar valores vazios em cada coluna
    #contagem_vazios = valores_vazios.sum()
    ##### Imprimir contagem de valores vazios em cada coluna
    #print(contagem_vazios) 

    #Código para aparecer todas as colunas quando usar o ".head()"
    #pd.set_option('display.max_columns', None)  # exibir todas as colunas
    #pd.set_option('display.width', None)  # exibir todas as colunas sem quebrar linhas

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

def mean_more_4(df):
            cols = ['city', 'aggregate_rating'] 
            linhas_selecionadas = df['aggregate_rating'] > 4
            df_aux = df.loc[linhas_selecionadas, cols].groupby('city').count().sort_values('aggregate_rating', ascending=False).reset_index() 
            
            df_aux = df_aux.head(7)
            
            #Plotando o Gráfico: 
            fig = px.bar(df_aux, x='city', y='aggregate_rating', 
                            title='7 cidades com média de avaliações acima de 4',
                            labels={'city': 'Cidades', 'aggregate_rating': 'Avaliações'},
                            text='aggregate_rating')
            return fig
#==============================================================

def city_more_restaurant(df):
    df_aux = df.loc[:, ['city', 'restaurant_id']].groupby('city').count().sort_values('restaurant_id', ascending=False).reset_index()
    # Seleciona no máximo as 3 cidades com o maior número de restaurantes
    df_aux = df_aux.nlargest(10, 'restaurant_id')
    
    fig = px.bar(df_aux, x='city', y='restaurant_id',   
                        title='Top 10 cidades com mais restaurantes na Base de Dados',
                        text='restaurant_id',
                        labels={'city':'Cidades', 'restaurant_id':'Restaurantes'})
    return fig
#==============================================================

def menor_que_2(df):
            cols = ['city', 'aggregate_rating'] 
            linhas_selecionadas = df['aggregate_rating'] < 2.5
            df_aux = df.loc[linhas_selecionadas, cols].groupby('city').count().sort_values('aggregate_rating', ascending=False).reset_index() 
            
            df_aux = df_aux.head(6)
            
            #Plotando o Gráfico: 
            fig = px.bar(df_aux, x='city', y='aggregate_rating', 
                            title='Cidades que possuem mais restaurantes com nota média abaixo de 2.5',
                            labels={'city': 'Cidades', 'aggregate_rating': 'Avaliações'},
                            text='aggregate_rating')
            return fig 

def culinaria_distintas(df):
    df_aux = df.loc[:, ['city', 'cuisines', 'country_name']].groupby(['city', 'country_name']).nunique().sort_values('cuisines', ascending=False).reset_index()
    
    df_aux = df_aux.head(10)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    #Plotando o Gráfico: 
    fig = px.bar(df_aux, x='city', y='cuisines', 
                    title='Top 10 cidades com mais restaurantes com culinárias distintas',
                    labels={'city': 'Cidades', 'cuisines': 'Culinária', 'country_name':'Países'},
                    text='cuisines',
                    color='country_name',# Coluna utilizada para definir a cor
                    color_discrete_sequence=colors)  # Sequência de cores a ser utilizada
    return fig
    

#===========================================================================
#IMPORTANDO O DATAFRAME
#===========================================================================
df_row = pd.read_csv('dataset/zomato.csv') 
df = df_row.copy()

#===========================================================================
#LIMPANDO OS DADOS
#===========================================================================
df = clean_code (df)

#=====================================================================================
#LAYOUT
#===================================================================================== 
#textos
st.title( "🏙️Análise das Cidades" ) 

#imagem
image = Image.open( 'imagem2.png' )
st.sidebar.image( image, width=40 ) 

st.sidebar.markdown('### Fome Zero!')
st.sidebar.markdown('---')

#=====================================================================================
# FILTRO DOS DADOS
#===================================================================================== 
st.sidebar.markdown("### Fome Zero")
# st.sidebar.markdown( '#### Escolha os países que deseja visualizar os  restaurantes:' )
##---------------------------------
traffic_options = st.sidebar.multiselect('#### Escolha os países que deseja visualizar os  restaurantes:',
['Philippines', 'Brazil', 'Australia', 'United States of America',
'Canada', 'Singapure', 'United Arab Emirates', 'India',
'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
'Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa',] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by William Moura')


#=====================================================================================
#PERGUNTAS SOBRE CIDADES
#===================================================================================== 
with st.container():
    fig = city_more_restaurant(df)
    st.plotly_chart(fig, use_container_width=False)

#=====================================================================================
#=====================================================================================

with st.container():
    col1, col2= st.columns( 2, gap='large')
    
    with col1:
        fig = mean_more_4(df)
        st.plotly_chart(fig, use_container_width=True)
#=====================================================================================

    with col2:

        fig = menor_que_2(df)
        st.plotly_chart(fig, use_container_width=True)
#=====================================================================================

with st.container():

    fig = culinaria_distintas(df)
    st.plotly_chart(fig, use_container_width=False)
#=====================================================================================
#=====================================================================================
#Fim
