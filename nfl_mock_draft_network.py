import pandas as pd
import streamlit as st
from pyvis.network import Network
from pyvis import network as net
import streamlit.components.v1 as components
import networkx as nx
import plotly_express as px

st.set_page_config(
    page_title='NFL Mock Draft Database',
    page_icon='football',
    layout='wide',
    initial_sidebar_state='collapsed')

# st.title('NFL Mock Draft Network')
st.markdown("<h1 style='text-align: center; color: black;'>NFL Mock Draft Database</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: black;'>Taking a look at a number of public NFL mock drafts to identify trends and relationships</h4>", unsafe_allow_html=True)


df_i = pd.read_csv('https://raw.githubusercontent.com/aaroncolesmith/nfl_mock_draft_db/main/nfl_mock_draft_db.csv')


d1=pd.DataFrame()
d2=pd.DataFrame()
for i in df_i.player.unique():
  d1 = pd.concat([d1, df_i.loc[df_i.player == i].iloc[0:5]])
  d2 = pd.concat([d2, df_i.loc[df_i.player == i].iloc[5:10]])

d3=pd.merge(d1.groupby(['player']).agg({'pick':'mean'}).reset_index(), d2.groupby(['player']).agg({'pick':'mean'}).reset_index(), how='left', suffixes=('_0','_1'), left_on='player', right_on='player')
d3['chg'] = d3['pick_0'] - d3['pick_1']
d3['pct_chg']=d3['chg'] / d3['pick_1']
d3=d3.sort_values('chg',ascending=True)
st.write(d3.head(7))
st.write(d3.tail(7))

col1, col2 = st.beta_columns(2)
col1.success("### Players Rising :fire:")
for i, r in d3.head(5).iterrows():
    col1.write(r['player']+' - trending ' + str(round(abs(r['chg']),2)) + ' picks earlier')


col2.warning("### Players Falling 🧊")
for i, r in d3.tail(5).iterrows():
    col2.write(r['player'] + ' - trending ' + str(round(r['chg'],2)) +' picks later')


st.markdown("<h4 style='text-align: center; color: black;'>Network diagram showing relationships between teams and drafted players in recent mock drafts</h4>", unsafe_allow_html=True)


num=10
df=pd.DataFrame()
for i in df_i.player.unique():
    df = pd.concat([df, df_i.loc[df_i.player == i].head(num)])

df['team_pick'] = 'Pick '+ df['pick'].astype('str').replace('\.0', '', regex=True) + ' - ' +df['team']
d=df.groupby(['player','team_pick','team_img']).size().to_frame('cnt').reset_index()

player=d.groupby(['player']).agg({'cnt':'sum'}).reset_index()
player.columns=['player','times_picked']
team=d.groupby(['team_pick']).agg({'cnt':'sum'}).reset_index()
team.columns=['team_pick','team_times_picked']

d=pd.merge(d,player)
d=pd.merge(d,team)

d=d.sort_values('cnt',ascending=False)

d['pick_str'] = d['team_pick']+ ' - '+d['cnt'].astype('str')+' times'
d['player_pick_str'] = d['player']+ ' - '+d['cnt'].astype('str')+' times'

nt = Network(directed=False,
             # notebook=True,
             height="480px",
             width="1260px",
             heading='')

for i, r in d.iterrows():
    nt.add_node(r['player'],
                size=r['times_picked'],
                title = '<b>'+r['player'] + '</b> <br> ' + d.loc[d.player==r['player']].groupby('player').apply(lambda x: ', <br>'.join(x.pick_str)).to_frame('pick_str').reset_index()['pick_str'].item())
    nt.add_node(r['team_pick'],
                size=r['cnt'],
                # shape='image',
                # image =r['team_img'],
                title='<b>' +r['team_pick'] + '</b> <br> ' + d.loc[d.team_pick == r['team_pick']].groupby('team_pick').apply(lambda x: ', <br>'.join(x.player_pick_str)).to_frame('cnt').reset_index()['cnt'].item())
    nt.add_edge(r['player'], r['team_pick'], value = r['cnt'], title=r['team_pick']+' picked '+r['player']+' '+str(r['cnt'])+ '  times')
nt.show('mock_draft_network.html')

html_file = open('./mock_draft_network.html', 'r', encoding='utf-8')
source_code = html_file.read()
components.html(source_code, height=510,width=1300)



fig=px.bar(df_i.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15),
       y=df_i.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).team + ' - '+df_i.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).player,
       x='cnt',
       orientation='h',
       title='Most Common Team - Player Pairings')
fig.update_yaxes(title='Count')
fig.update_xaxes(title='Team & Player Pairing', categoryorder='category ascending')
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)


fig = px.box(df_i.loc[df_i.player.isin(df_i.groupby('player').agg({'pick':'mean'}).reset_index().sort_values('pick',ascending=True).head(15)['player'])], x="player", y="pick", points="all", hover_data=['team','date','source'], title='Distribution of Draft Position by Player', width=1600)
fig.update_xaxes(title='Player')
fig.update_yaxes(title='Draft Position')
st.plotly_chart(fig, use_container_width=True)
