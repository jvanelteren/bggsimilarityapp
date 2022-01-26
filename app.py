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

def quickselect():
     # refreshes table when filters are changed
     st.session_state['selected_game'] = st.session_state['quick_selection']
     update()

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
     st.session_state.setdefault('quick_selection', 'Chess')
     st.session_state.setdefault('quick_options', ['Agricola', 'Pandemic', 'Chess', 'Monopoly'])
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
     
     filtered_df =  filtered_df.sort_values('similarity', ascending=False)
     st.session_state['quick_options'] = filtered_df['name'][:10]
     return filtered_df
# Sidebar filters
st.sidebar.header('Options to filter and sort')
st.sidebar.slider(
    "Minimal amount of votes",0,5000, key='minvotes', step=100, on_change=update
)
st.sidebar.slider(
    "Minimum average score",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f"
)
st.sidebar.slider(
    "Weight",0.,5., value=[0.,5.], key='weight', step = 0.1, on_change=update, format="%.1f"
)
st.sidebar.radio(
    "Amount of results",[10, 100,1000], key='amountresults', on_change=update
)
st.sidebar.radio(
    "Model",['standard', 'experimental'], key='model', on_change=modelupdate
)

st.title('BoardGameExplorer')
mobile = st.radio(
    "",['mobile', 'desktop'],
)
game = st.selectbox(label='Select a game and see what the most similar games are!', options=model.df_games.sort_values('usersrated', ascending=False)['name'], key='selected_game')
df = filter(model.most_similar_games(st.session_state['selected_game']))


st.sidebar.radio(
    "Quick select game",st.session_state['quick_options'], key = 'quick_selection', on_change=quickselect
)
if st.sidebar.button('Reset selections'):
     reset(clear_cache=True)
     st.experimental_rerun()
 
from st_aggrid import JsCode, GridOptionsBuilder

# gb.configure_column("link", headerName="thumbnail",
#                             cellRenderer=JsCode('''function(params) {return '<a href="https://www.google.com">params.value</a>'}'''),
#                             width=300)
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
     gb.configure_column("url", cellRenderer=link_jscode)
     gb.configure_column('average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     gb.configure_column('thumbnail', hide=True,suppressToolPanel=True)
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     
     gridOptions = gb.build()
          
          
     # AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True
          #   )
     grid_height= 100*st.session_state['amountresults']+70
     grid_response = AgGrid(
     df[[' ', 'url', 'average', 'thumbnail', 'name']],
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
     gb.configure_column("url", cellRenderer=link_jscode)
     gb.configure_column("usersrated", maxwidth=80)
     gb.configure_column('similarity', valueFormatter="data.similarity.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     gb.configure_column('average', valueFormatter="data.similarity.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     # gb.configure_column('bayesaverage', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     gb.configure_column('averageweight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_column('thumbnail', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     
     gridOptions = gb.build()
     # AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True
          #   )
     grid_height= 100*st.session_state['amountresults']+70

     grid_response = AgGrid(
     df,
     gridOptions=gridOptions,
     update_mode=GridUpdateMode.SELECTION_CHANGED,
     
     height=grid_height,
     fit_columns_on_grid_load=True,
     allow_unsafe_jscode=True,
     )
# grid_response = AgGrid(
#     df, 
#     gridOptions=gridOptions,
#     height=grid_height, 
#     width='100%',
#     data_return_mode=return_mode_value, 
#     update_mode=update_mode_value,
#     fit_columns_on_grid_load=fit_columns_on_grid_load,
#     allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
#     enable_enterprise_modules=enable_enterprise_modules,
#     )
# col1, = st.columns(1)
# with col1:
#      table = st.dataframe(df.to_html(escape = False, index=False), unsafe_allow_html = True)

st.info(grid_response['selected_rows'][0]['name'])
