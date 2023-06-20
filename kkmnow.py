# https://github.com/MoH-Malaysia/covid19-public

## Deploy app on heroku 
# https://www.youtube.com/watch?v=nJHrSvYxzjE

import pandas as pd
import plotly.express as px
import io
import requests
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import datetime

st.set_page_config("Covid-19 Dashboard", page_icon=":bar_chart:", layout="wide")

# All
# https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv
# https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv

# URL of the CSV file
@st.cache_data()
def load_data():    
    url = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv'
    contents = requests.get(url).content
    reader = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    return reader


df = load_data()
#df.info() # display dataframe info
# Select column to show.
df1 = df[['date', 'state', 'cases_new', 'cases_recovered', 'cases_active']]
df1['date'] = pd.to_datetime(df['date'])


#st.dataframe(data=df)
#st.info(len(df))

# ---- SIDEBAR ----
# https://www.youtube.com/watch?v=Sb0A9i6d320

latest_date = ( df1["date"].max() )
start_date = latest_date - datetime.timedelta(days=1)

st.sidebar.header("Please Filter Here: ")

start_date = st.sidebar.date_input('Start date', start_date)
end_date = st.sidebar.date_input('End date', latest_date)

#mask = (df1['date'] > start_date) & (df1['date'] <= end_date)
mask = df[df1["date"].isin(pd.date_range(start_date, end_date))]


city = st.sidebar.multiselect(
   "Select the city: ",
   options=df1["state"].unique(),
   default=df1["state"].unique()
   )


df_selection = df1.query(
    "state == @city"
#    "state == @city & date == @mask"
)

#print(df_selection)

# ---- MAINPAGE ----
st.header(":bar_chart: Dashboard")


## TOP KPI's

cases_new = df1.loc[ df1['date'] == latest_date, 'cases_new' ].sum()
str_date = latest_date
# print("Latest date is ", latest_date, "  :  ", cases_new )
cases_recovered = df1.loc[df1['date'] == latest_date, 'cases_recovered'].sum()
cases_active = df1.loc[df1['date'] == latest_date, 'cases_active'].sum()




column1, column2, column3, column4 = st.columns(4)
with column1:
    st.warning(f"As at {latest_date:%d, %b %Y} ")
with column2:
    st.error(f"New Case :  {cases_new:,}")
with column3:
    st.success(f"Recovered :  {cases_recovered:,}")
with column4:
    st.info(f"Total Active : {cases_active:,}")



#gd = GridOptionsBuilder.from_dataframe(df)
gd = GridOptionsBuilder.from_dataframe(df_selection)
gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=20)
gd.configure_default_column(
   # sortable=True, sort='asc',  # configure default all column
    editable=True, groupable=True
    )
gd.configure_column('date', sort='desc', headerName='Date')
gd.configure_column('state', headerName='State')
gd.configure_side_bar() #Add a sidebar
gd.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection

gridoptions = gd.build()

# col_opt = st.selectbox( label = 'Select column', options = df1.columns )
# cellstyle_jscode = JsCode("""
#         function(params) {
#             if (params.value > 100) {
#                 return {
#                     'color': 'black',
#                     'backgroundColor': 'lightpink'
#                 }
#             }
#         };
#     """)
# gd.configure_column(col_opt, cellStyle=cellstyle_jscode)
# gd.configure_columns([cases_new, cases_recovered, cases_active], cellstyle_jscode )
# gd.configure_column(cases_new, cellstyle_jscode )



# # show grid table
# grid_table = AgGrid(df_selection, 
#         gridOptions=gridoptions, 
#         enable_enterprise_modules=True,
#         reload_data=True,
#         update_mode=GridUpdateMode.SELECTION_CHANGED,
#         allow_unsafe_jscode=True, 
#         theme='material'
#         )


# SALES BY PRODUCT LINE [BAR CHART]
#latest_date = ( df1["date"].max() )
cases_new = df1.loc[ df1['date'] == latest_date, 'cases_new' ].sum()

cases_by_date = (
    #df_selection.groupby(by=["state"]).sum()[["cases_new"]].sort_values(by="state")
    df_selection.groupby(by=["state"]).sum(False,0)[["cases_new"]].sort_values(by="state")
)

fig_cases_new = px.bar (
    cases_by_date,
    x="cases_new",
    y=cases_by_date.index,
    orientation="h",
    title="<b>Cases by State</b>", 
    color_discrete_sequence=["#0083B8"] * len(cases_by_date),
    template="plotly_white",
)

fig_cases_new.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

st.plotly_chart(fig_cases_new)