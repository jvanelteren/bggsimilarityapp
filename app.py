import streamlit as st
import pandas as pd
pd.options.display.max_rows = 20
pd.options.display.float_format = "{:,.1f}".format
pd.options.mode.chained_assignment = None
import os
from dotproductbias import DotProductBias
import model
from st_aggrid.shared import GridUpdateMode  

from st_aggrid import AgGrid

def update():
     # refreshes table when filters are changed
     st.session_state['selected_game'] = st.session_state['selected_game']

def modelupdate():
     # refreshes table when filters are changed
     if st.session_state['model'] == 'standard':
          model.m = model.modelstandard
     elif st.session_state['model'] == 'experimental':
          model.m = model.modeltransform
          bla.expanded = False
     update()
# Initialisation of session state
def reset(clear_cache=False):
     if clear_cache:
          for key in st.session_state.keys():
               del st.session_state[key]
               
     hide_streamlit_style = """
          <style>
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}
          </style>
          """
     st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
     
               
     st.session_state.setdefault('selected_game', 'Chess')
     st.session_state.setdefault('minvotes', 1000)
     st.session_state.setdefault('minaverage', 0)
     st.session_state.setdefault('weight', [0.,5.])
     st.session_state.setdefault('amountresults', 20)
     st.session_state.setdefault('model', 'standard')
     modelupdate()
reset()


def filter(df):
     filtered_df = df.loc[(df['usersrated'] >= st.session_state['minvotes']) &
                          (df['average'] >= st.session_state['minaverage']) &
                          (df['averageweight'] >= st.session_state['weight'][0]) &
                          (df['averageweight'] <= st.session_state['weight'][1])
                          
                          ][:st.session_state['amountresults']]

     
     # filtered_df.set_index('thumbnail', inplace=True)
     # filtered_df.index.name = None
     
     # filtered_df =  filtered_df.sort_values('similarity', ascending=False)
     return filtered_df

# Sidebar filters
st.sidebar.header('Options to filter and sort')
mobile = st.sidebar.radio("Select the version of the app",['mobile', 'desktop'],)
st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.sidebar.slider("Minimal amount of votes",0,5000, key='minvotes', step=100, on_change=update)
st.sidebar.slider("Minimum average score",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f")
st.sidebar.slider("Weight",0.,5., value=[0.,5.], key='weight', step = 0.1, on_change=update, format="%.1f")
st.sidebar.radio("Amount of results",[20, 50,200], key='amountresults', on_change=update)
st.sidebar.radio("Model",['standard', 'experimental'], key='model', on_change=modelupdate)

st.write('<style>div.row-widget.stExpander > div{align:right;}</style>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>BoardGame Explorer</h1>", unsafe_allow_html=True)
# st.title('BoardGame Explorer')

placeholder = st.empty()

df = filter(model.most_similar_games(st.session_state['selected_game']))
# import seaborn as sns
# cm = sns.light_palette("green", as_cmap=True)
# st.dataframe(df.style.background_gradient(cmap=cm))

if st.sidebar.button('Reset selections'):
     reset(clear_cache=True)
     st.experimental_rerun()
 
from st_aggrid import JsCode, GridOptionsBuilder


link_jscode = JsCode("""
  function(params) {
  	var element = document.createElement("span");
  	var linkElement = document.createElement("a");
  	var linkText = document.createTextNode(params.data.name);
  	link_url = params.value;
  	linkElement.appendChild(linkText);
  	linkText.title = params.value;
  	linkElement.href = link_url;
  	linkElement.target = "_blank";
  	element.appendChild(linkElement);
  	return element;
  };
  """)

if mobile == 'mobile':
     image_nation = JsCode("""function (params) {
          var element = document.createElement("span");
          var imageElement = document.createElement("img");
     
          if (params.data.thumbnail) {
               imageElement.src = params.data.thumbnail;
               imageElement.width="80";
          } else {
               imageElement.src = "";
          }
          element.appendChild(imageElement);
          element.appendChild(document.createTextNode(params.value));
          return element;
          }""")
     gb = GridOptionsBuilder.from_dataframe(df[['url', 'average', 'thumbnail', 'name']])

     df[' ']= ' '
     # gb.configure_pagination(paginationAutoPageSize=True )
     gb.configure_grid_options(rowHeight=100, pagination=True)

     gb.configure_column(' ', minWidth=100, cellRenderer=image_nation, initialPinned='left')
     gb.configure_column("url", headerName='Name', cellRenderer=link_jscode)

     gb.configure_column('average', headerName='Avg', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})")
     gb.configure_column('thumbnail', hide=True,suppressToolPanel=True)
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     
     gridOptions = gb.build()
          
          
     # AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True
          #   )
     grid_height= 100*st.session_state['amountresults']+80
     grid_response = AgGrid(
     df[[' ', 'url', 'average','thumbnail', 'name']],
     gridOptions=gridOptions,
     height=grid_height,
     fit_columns_on_grid_load=True,
     allow_unsafe_jscode=True,
     update_mode=GridUpdateMode.SELECTION_CHANGED,
     )
else:
     image_nation = JsCode("""function (params) {
          var element = document.createElement("span");
          var imageElement = document.createElement("img");
     
          if (params.data.thumbnail) {
               imageElement.src = params.data.thumbnail;
               imageElement.width="120";
          } else {
               imageElement.src = "";
          }
          element.appendChild(imageElement);
          element.appendChild(document.createTextNode(params.value));
          return element;
          }""")
     gb = GridOptionsBuilder.from_dataframe(df)
     
     df[' ']= ' '
     # gb.configure_pagination(paginationAutoPageSize=True )
     gb.configure_grid_options(rowHeight=100, pagination=True)
     gb.configure_column(' ', minWidth=130, cellRenderer=image_nation, initialPinned='left')
     gb.configure_column("url", minWidth=120, headerName='Name', cellRenderer=link_jscode)
     gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
     gb.configure_column('similarity', headerName='Similarity', valueFormatter="data.similarity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
     gb.configure_column('average', headerName='Average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
     gb.configure_column('bayesaverage', headerName='GeekRating', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     gb.configure_column('averageweight', headerName='Weight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_column('thumbnail', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     
     gridOptions = gb.build()
     # AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True
          #   )
     grid_height= 100*st.session_state['amountresults']+80

     grid_response = AgGrid(
     df,
     gridOptions=gridOptions,
     update_mode=GridUpdateMode.SELECTION_CHANGED,
     
     height=grid_height,
     fit_columns_on_grid_load=True,
     allow_unsafe_jscode=True,
     )

if grid_response['selected_rows']:
     if grid_response['selected_rows'][0]['name'] != st.session_state['selected_game']:
          st.session_state['selected_game'] = grid_response['selected_rows'][0]['name']
          st.experimental_rerun()

placeholder.selectbox(label="This app is designed to find similar games. You may find games you didn't know but will love 😍 even more!", options=model.df_games.sort_values('usersrated', ascending=False)['name'], key='selected_game')
with st.expander("🔎  Click for explanation"):
     
     st.write("""
         
         
         The results are sorted by similarity by default. This means obviously that the game you selected comes first.
         Other stats are:
         
         ▶ Average: the average rating the game received
        
         ▶ Geekrating: the BGG GeekRating, which penalizes game with few ratings
        
         ▶ # Ratings: the amount of times a game has been rated
        
         ▶ Weight: the 'complexity of a game between 1-5
         
         👉Click on a row to see results for that game. 
         
         👉Click on the column names to sort. 
         
         👉Click the game name to go to the game on BoardGameGeek. 
         
         This recommender model uses a technique called 'collaborative filtering', which is similar to how Netflix recommends your next serie.
         A great explanation about the pro's and con's can be found [here](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.1740-9713.2019.01317.x)          
     """)
with st.expander("⚙️ Thanks & feedback ", expanded=False):
     st.markdown(
               """
          Let me know if you have feedback, e.g. on Reddit

          Thanks to:

          * :sun_with_face: [BoardGameGeek](https://boardgamegeek.com/) for making their data openly available.
          * :sun_with_face: [Streamlit](https://streamlit.io/) voor het maken van zo'n geweldige library

          [![License: Creative Commons Naamsvermelding-GelijkDelen 4.0 Internationaal-licentie](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-sa/3.0/) 2022 Jesse van Elteren
               """
     )