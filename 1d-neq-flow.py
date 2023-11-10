import streamlit as st
import cantera as ct
import numpy as np
import plotly.express as px   
import pandas as pd

import STube
import Reactor



st.set_page_config(
    page_title="1D non-equlibrium nozzle flow - Calc",
    layout="wide",
    )

with st.sidebar:
    st.write("# Parâmetros de Entrada")

    st.write("## Tubo de Choque")
    X1  = st.text_input(label='Composição Inicial do Driven', value='O2: 0.21, N2: 0.79')
    st.write("*obs: a composição inicial deverá conter N2 e O2, somente*")
    p1 =  st.number_input(label="Pressão inicial do Driven (kPa):"       , value=11.0   , min_value=1.0, step=0.1)*1e3
    T1 =  st.number_input(label="Temperatura inicial do Driven (K):"     , value=298.   , min_value=298., step=1.)
    us =  st.number_input(label="Vel. da Onda de Choque Incidente (m/s):", value=2100.0 , min_value=350., step=0.1)
    p8 =  st.number_input(label="Pressão de Estagnação Medida (MPa):"    , value=8.8    , min_value=1.0, step=0.1)*1e6

    bool_ST= False
    try:
        st.write(":green[**!STube Rodou Corretamente!**]")
        gas8 = STube.STube_Calc(T1, p1, us, p8, X1)
        bool_ST= True
        st.write(":green[**!STube Rodou Corretamente!**]")
        T5 = gas8.T; p5 = gas8.P; h5 = gas8.h; X = gas8.X 
        st.write(":green[**!STube Rodou Corretamente!**]")
        
    except:
        st.write(":red[**!Erro em STube Calc!**]")
        bool_ST= False


    st.write("## Tubeira")
    ang =  st.number_input(label="Ângulo de divergência (graus):"  , value=15.0,   min_value=1.0, step=0.10 )
    r_0 =  st.number_input(label="Raio à Garganta (mm):"           , value=6.40,   min_value=0.0, step=0.10 )*1e-3
    r_f =  st.number_input(label="Raio à Saída (mm):"              , value=150.,   min_value=0.0, step=0.10 )*1e-3

    if bool_ST == True:
        try: 
            Reator = Reactor.PFR_Solver(r_0=r_0, r_f=r_f, ang=ang, gas=gas8, T5=T5, p5=p5, X=X )
            st.write(":green[**!NEq-Nozzle Rodou Corretamente!**]")
        except:
            st.write(":red[**!Erro em NEq-Nozzle!**]")


st.write("### Tubo de Choque ")

col1, col2 = st.columns(2)

with col1:
    st.write("###### Condições Iniciais:")
    st.info(f"""Pressão, p1 :         {p1/1e3 : 4.4} kPa   \\
            Temperatura, T1 :         {T1 : .0f} K         \\
            Vel. Onda Incidente, us : {us : 5.5} m/s       \\
            Composição Inicial : {X1} 
            """)
    
    st.write("###### Condições de Estagnação:")

    st.info(f"""Pressão, p5 :     {p5/1e6 : 4.4} MPa       \\
        Temperatura, T5 :         {T5 : .0f} K             \\
        Entalpia Específica, h5 : {h5/1e6 : 4.2f} MJ/kg 
        """)


with col2:
    k = np.argsort(gas8.X)[::-1]
    Xi = np.array(gas8.species_names)

    fig = px.bar( title='Concentrações de Espécies - Estagnação', x=Xi[k], y=100*gas8.X[k],height=350,width=600,labels=dict(x='Espécies', y='Fração Molar (%)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_xaxes(title_font_family="Arial")
    st.plotly_chart(fig)

#st.write(gas8.species_names[k])

st.write("### Geometria da Tubeira")

col1, col2 = st.columns(2)
with col1:
    fig = px.area(x=Reator.x, y= Reator.R(Reator.x), labels=dict(x='Posição Axial (cm)', y='Raio (cm)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_xaxes(title_font_family="Arial")
    st.plotly_chart(fig)

with col2:
    fig = px.area(x=Reator.x, y= Reator.A(Reator.x),labels=dict(x='Posição Axial (cm)', y='Area (cm^2)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
    fig.update_xaxes(title_font_family="Arial")
    st.plotly_chart(fig)
    
st.write("### Saída da Tubeira")
col1, col2 = st.columns(2)
with col1:
    fig = px.area(title='Velocidade',x=Reator.states.x, y= Reator.states.Vel.astype('int'),labels=dict(x='Posição Axial (cm)', y='Velocidade (m/s)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_xaxes(title_font_family="Arial")
    fig.update_traces(line={'width': 5},line_color='#147852',hoverlabel=dict(font_size=18))
    st.plotly_chart(fig)

    fig = px.area(title='Mach',x=Reator.states.x, y= np.round(Reator.states.Mach,2),labels=dict(x='Posição Axial (cm)', y='Número de Mach'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_xaxes(title_font_family="Arial")
    fig.update_traces(line={'width': 5},line_color='#018989',hoverlabel=dict(font_size=18))
    st.plotly_chart(fig)


with col2:
    fig = px.area(title='Temperatura',x=Reator.states.x, y= Reator.states.T.astype('int'),labels=dict(x='Posição Axial (cm)', y='Temperatura (K)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_xaxes(title_font_family="Arial")
    fig.update_traces(line={'width': 5},line_color='#910902',hoverlabel=dict(font_size=18))
    st.plotly_chart(fig)
    
    fig = px.area(title='Pressão',x=Reator.states.x, y= Reator.states.P.astype('int'),labels=dict(x='Posição Axial (cm)', y='Pressão (Pa)'))
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17), type="log") )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
    fig.update_xaxes(title_font_family="Arial")
    fig.update_traces(line={'width': 5},line_color='#186211',hoverlabel=dict(font_size=18))
    st.plotly_chart(fig)

df_X = 100*pd.DataFrame(Reator.states.X)
df_X.columns = Reator.states.species_names
df_X.set_index = Reator.states.x

fig = px.line(df_X, title='Concentração de Espécies Químicas', labels={'index':'Posição Axial (cm)', 'value':'Fração Molar'} )
fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20), type="log" ),yaxis_range=[-2,2] )
fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20) ) )
fig.update_xaxes(title_font_family="Arial")
fig.update_traces(line={'width': 10},hoverlabel=dict(font_size=20))
st.plotly_chart(fig)