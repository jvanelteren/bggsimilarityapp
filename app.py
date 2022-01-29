import streamlit as st
import pandas as pd
pd.options.display.max_rows = 20
pd.options.display.float_format = "{:,.1f}".format
pd.options.mode.chained_assignment = None
from dotproductbias import DotProductBias
import model
from st_aggrid.shared import GridUpdateMode  
from st_aggrid import JsCode, GridOptionsBuilder

from st_aggrid import AgGrid
st.set_page_config(
   page_title="BoardGame Explorer",
   page_icon="🎈",
)


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
               
     hide_streamlit_style = """
          <style>
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}
          </style>
          """
     st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
     
               
     st.session_state.setdefault('selected_game', 'Chess')
     st.session_state.setdefault('minvotes', 500)
     st.session_state.setdefault('minaverage', 0)
     st.session_state.setdefault('weight', [0.,5.])
     st.session_state.setdefault('amountresults', 10)
     st.session_state.setdefault('model', 'standard')
     st.session_state.setdefault('tag_incl', [])
     st.session_state.setdefault('tag_excl', [])
     modelupdate()

def filter(df):
     filtered_df = df.loc[(df['usersrated'] >= st.session_state['minvotes']) &
                          (df['average'] >= st.session_state['minaverage']) &
                          (df['averageweight'] >= st.session_state['weight'][0]) &
                          (df['averageweight'] <= st.session_state['weight'][1])
                          
                          ][:st.session_state['amountresults']]
     for tag in st.session_state['tag_incl']:
          filtered_df = filtered_df.loc[filtered_df['tag'].str.contains(tag)]
     if st.session_state['tag_excl']:
          reg = '|'.join(st.session_state['tag_excl'])
          filtered_df = filtered_df.loc[~filtered_df['tag'].str.contains(reg, regex=True)]
     
     # filtered_df.set_index('thumbnail', inplace=True)
     # filtered_df.index.name = None
     
     # filtered_df =  filtered_df.sort_values('similarity', ascending=False)
     return filtered_df

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
img_thumbnail_mobile = JsCode("""function (params) {
     var element = document.createElement("span");
     var imageElement = document.createElement("img");

     if (params.data.thumbnail) {
          imageElement.src = params.data.thumbnail;
          imageElement.width="100";
     } else {
          imageElement.src = "";
     }
     element.appendChild(imageElement);
     return element;
     }""")

     # element.appendChild(document.createTextNode(params.value));
img_thumbnail_desktop = JsCode("""function (params) {
     var element = document.createElement("span");
     var imageElement = document.createElement("img");

     if (params.data.thumbnail) {
          imageElement.src = params.data.thumbnail;
          imageElement.width="120";
     } else {
          imageElement.src = "";
     }
     element.appendChild(imageElement);
     return element;
     }""")

     # element.appendChild(document.createTextNode(params.value));

reset()
# Sidebar filters
st.sidebar.header('App version')
analysis_type = st.sidebar.radio("Analysis",['similarity', 'user predictions'],)
mobile = st.sidebar.radio("Display",['mobile', 'desktop'],)
st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.sidebar.header('Options')
st.sidebar.slider("Minimal amount of ratings",0,5000, key='minvotes', step=100, on_change=update)
st.sidebar.slider("Minimum average rating",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f")
st.sidebar.slider("Weight between",0.,5., value=[0.,5.], key='weight', step = 0.1, on_change=update, format="%.1f")
st.sidebar.multiselect('Having all these tags', model.boardgamecategory + model.boardgamemechanic, key='tag_incl')
st.sidebar.multiselect('Excluding all these tags', model.boardgamecategory + model.boardgamemechanic, key='tag_excl')
st.sidebar.radio("Amount of results",[10, 50,22000], key='amountresults', on_change=update)
st.sidebar.radio("Model",['standard', 'experimental'], key='model', on_change=modelupdate)




st.title('BoardGame Explorer')
if analysis_type == 'similarity':
     placeholder = st.empty()
     df = filter(model.most_similar_games(st.session_state['selected_game']))

     if st.sidebar.button('Reset selections'):
          reset(clear_cache=True)
          st.experimental_rerun()
     
     rowsperpage = 50
     grid_height= 100 * min(len(df), rowsperpage) + 80

     if mobile == 'mobile':
          image_thumbnail = img_thumbnail_mobile
          thumb_width = 100
          gb = GridOptionsBuilder.from_dataframe(df[['url', 'average', 'name', 'thumbnail']])
          gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
          gb.configure_grid_options(rowHeight=100, pagination=True)
          gb.configure_column("url", wrapText=True, headerName='Name', cellRenderer=link_jscode)
          gb.configure_column('average', maxWidth=90, headerName='Rating', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})")
          
     else:
          image_thumbnail = img_thumbnail_desktop
          thumb_width = 130
          gb = GridOptionsBuilder.from_dataframe(df[['url', 'similarity', 'average', 'bayesaverage', 'usersrated', 'averageweight', 'name', 'thumbnail']])  
          gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
          gb.configure_grid_options(rowHeight=100, pagination=True)
          gb.configure_column("url", wrapText=True, minWidth=120, headerName='Name', cellRenderer=link_jscode)
          gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
          gb.configure_column('similarity', headerName='Similarity', valueFormatter="data.similarity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
          gb.configure_column('average', headerName='Average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
          gb.configure_column('bayesaverage', headerName='GeekRating', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
          gb.configure_column('averageweight', headerName='Weight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
     
     gb.configure_column('name', hide=True,suppressToolPanel=True)
     gb.configure_selection(selection_mode="single", use_checkbox=False)
     gb.configure_column('thumbnail', headerName='', minWidth=thumb_width, cellRenderer=image_thumbnail, initialPinned='left')     
     gridOptions = gb.build()
     grid_response = AgGrid(
          df,
          gridOptions=gridOptions,
          update_mode=GridUpdateMode.SELECTION_CHANGED,
          height=grid_height,
          fit_columns_on_grid_load=True,
          allow_unsafe_jscode=True)

     if grid_response['selected_rows']:
          if grid_response['selected_rows'][0]['name'] != st.session_state['selected_game']:
               st.session_state['selected_game'] = grid_response['selected_rows'][0]['name']
               st.experimental_rerun()

     placeholder.selectbox(label="This app is designed to find similar games. You may find games you didn't know but will love 😍 even more!", options=model.df.sort_values('usersrated', ascending=False)['name'], key='selected_game')
     with st.expander("🔎  Click for explanation"):
          
          st.write("""
          This recommender model uses a technique called 'collaborative filtering', which is similar to how Netflix recommends your next serie.
          A great explanation about the pro's and con's can be found [here](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.1740-9713.2019.01317.x)         
          
          The results are sorted by similarity with the selected game, which means that the game you selected comes on top.
          Other stats are:
          
          ▶ Average: the average rating the game received
          
          ▶ Geekrating: the BGG GeekRating, which penalizes game with few ratings
          
          ▶ # Ratings: the amount of times a game has been rated
          
          ▶ Weight: the 'complexity of a game between 1-5
          
          👉Click on a row to see results for that game. 
          
          👉Click on the column names to sort. 
          
          👉Click the game name to go to the game on BoardGameGeek. 
          
          """)
     
     

elif analysis_type == 'user predictions':

     # Some space for experimenting with User preds

     user = st.text_input('Enter your BoardGameGeek user name to get your predictions')
     if user:
          if user in model.users:
               user_scores = filter(model.get_user_preds(user))
               rowsperpage = 50
               grid_height= 100 * min(len(user_scores), rowsperpage) + 80
               if mobile == 'mobile':
                    image_thumbnail = img_thumbnail_mobile
                    thumb_width = 100
                    gb = GridOptionsBuilder.from_dataframe(user_scores[['thumbnail', 'url', 'average', 'name', 'preds']])
                    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
                    gb.configure_grid_options(rowHeight=100, pagination=True)
                    gb.configure_column("url", wrapText=True, headerName='Name', cellRenderer=link_jscode)
                    gb.configure_column('average', maxWidth=90, headerName='Rating', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})")
                    gb.configure_column('preds', headerName='Predict', valueFormatter="data.preds.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
               else:
                    image_thumbnail = img_thumbnail_desktop
                    thumb_width = 130
                    gb = GridOptionsBuilder.from_dataframe(user_scores[['url', 'preds', 'average', 'bayesaverage', 'usersrated', 'averageweight', 'name', 'thumbnail']])
                    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
                    gb.configure_grid_options(rowHeight=100, pagination=True)
                    gb.configure_column("url", wrapText=True, minWidth=120, headerName='Name', cellRenderer=link_jscode)
                    gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
                    gb.configure_column('preds', headerName='Predict', valueFormatter="data.preds.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
                    gb.configure_column('average', headerName='Average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
                    gb.configure_column('bayesaverage', headerName='GeekRating', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
                    gb.configure_column('averageweight', headerName='Weight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")

               gb.configure_column('name', hide=True,suppressToolPanel=True)
               gb.configure_column('thumbnail', headerName='', minWidth=thumb_width, cellRenderer=image_thumbnail, initialPinned='left')
               gridOptions = gb.build()
               user_scoreag = AgGrid(
                    user_scores,
                    gridOptions=gridOptions,
                    update_mode=GridUpdateMode.NO_UPDATE,
                    height=grid_height,
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True)
          else:
               st.write('Sumbit a BGG username that rated at least 10 games beginning of 2022')
     
with st.expander("⚙️ Thanks & feedback ", expanded=False):
     st.markdown(
               """
          Let me know if you have feedback, e.g. on Reddit

          Thanks to:

          * :sun_with_face: [BoardGameGeek](https://boardgamegeek.com/) for making their data openly available.
          * :sun_with_face: [Streamlit](https://streamlit.io/) for such a great data science tool

          [![License: Creative Commons Naamsvermelding-GelijkDelen 4.0 Internationaal-licentie](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-sa/3.0/) 2022 Jesse van Elteren
               """
     )