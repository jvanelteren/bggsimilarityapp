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
     update()
# Initialisation of session state
def reset(clear_cache=False):
     if clear_cache:
          for key in st.session_state.keys():
               del st.session_state[key]

     st.session_state.setdefault('selected_game', 'Chess')
     st.session_state.setdefault('minvotes', 0)
     st.session_state.setdefault('minaverage', 0)
     st.session_state.setdefault('weight', [0.,5.])
     st.session_state.setdefault('amountresults', 10)
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
st.sidebar.slider("Minimal amount of votes",0,5000, key='minvotes', step=100, on_change=update)
st.sidebar.slider("Minimum average score",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f")
st.sidebar.slider("Weight",0.,5., value=[0.,5.], key='weight', step = 0.1, on_change=update, format="%.1f")
st.sidebar.radio("Amount of results",[10, 50,200], key='amountresults', on_change=update)
st.sidebar.radio("Model",['standard', 'experimental'], key='model', on_change=modelupdate)

st.title('BoardGameExplorer')

placeholder = st.empty()
st.markdown("This app is designed to find similar games. You may find games you didn't know but will like even more! The mobile version is basic, while the desktop version shows more stats.")
with st.expander("More details"):
     st.write("""
         The chart above shows some numbers I picked for you.
         I rolled actual dice for these, so they're *guaranteed* to
         be random.
     """)
     mobile = st.radio(
     "",['mobile', 'desktop'],
     )
df = filter(model.most_similar_games(st.session_state['selected_game']))
# import seaborn as sns
# cm = sns.light_palette("green", as_cmap=True)
# st.dataframe(df.style.background_gradient(cmap=cm))

if st.sidebar.button('Reset selections'):
     reset(clear_cache=True)
     st.experimental_rerun()
 
from st_aggrid import JsCode, GridOptionsBuilder

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
     gb = GridOptionsBuilder.from_dataframe(df[['url', 'average', 'thumbnail', 'name']])

     df[' ']= ' '
     # gb.configure_pagination(paginationAutoPageSize=True )
     gb.configure_grid_options(rowHeight=100, pagination=True)

     gb.configure_column(' ', minWidth=100, cellRenderer=image_nation, initialPinned='left')
     gb.configure_column("url", headerName='Name', cellRenderer=link_jscode)

     gb.configure_column('average', headerName='Avg rating', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
     gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
     gb.configure_column('thumbnail', hide=True,suppressToolPanel=True)
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     
     gridOptions = gb.build()
          
          
     # AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True
          #   )
     grid_height= 100*st.session_state['amountresults']+80
     grid_response = AgGrid(
     df[[' ', 'url', 'average', 'usersrated', 'thumbnail', 'name']],
     gridOptions=gridOptions,
     height=grid_height,
     fit_columns_on_grid_load=True,
     allow_unsafe_jscode=True,
     update_mode=GridUpdateMode.SELECTION_CHANGED,
     )
else:
     gb = GridOptionsBuilder.from_dataframe(df)
     
     df[' ']= ' '
     # gb.configure_pagination(paginationAutoPageSize=True )
     gb.configure_grid_options(rowHeight=100, pagination=True)
     gb.configure_column(' ', minWidth=145, cellRenderer=image_nation, initialPinned='left')
     gb.configure_column("url", headerName='Name', cellRenderer=link_jscode)
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

placeholder.selectbox(label='Select a game and see what the most similar games are!', options=model.df_games.sort_values('usersrated', ascending=False)['name'], key='selected_game')