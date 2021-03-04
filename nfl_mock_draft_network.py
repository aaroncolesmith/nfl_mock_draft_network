import pandas as pd
import streamlit as st
from pyvis.network import Network
from pyvis import network as net
import streamlit.components.v1 as components
import networkx as nx
import plotly_express as px
import streamlit_analytics

st.set_page_config(
    page_title='NFL Mock Draft Database',
    page_icon='football',
    layout='wide',
    initial_sidebar_state='collapsed')


with streamlit_analytics.track(unsafe_password="test123"):
    st.markdown("<h1 style='text-align: center; color: black;'>NFL Mock Draft Database</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: black;'>Taking a look at a number of public NFL mock drafts to identify trends and relationships</h4>", unsafe_allow_html=True)

df_i = pd.read_csv('https://raw.githubusercontent.com/aaroncolesmith/nfl_mock_draft_db/main/nfl_mock_draft_db.csv')

num=30

d1=pd.DataFrame()
d2=pd.DataFrame()
for i in df_i.loc[df_i.date.isin(df_i.head(num)['date'].values)].player.unique():
  d1 = pd.concat([d1, df_i.loc[df_i.player == i].iloc[0:5]])
  d2 = pd.concat([d2, df_i.loc[df_i.player == i].iloc[5:10]])

d3=pd.merge(d1.groupby(['player']).agg({'pick':'mean'}).reset_index(), d2.groupby(['player']).agg({'pick':'mean'}).reset_index(), how='left', suffixes=('_0','_1'), left_on='player', right_on='player')
d3['chg'] = d3['pick_0'] - d3['pick_1']
d3['pct_chg']=d3['chg'] / d3['pick_1']
d3=d3.sort_values('chg',ascending=True)

col1, col2 = st.beta_columns(2)
col1.success("### Players Rising :fire:")
for i, r in d3.loc[d3.chg.notnull()].head(5).iterrows():
    col1.write(r['player']+' - trending ' + str(round(abs(r['chg']),2)) + ' picks earlier')


col2.warning("### Players Falling 🧊")
for i, r in d3.loc[d3.chg.notnull()].tail(5).iterrows():
    col2.write(r['player'] + ' - trending ' + str(round(r['chg'],2)) +' picks later')


st.markdown("<h4 style='text-align: center; color: black;'>Network diagram showing relationships between teams and drafted players in recent mock drafts</h4>", unsafe_allow_html=True)



df=pd.DataFrame()
# for i in df_i.player.unique():
#     df = pd.concat([df, df_i.loc[df_i.player == i].head(num)])

df = df_i.loc[df_i.date.isin(df_i.head(num)['date'].values)]

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

nt.force_atlas_2based(damping=2)

with streamlit_analytics.track(unsafe_password="test123"):
    icon = st.checkbox('Show icons (slows it down a bit)')

for i, r in d.iterrows():
    nt.add_node(r['player'],
                size=r['times_picked'],
                color={'background':'#40D0EF','border':'#03AED3'},
                title = '<b>'+r['player'] + ' - Picked '+str(r['times_picked'])+'  times </b> <br> ' + d.loc[d.player==r['player']].groupby('player').apply(lambda x: ', <br>'.join(x.pick_str)).to_frame('pick_str').reset_index()['pick_str'].item())
    if icon:
        nt.add_node(r['team_pick'],
                    size=r['team_times_picked'],
                    color={'background':'#FA70C8','border':'#EC0498'},
                    shape='image',
                    image =r['team_img'],
                    title='<b>' +r['team_pick'] + ' - ' +str(r['team_times_picked'])+'  total picks</b> <br> ' + d.loc[d.team_pick == r['team_pick']].groupby('team_pick').apply(lambda x: ', <br>'.join(x.player_pick_str)).to_frame('cnt').reset_index()['cnt'].item())
    else:
        nt.add_node(r['team_pick'],
                    size=r['team_times_picked'],
                    color={'background':'#FA70C8','border':'#EC0498'},
                    # shape='image',
                    # image =r['team_img'],
                    title='<b>' +r['team_pick'] + ' - ' +str(r['team_times_picked'])+'  total picks</b> <br> ' + d.loc[d.team_pick == r['team_pick']].groupby('team_pick').apply(lambda x: ', <br>'.join(x.player_pick_str)).to_frame('cnt').reset_index()['cnt'].item())

    nt.add_edge(r['player'],
                r['team_pick'],
                value = r['cnt'],
                color='#9DA0DC',
                title=r['team_pick']+' picked '+r['player']+' '+str(r['cnt'])+ '  times')
nt.show('mock_draft_network.html')

html_file = open('./mock_draft_network.html', 'r', encoding='utf-8')
source_code = html_file.read()
components.html(source_code, height=510,width=1300)

# option = st.radio('View all or most recent mock drafts?',('All','Most Recent'))
# if option == 'All':
#     d2 = df_i
#
# if option == 'Most Recent':
#     num=st.number_input('How many recent mock drafts?', min_value=1, max_value=50, value=10)
#     df_latest=pd.DataFrame()
#     d2=pd.DataFrame()
#     df_latest = df_i.loc[df_i.date.isin(df_i.head(num)['date'].values)]
#
#     for i in df_latest.player.unique():
#       d2 = pd.concat([d2, df_latest.loc[df_latest.player == i].head(num)])


d2=df

with streamlit_analytics.track(unsafe_password="test123"):
    fig=px.bar(d2.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15),
           y=d2.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).team + ' - '+d2.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).player,
           x='cnt',
           orientation='h',
           title='Most Common Team - Player Pairings')
    fig.update_yaxes(title='Count')
    fig.update_xaxes(title='Team & Player Pairing', categoryorder='category ascending')
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with streamlit_analytics.track(unsafe_password="test123"):
    fig = px.box(d2.loc[d2.player.isin(d2.groupby('player').agg({'pick':'size'}).reset_index().sort_values('pick',ascending=True).head(25)['player'])], x="player", y="pick", points="all", hover_data=['team','date','source'], title='Distribution of Draft Position by Player', width=1600)
    fig.update_xaxes(title='Player')
    fig.update_yaxes(title='Draft Position')
    st.plotly_chart(fig, use_container_width=True)

with streamlit_analytics.track(unsafe_password="test123"):
    d=d2.groupby(['team','team_img','player']).agg({'pick':['min','mean','median','size']}).reset_index()
    d.columns=['team','team_img','player','min_pick','avg_pick','median_pick','cnt']
    fig=px.scatter(d,
          x='cnt',
          y='avg_pick',
           color='team',
           title='# of Times a Player is Mocked to a Given Pick / Team',
          hover_data=['player'])
    fig.update_xaxes(title='# of Occurences')
    fig.update_yaxes(title='Avg. Draft Pick')
    fig.update_traces(mode='markers',
                      marker=dict(size=8,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')))
    st.plotly_chart(fig, use_container_width=True)

with streamlit_analytics.track(unsafe_password="test123"):
    d=d.sort_values('avg_pick',ascending=True)
    fig=px.scatter(d,
          x='player',
          y='avg_pick',
           size='cnt',
          color='team',
          height=600,
          title='Avg. Pick Placement by Player / Team')
    fig.update_xaxes(title='Player')
    fig.update_yaxes(title='Avg. Draft Position')
    st.plotly_chart(fig, use_container_width=True)
