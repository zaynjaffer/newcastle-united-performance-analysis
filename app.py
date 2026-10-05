from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='NUFC Post-Goal Control', page_icon='⚫', layout='wide')
BASE=Path(__file__).parent
DATA=BASE

@st.cache_data
def load_data():
    x=DATA/'event_analysis.xlsx'
    return {
        'windows':pd.read_excel(x,sheet_name='Goal Windows'),
        'goals':pd.read_excel(x,sheet_name='Goals'),
        'shots':pd.read_excel(x,sheet_name='Shots'),
        'uncertainty':pd.read_excel(x,sheet_name='Uncertainty'),
        'players':pd.read_csv(DATA/'players.csv'),
        'pairs':pd.read_csv(DATA/'pairs.csv'),
        'subs':pd.read_csv(DATA/'subs.csv'),
        'player_windows':pd.read_csv(DATA/'player_windows.csv'),
    }
d=load_data(); W=d['windows']; S=d['shots']; G=d['goals']; P=d['players']; PA=d['pairs']

st.markdown('''<style>
.block-container{padding-top:1.25rem;max-width:1400px}.metric-card{border:1px solid #ddd;border-radius:12px;padding:12px}.small{color:#666;font-size:.9rem}
</style>''',unsafe_allow_html=True)

st.title('Newcastle United 2025/26 — Post-Goal Control')
st.caption('Interactive portfolio dashboard | 38 Premier League matches • 962 shots • 108 goals')

page=st.sidebar.radio('Explore', ['Overview','Post-goal analysis','Shot map','Why control changes','Players & units','Match explorer','Methodology'])
st.sidebar.markdown('---')
st.sidebar.caption('PGCI = Newcastle mean share of shots, SOT and xG. 50 = even control.')

# helpers
def complete(event='Scored',window=15,venue='All'):
    q=W[(W.goal_event==event)&(W.window==window)&(W.complete_window==True)].copy()
    if venue!='All': q=q[q.venue==venue]
    return q

def pitch_scatter(df,title):
    fig=go.Figure()
    # half-pitch geometry based on supplied coordinate orientation
    fig.add_shape(type='rect',x0=0,y0=0,x1=35,y1=100,line=dict(color='gray'))
    fig.add_shape(type='rect',x0=0,y0=21.1,x1=16.5,y1=78.9,line=dict(color='gray'))
    fig.add_shape(type='rect',x0=0,y0=36.8,x1=5.5,y1=63.2,line=dict(color='gray'))
    for team,label,sym in [(True,'Newcastle','circle'),(False,'Opponent','x')]:
        z=df[df.is_nufc==team] if 'is_nufc' in df.columns else df[df.team.eq('Newcastle United')==team]
        if len(z):
            fig.add_trace(go.Scatter(x=z.start_x,y=z.start_y,mode='markers',name=label,
                marker=dict(size=np.clip(8+z.xg.fillna(0)*34,8,26),symbol=sym,opacity=.7),
                customdata=np.stack([z.player_name,z.minute,z.xg.fillna(0),z.outcome,z.situation],axis=-1),
                hovertemplate='<b>%{customdata[0]}</b><br>Minute %{customdata[1]}<br>xG %{customdata[2]:.3f}<br>%{customdata[3]} • %{customdata[4]}<extra></extra>'))
    fig.update_xaxes(range=[35,0],title='Distance from goal line (m)')
    fig.update_yaxes(range=[0,100],title='Pitch width')
    fig.update_layout(title=title,height=560,legend_orientation='h',margin=dict(l=20,r=20,t=55,b=20))
    return fig

if page=='Overview':
    q=complete('Scored',15)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('15m xG differential',f"{q.xg_diff.mean():+.3f}")
    c2.metric('15m SOT differential',f"{q.sot_diff.mean():+.2f}")
    c3.metric('15m PGCI',f"{q.PGCI.mean():.1f}")
    c4.metric('Qualifying goal windows',len(q))
    st.subheader('The story')
    st.write('Newcastle generally retain better chance quality after scoring, but the effect weakens away from home. The strongest tactical separator in the study is whether Newcastle maintain positive territorial pressure after going ahead.')
    a=complete('Scored',15).groupby('venue',as_index=False).agg(PGCI=('PGCI','mean'),xG_diff=('xg_diff','mean'),SOT_diff=('sot_diff','mean'))
    col1,col2=st.columns(2)
    with col1: st.plotly_chart(px.bar(a,x='venue',y='PGCI',text_auto='.1f',title='Post-score control by venue').add_hline(y=50,line_dash='dash'),use_container_width=True)
    with col2: st.plotly_chart(px.bar(a,x='venue',y='xG_diff',text_auto='.3f',title='15-minute xG differential after scoring').add_hline(y=0,line_dash='dash'),use_container_width=True)
    st.info('Portfolio takeaway: retaining territory and chance quality after scoring appears more informative than simply counting shots.')

elif page=='Post-goal analysis':
    event=st.selectbox('Goal event',['Scored','Conceded'])
    venue=st.selectbox('Venue',['All','Home','Away'])
    rows=[]
    for w in [5,10,15]:
        q=complete(event,w,venue)
        rows.append({'Window':f'{w} min','Shots diff':q.shots_diff.mean(),'SOT diff':q.sot_diff.mean(),'xG diff':q.xg_diff.mean(),'xGOT diff':q.xgot_diff.mean(),'PGCI':q.PGCI.mean(),'N':len(q)})
    z=pd.DataFrame(rows)
    st.dataframe(z.style.format({'Shots diff':'{:+.2f}','SOT diff':'{:+.2f}','xG diff':'{:+.3f}','xGOT diff':'{:+.3f}','PGCI':'{:.1f}'}),use_container_width=True,hide_index=True)
    long=z.melt(id_vars=['Window'],value_vars=['Shots diff','SOT diff','xG diff','xGOT diff'],var_name='Metric',value_name='Differential')
    st.plotly_chart(px.line(long,x='Window',y='Differential',color='Metric',markers=True,title=f'Newcastle response after a goal {event.lower()}'),use_container_width=True)
    st.plotly_chart(px.line(z,x='Window',y='PGCI',markers=True,title='Post-Goal Control Index').add_hline(y=50,line_dash='dash'),use_container_width=True)

elif page=='Shot map':
    event=st.selectbox('Following',['Newcastle scoring','Newcastle conceding'])
    window=st.select_slider('Window (minutes)',options=[5,10,15],value=15)
    venue=st.selectbox('Venue',['All','Home','Away'])
    ev='Scored' if 'scoring' in event else 'Conceded'
    goals=G[G.event==ev].copy()
    if venue!='All': goals=goals[goals.venue==venue]
    parts=[]
    for _,g in goals.iterrows():
        if g.match_end_t-g.t < window: continue
        x=S[(S.match_id==g.match_id)&(S.t>g.t)&(S.t<=g.t+window)].copy()
        x['is_nufc']=x.team.eq('Newcastle United')
        parts.append(x)
    shots=pd.concat(parts,ignore_index=True) if parts else S.iloc[0:0].copy()
    st.plotly_chart(pitch_scatter(shots,f'Shots in {window} minutes after {event.lower()}'),use_container_width=True)
    c1,c2,c3=st.columns(3)
    n=shots[shots.is_nufc]; o=shots[~shots.is_nufc]
    c1.metric('NUFC shots',len(n),delta=len(n)-len(o)); c2.metric('NUFC xG',f'{n.xg.sum():.2f}',delta=f'{n.xg.sum()-o.xg.sum():+.2f}'); c3.metric('NUFC SOT',int(n.is_sot.sum()),delta=int(n.is_sot.sum()-o.is_sot.sum()))

elif page=='Why control changes':
    st.subheader('Territory / pressure mechanism')
    mech=pd.DataFrame({'Pressure state':['Negative','Positive'],'PGCI':[32.906,62.387],'xG diff':[-.118,.314],'SOT diff':[-.400,.519],'Shot diff':[-1.400,.852]})
    col1,col2=st.columns(2)
    with col1: st.plotly_chart(px.bar(mech,x='Pressure state',y='PGCI',text_auto='.1f',title='PGCI after scoring').add_hline(y=50,line_dash='dash'),use_container_width=True)
    with col2:
        ml=mech.melt(id_vars='Pressure state',value_vars=['xG diff','SOT diff','Shot diff'],var_name='Metric',value_name='Differential')
        st.plotly_chart(px.bar(ml,x='Metric',y='Differential',color='Pressure state',barmode='group',title='Control differentials'),use_container_width=True)
    st.write('Positive-pressure post-score windows are associated with substantially stronger shot, SOT and xG control. This is descriptive evidence: the pressure signal is a territory proxy, not possession percentage, and does not establish causation.')
    venue=pd.DataFrame({'Venue':['Away','Home'],'Momentum':[2.791,9.162],'Positive pressure share':[.501,.635],'PGCI':[45.844,55.559],'xG diff':[.067,.217]})
    st.dataframe(venue.style.format({'Momentum':'{:+.2f}','Positive pressure share':'{:.1%}','PGCI':'{:.1f}','xG diff':'{:+.3f}'}),hide_index=True,use_container_width=True)

elif page=='Players & units':
    st.subheader('Player-level post-score control')
    st.caption('Only complete 15-minute windows in which the player remained on the pitch for the full window. Associations, not causal rankings.')
    # tolerate schema from generated CSV
    cols={c.lower():c for c in P.columns}
    min_n=st.slider('Minimum qualifying windows',5,20,8)
    ncol=next((c for c in P.columns if c.lower() in ['n','windows','count']),P.columns[1])
    p=P[pd.to_numeric(P[ncol],errors='coerce')>=min_n].copy()
    pgcol=next((c for c in P.columns if c.lower()=='pgci'),None)
    namecol=next((c for c in P.columns if 'player' in c.lower()),P.columns[0])
    if pgcol:
        p=p.sort_values(pgcol,ascending=False)
        st.plotly_chart(px.bar(p.head(15),x=pgcol,y=namecol,orientation='h',hover_data=p.columns,title='PGCI when player is present').add_vline(x=50,line_dash='dash'),use_container_width=True)
    st.dataframe(p,use_container_width=True,hide_index=True)
    st.subheader('Repeated player combinations')
    pn=next((c for c in PA.columns if c.lower() in ['n','windows','count']),PA.columns[1])
    pp=PA[pd.to_numeric(PA[pn],errors='coerce')>=6].copy()
    if 'PGCI' in pp.columns: pp=pp.sort_values('PGCI',ascending=False)
    st.dataframe(pp.head(20),use_container_width=True,hide_index=True)

elif page=='Match explorer':
    opts=sorted(W.opponent.dropna().unique())
    opp=st.selectbox('Opponent',opts)
    venue=st.selectbox('Venue',sorted(W[W.opponent==opp].venue.unique()))
    mid=W[(W.opponent==opp)&(W.venue==venue)].match_id.iloc[0]
    st.subheader(f'{"Newcastle vs" if venue=="Home" else "Away at"} {opp}')
    goals=G[G.match_id==mid].sort_values('t')
    st.dataframe(goals[['minute','added_time','player_name','event','state_after']],hide_index=True,use_container_width=True)
    shots=S[S.match_id==mid].copy(); shots['is_nufc']=shots.team.eq('Newcastle United')
    st.plotly_chart(pitch_scatter(shots,'All shots in match'),use_container_width=True)
    q=W[(W.match_id==mid)&(W.window==15)&(W.complete_window==True)]
    if len(q): st.dataframe(q[['goal_event','goal_minute','opening_goal','state_after','shots_diff','sot_diff','xg_diff','PGCI']],hide_index=True,use_container_width=True)

else:
    st.header('Methodology')
    st.markdown('''
**Scope.** Newcastle United's 38 Premier League matches in 2025/26: 962 shots and 108 goal incidents.

**Post-goal windows.** A 5/10/15-minute observation is included only when the full requested amount of playing time remained. Added time is incorporated into the effective match clock.

**SOT.** Outcomes recorded as a save or goal. **xGOT** is summed where supplied.

**PGCI.** `100 × mean(Newcastle shot share, Newcastle SOT share, Newcastle xG share)`. A value of 50 represents even control.

**Player analysis.** A player counts as present only when he remains on the pitch for the entire 15-minute post-score window. Pair and player outputs are descriptive associations and should be used to identify video-review questions, not to claim causal player effects.

**Territorial pressure.** The source dataset's minute-level momentum signal is used as a territory/pressure proxy and re-signed so positive values favour Newcastle. It is not possession percentage.

**Interpretation.** This is a one-season observational study. Goal windows within the same match are not fully independent, and contextual splits can become small.
''')
