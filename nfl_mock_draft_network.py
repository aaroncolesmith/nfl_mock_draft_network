import pandas as pd
import streamlit as st
from pyvis.network import Network
from pyvis import network as net
import streamlit.components.v1 as components
import networkx as nx
import plotly_express as px
import streamlit_analytics
from IPython.core.display import HTML

st.set_page_config(
    page_title='NFL Mock Draft Database',
    page_icon='football',
    layout='wide',
    initial_sidebar_state='collapsed')

def update_colors(fig):
  fig.for_each_trace(lambda trace: trace.update(marker_color='#FB4F14') if trace.name == "Cincinnati Bengals" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#006778') if trace.name == "Jacksonville Jaguars" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#008E97') if trace.name == "Miami Dolphins" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#A71930') if trace.name == "Atlanta Falcons" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#125740') if trace.name == "New York Jets" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#97233F') if trace.name == "Arizona Cardinals" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#0076B6') if trace.name == "Detroit Lions" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#AA0000') if trace.name == "San Francisco 49Ers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#241773') if trace.name == "Baltimore Ravens" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#C60C30') if trace.name == "Buffalo Bills" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#0085CA') if trace.name == "Carolina Panthers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#C83803') if trace.name == "Chicago Bears" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#041E42') if trace.name == "Dallas Cowboys" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#FB4F14') if trace.name == "Denver Broncos" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#203731') if trace.name == "Green Bay Packers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#03202F') if trace.name == "Houston Texans" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#FF3C00') if trace.name == "Cleveland Browns" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#002C5F') if trace.name == "Indianapolis Colts" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#E31837') if trace.name == "Kansas City Chiefs" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#0080C6') if trace.name == "Los Angeles Chargers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#003594') if trace.name == "Los Angeles Rams" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#4F2683') if trace.name == "Minnesota Vikings" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#002244') if trace.name == "New England Patriots" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#D3BC8D') if trace.name == "New Orleans Saints" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#0B2265') if trace.name == "New York Giants" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#A5ACAF') if trace.name == "Las Vegas Raiders" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#004C54') if trace.name == "Philadelphia Eagles" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#FFB612') if trace.name == "Pittsburgh Steelers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#69BE28') if trace.name == "Seattle Seahawks" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#D50A0A') if trace.name == "Tampa Bay Buccaneers" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#4B92DB') if trace.name == "Tennessee Titans" else ())
  fig.for_each_trace(lambda trace: trace.update(marker_color='#773141') if trace.name == "Washington Football Team" else ())

  return fig


st.markdown("<h1 style='text-align: center; color: black;'>NFL Mock Draft Database</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: black;'>Taking a look at a number of public NFL mock drafts to identify trends and relationships</h4>", unsafe_allow_html=True)

df = pd.read_csv('https://raw.githubusercontent.com/aaroncolesmith/nfl_mock_draft_db/main/new_nfl_mock_draft_db.csv')
# df['pick']=df.pick.str.replace('\u200b', '')
# df['pick']=pd.to_numeric(df['pick'])
# df['team_pick'] = 'Pick '+ df['pick'].astype('str').replace('\.0', '', regex=True) + ' - ' +df['team']
# df=df.loc[~df.team_pick.str.contains('/Colleges')]
# st.write(df.head(3))

d=pd.merge(df.iloc[0:500].groupby('player').agg({'pick':'mean','player_details':'size'}).reset_index(),
         df.iloc[501:1000].groupby('player').agg({'pick':'mean','player_details':'size'}).reset_index(),
         left_on='player',
         right_on='player',
         suffixes=('_recent','_before')
)
d=d.loc[d.player_details_recent>=5]
d['chg']=d['pick_recent'] - d['pick_before']
d['pct_chg'] = (d['pick_recent'] - d['pick_before'])/d['pick_before']
d.sort_values('chg',ascending=True)

col1, col2 = st.beta_columns(2)
col1.success("### Players Rising :fire:")
for i, r in d.sort_values('chg',ascending=True).head(5).iterrows():
    col1.write(r['player']+' - trending ' + str(round(abs(r['chg']),2)) + ' picks earlier')


col2.warning("### Players Falling 🧊")
for i, r in d.sort_values('chg',ascending=False).head(5).iterrows():
    col2.write(r['player'] + ' - trending ' + str(round(r['chg'],2)) +' picks later')

del d


st.markdown("<h4 style='text-align: center; color: black;'>Network diagram showing relationships between teams and drafted players in recent mock drafts</h4>", unsafe_allow_html=True)


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


fig=px.bar(df.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15),
       y=df.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).team + ' - '+df.groupby(['team','player']).size().to_frame('cnt').reset_index().sort_values('cnt',ascending=False).head(15).player,
       x='cnt',
       # color='#FA70C8',
       orientation='h',
       title='Most Common Team - Player Pairings')
fig.update_yaxes(title='Count')
fig.update_xaxes(title='Team & Player Pairing', categoryorder='category ascending')
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

fig = px.box(df.loc[df.player.isin(df.groupby('player').agg({'pick':'size'}).reset_index().sort_values('pick',ascending=False).head(25)['player'])], x="player", y="pick", points="all", hover_data=['team','date','source'], title='Distribution of Draft Position by Player', width=1600)
fig.update_xaxes(title='Player', categoryorder='mean ascending')
fig.update_yaxes(title='Draft Position')
st.plotly_chart(fig, use_container_width=True)

d=df.groupby(['team','team_img','player']).agg({'pick':['min','mean','median','size']}).reset_index()
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
fig = update_colors(fig)
st.plotly_chart(fig, use_container_width=True)

d=d.sort_values('avg_pick',ascending=True)
fig=px.scatter(d,
      x='player',
      y='avg_pick',
       size='cnt',
      color='team',
      height=600,
      title='Avg. Pick Placement by Player / Team')
fig.update_xaxes(title='Player')
fig.update_xaxes(categoryorder='mean ascending')
fig.update_yaxes(title='Avg. Draft Position')
fig = update_colors(fig)
st.plotly_chart(fig, use_container_width=True)

df['source_date'] = df['source'] + ' - ' +df['date']
draft = st.selectbox('Pick a draft to view:',df['source_date'].unique())


col1, col2, col3 = st.beta_columns((4,4,4))
df_table=df.loc[df['source_date'] == draft].sort_values('pick',ascending=True).reset_index(drop=True)
df_table['team'] = ["<img src='" + r.team_img
+ f"""' style='display:block;margin-left:auto;margin-right:auto;width:32px;border:0;'><div style='text-align:center'>"""
# + "<br>".join(r.team.split()) + "</div>"
for ir, r in df_table.iterrows()]
df_table['pick'] = df_table['pick'].astype('str').replace('\.0', '', regex=True)

col2.write(df_table[['pick','team','player']].to_html(index=False,escape=False), unsafe_allow_html=True)
