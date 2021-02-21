import pandas as pd
import streamlit as st
from pyvis.network import Network
from pyvis import network as net
import streamlit.components.v1 as components
import networkx as nx

st.set_page_config(
    page_title='NFL Mock Draft Network',
    page_icon='football',
    # layout='wide',
    initial_sidebar_state='collapsed')

st.title('NFL Mock Draft Network')

df_i = pd.read_csv('https://raw.githubusercontent.com/aaroncolesmith/nfl_mock_draft_db/main/nfl_mock_draft_db.csv')
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
             notebook=True,
             height="600px",
             width="800px",
             heading='')

for i, r in d.iterrows():
    nt.add_node(r['player'],
                size=r['times_picked'],
                title = '<b>'+r['player'] + '</b> <br> ' + d.loc[d.player==r['player']].groupby('player').apply(lambda x: ', <br>'.join(x.pick_str)).to_frame('pick_str').reset_index()['pick_str'].item())
    nt.add_node(r['team_pick'],
                size=r['times_picked'],
                # shape='image',
                # image =r['team_img'],
                title='<b>' +r['team_pick'] + '</b> <br> ' + d.loc[d.team_pick == r['team_pick']].groupby('team_pick').apply(lambda x: ', <br>'.join(x.player_pick_str)).to_frame('cnt').reset_index()['cnt'].item())
    nt.add_edge(r['player'], r['team_pick'], value = r['cnt'], title=r['team_pick']+' picked '+r['player']+' '+str(r['cnt'])+ '  times')
nt.show('mock_draft_network.html')

html_file = open('./mock_draft_network.html', 'r', encoding='utf-8')
source_code = html_file.read()
components.html(source_code, height = 600,width=800)
