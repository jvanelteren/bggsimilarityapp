import streamlit as st
import pandas as pd
from fastai.tabular.all import load_pickle
from dotproductbias import DotProductBias
import model
from st_aggrid import JsCode, GridOptionsBuilder, AgGrid
from st_aggrid.shared import GridUpdateMode  

pd.options.display.max_rows = 20
pd.options.display.float_format = "{:,.1f}".format
pd.options.mode.chained_assignment = None
from collections import namedtuple
Model = namedtuple('model', 'modelstandard modeltransform users games boardgamemechanic boardgamecategory df gamelist')

# @st.cache()
@st.experimental_singleton()
def load_inputs():
     df_games = pd.read_csv('./input/games_detailed_info_incl_modelid.csv')
     cols = ['thumbnail','url','name','usersrated','average', 'bayesaverage', 'averageweight', 'tag','yearpublished']
     # 'model_score','distance'
     df =  df_games[cols]
    
     gamelist = df.sort_values('usersrated', ascending=False)['name'].copy()
     return Model(
          modelstandard = load_pickle('./input/size30model.pickle'),
          modeltransform = load_pickle('./input/size30modeltransform.pickle'),
          users = load_pickle('./input/userids.pickle'),
          games = load_pickle('./input/gameids.pickle'),
          boardgamemechanic = load_pickle('./input/boardgamemechanic.pickle'),
          boardgamecategory = load_pickle('./input/boardgamecategory.pickle'),
          df = df,
          gamelist = gamelist)

def getgames(game):
     return model.most_similar_games(game,m, st.session_state['model'])



def update():
     # refreshes table when filters are changed
     st.session_state['selected_game'] = st.session_state['selected_game']

# Initialisation of session state
def init(clear_cache=False):
     if clear_cache:
          for key in st.session_state.keys():
               if key != 'selected_game':
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
     update()

def filter(df):
     filtered_df = df.loc[(df['usersrated'] >= st.session_state['minvotes']) &
                          (df['average'] >= st.session_state['minaverage']) &
                          (df['averageweight'] >= st.session_state['weight'][0]) &
                          (df['averageweight'] <= st.session_state['weight'][1])
                          
                          ][:st.session_state['amountresults']]

     if 'year' in st.session_state and st.session_state['year'] != 'No filter':
          filtered_df = df.loc[(df['yearpublished'] <= int(st.session_state['year']))]
          
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
  	var br = document.createElement("br");
  	var linkYear = document.createTextNode('('+params.data.yearpublished+')');
  	link_url = params.value;
  	linkElement.appendChild(linkText);
  	linkElement.appendChild(br);
  	linkElement.appendChild(linkYear);
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

st.set_page_config(
   page_title="BoardGame Explorer",
   page_icon="🎈",
)

m = load_inputs()
init()

# Sidebar filters
st.sidebar.header('App version')
analysis_type = st.sidebar.radio("Analysis",['similarity', 'user predictions'],)
mobile = st.sidebar.radio("Display",['mobile', 'desktop'],)
st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.sidebar.header('Options')
st.sidebar.slider("Minimum average rating",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f")
st.sidebar.slider("Minimal amount of ratings",0,5000, key='minvotes', step=100, on_change=update, help='The rating of games with few ratings is less reliable')
st.sidebar.slider("Weight between",0.,5., value=st.session_state['weight'], key='weight', step = 0.1, on_change=update, format="%.1f", help='The weight is a measure for complexity & depth, 1=Very light games, 5=Very heavy games. Here you can select ligher or heavier games.')
st.sidebar.select_slider("Maximum year of publication",['No filter', *list(range(2015, 2024))], key='year', on_change=update, help='You can use this to filter out newer games which often have hyped ratings')
st.sidebar.multiselect('Having all these tags', m.boardgamecategory + m.boardgamemechanic, key='tag_incl', help="BoardGameGeek has a boardgame category and mechanic. I've combined them into 'tags'")
st.sidebar.multiselect('Excluding all these tags', m.boardgamecategory + m.boardgamemechanic, key='tag_excl')
st.sidebar.radio("Amount of results",[10, 50,22000], key='amountresults', on_change=update, help='Select 22000 if you want to return all of the games')
st.sidebar.radio("Model",['standard', 'experimental'], key='model', on_change=update, help='In the experimental model the ratings are transformed before training: (rating ** 2)/10, to account for the nonlinearity of the 1-10 scale. Since the difference between a 7 or an 8 is much larger than the difference between a 3 and a 4.')
if st.sidebar.button('Reset selections'):
     init(clear_cache=True)
     st.experimental_rerun()


# st.title('BoardGame Explorer')
if analysis_type == 'similarity':
     placeholder = st.empty()
#      try:
          
     df = filter(getgames(st.session_state['selected_game']))
#      except:
#           st.experimental_memo.clear()
#           st.experimental_rerun()
          
     rowsperpage = 50
     grid_height= 100 * min(len(df), rowsperpage) + 80
     
     if mobile == 'mobile':
          image_thumbnail = img_thumbnail_mobile
          thumb_width = 100
          gb = GridOptionsBuilder.from_dataframe(df[['url', 'average', 'thumbnail']])
          gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
          gb.configure_grid_options(rowHeight=100, pagination=True)
          gb.configure_column("url", wrapText=True, headerName='Name', cellRenderer=link_jscode)
          gb.configure_column('average', maxWidth=100, headerName='Rating', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})")
     else:
          image_thumbnail = img_thumbnail_desktop
          thumb_width = 130
          gb = GridOptionsBuilder.from_dataframe(df[['url', 'similarity', 'average', 'bayesaverage', 'usersrated', 'averageweight', 'thumbnail']])  
          gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
          gb.configure_grid_options(rowHeight=100, pagination=True)
          gb.configure_column("url", wrapText=True, minWidth=120, headerName='Name', cellRenderer=link_jscode)
          gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
          gb.configure_column('similarity', headerName='Similarity', valueFormatter="data.similarity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
          gb.configure_column('average', headerName='Average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
          gb.configure_column('bayesaverage', headerName='GeekRating', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
          gb.configure_column('averageweight', headerName='Weight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
     
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
               st.write(st.session_state['selected_game'])
               st.experimental_rerun()


     placeholder.selectbox(label="This app is designed to find similar games. You might find games you didn't know but love 😍 even more!", options=m.gamelist, key='selected_game')
     
     with st.expander("🔎  Click for explanation"):
          st.write("""
          This recommender model uses a technique called 'collaborative filtering', which is similar to how Netflix recommends your next serie.
          A great explanation about the pro's and con's can be found [here](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.1740-9713.2019.01317.x)         
          
          The results are sorted by similarity with the selected game, which means that the game you selected comes on top.
          Other stats are:
          
          ▶ Avg: the average rating the game received
          
          ▶ GeekRating: the BGG GeekRating, which penalizes game with few ratings
          
          ▶ # Ratings: the amount of times a game has been rated
          
          ▶ Weight: the 'complexity of a game between 1-5
          
          👉Click on a row to see results for that game. 
          
          👉Click on the column names to sort. 
          
          👉(on mobile) Click arrow top left to expand options menu
          
          """)

elif analysis_type == 'user predictions':

     user = st.text_input('Enter your BoardGameGeek user name to get your predictions')
     if user:
          if user in m.users:
               user_scores = filter(model.get_user_preds(user, m, st.session_state['model']))
               rowsperpage = 50
               grid_height= 100 * min(len(user_scores), rowsperpage) + 80
               if mobile == 'mobile':
                    image_thumbnail = img_thumbnail_mobile
                    thumb_width = 100
                    gb = GridOptionsBuilder.from_dataframe(user_scores[['thumbnail', 'url', 'preds']])
                    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
                    gb.configure_grid_options(rowHeight=100, pagination=True)
                    gb.configure_column("url", wrapText=True, headerName='Name', cellRenderer=link_jscode)
                    gb.configure_column('preds', headerName='Predict', maxWidth=100, valueFormatter="data.preds.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})", sort='desc')
               else:
                    image_thumbnail = img_thumbnail_desktop
                    thumb_width = 130
                    gb = GridOptionsBuilder.from_dataframe(user_scores[['url', 'preds', 'average', 'bayesaverage', 'usersrated', 'averageweight', 'thumbnail']])
                    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rowsperpage)
                    gb.configure_grid_options(rowHeight=100, pagination=True)
                    gb.configure_column("url", wrapText=True, minWidth=120, headerName='Name', cellRenderer=link_jscode)
                    gb.configure_column("usersrated", headerName='# Ratings', maxwidth=80)
                    gb.configure_column('preds', headerName='Predict', valueFormatter="data.preds.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})", sort='desc')
                    gb.configure_column('average', headerName='Average', valueFormatter="data.average.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})")
                    gb.configure_column('bayesaverage', headerName='GeekRating', valueFormatter="data.bayesaverage.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2})")
                    gb.configure_column('averageweight', headerName='Weight', valueFormatter="data.averageweight.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})")

               # gb.configure_column('nameyear', hide=True,suppressToolPanel=True)
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
               st.write('Submit a BGG username that rated at least 10 games beginning of 2022')
     
with st.expander("⚙️ Thanks & feedback ", expanded=False):
     st.markdown(
               """
          Let me know if you have feedback, e.g. [on Reddit](https://boardgamegeek.com/thread/2811605/made-recommender-based-19m-ratings) or [LinkedIn](https://www.linkedin.com/posts/jessevanelteren_just-launched-the-boardgame-explorer-activity-6897193153204420610-YxkN)
          
          I also made [an analysis of the ratings](https://jvanelteren.github.io/blog/2022/01/19/boardgames.html) with a nice discussion again [on Reddit](https://www.reddit.com/r/boardgames/comments/s8fu55/analyzed_all_19m_reviews_from_boardgamegeek_this/)

          Thanks to:

          * :sun_with_face: [BoardGameGeek](https://boardgamegeek.com/) for making their data openly available.
          * :sun_with_face: [Fast.ai](https://www.fast.ai/) for a great deep learning framework and free courses
          * :sun_with_face: [Streamlit](https://streamlit.io/) for such a great data science tool
          * :sun_with_face: beefsack for the [bgg-ranking-historicals](https://github.com/beefsack/bgg-ranking-historicals)

          [![License: Creative Commons Naamsvermelding-GelijkDelen 4.0 Internationaal-licentie](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-sa/3.0/) 2022 Jesse van Elteren
               """
     )