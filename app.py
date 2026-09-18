import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='AI 사용 직업과 고용인원 비교', page_icon='📊', layout='wide')

@st.cache_data
def load_data():
    return pd.read_csv('occupation_ai_employment_merged.csv')

try:
    df = load_data()
except FileNotFoundError:
    st.error('occupation_ai_employment_merged.csv 파일이 app.py와 같은 폴더에 있어야 합니다.')
    st.stop()

st.title('📊 AI를 많이 사용하는 직업은 일하는 사람도 많을까?')
st.write('직업별 AI 사용 비율과 미국에서 실제로 일하는 사람 수를 비교해 봅니다.')
st.warning('두 자료의 범위가 다릅니다. AI 사용 자료는 전 세계 Claude 사용 기록이고, 고용인원 자료는 미국 노동통계입니다. 따라서 “전 세계 사용량과 미국 고용인원의 관계”를 살펴보는 탐색입니다.')

st.subheader('🔎 질문')
st.markdown('> **AI 사용 비율이 높은 직업군은 실제로 일하는 사람도 많을까?**')

c1, c2, c3, c4 = st.columns(4)
c1.metric('비교한 직업군', f"{len(df)}개")
c2.metric('AI 사용 비율 1위', df.loc[df['AI 사용 비율(%)'].idxmax(), '직업군'])
c3.metric('고용인원 1위', df.loc[df['미국 고용인원'].idxmax(), '직업군'])
correlation = df['AI 사용 비율(%)'].corr(df['미국 고용인원'])
c4.metric('두 값의 함께 움직임', f'{correlation:.2f}')

st.subheader('📈 한눈에 비교하기')
st.write('점 하나가 직업군 하나입니다. 오른쪽일수록 일하는 사람이 많고, 위쪽일수록 Claude 사용 비율이 높습니다.')
fig = px.scatter(
    df,
    x='미국 고용인원',
    y='AI 사용 비율(%)',
    text='직업군',
    hover_name='직업군',
    hover_data={'미국 고용인원': ':,', '미국 고용인원(만명)': ':.2f', 'AI 사용 비율(%)': ':.2f', '직업군': False},
    labels={'미국 고용인원': '미국에서 일하는 사람 수', 'AI 사용 비율(%)': '전체 Claude 사용 중 비율 (%)'},
    title='직업군별 AI 사용 비율과 미국 고용인원'
)
fig.update_traces(textposition='top center', marker={'size': 13})
fig.update_xaxes(type='log', tickformat=',')
st.plotly_chart(fig, use_container_width=True)

st.subheader('🧭 네 가지로 나누어 보기')
median_ai = df['AI 사용 비율(%)'].median()
median_jobs = df['미국 고용인원'].median()
def group(row):
    many_ai = row['AI 사용 비율(%)'] >= median_ai
    many_jobs = row['미국 고용인원'] >= median_jobs
    if many_ai and many_jobs:
        return 'AI 사용 많음 · 일하는 사람 많음'
    if many_ai and not many_jobs:
        return 'AI 사용 많음 · 일하는 사람 적음'
    if not many_ai and many_jobs:
        return 'AI 사용 적음 · 일하는 사람 많음'
    return 'AI 사용 적음 · 일하는 사람 적음'

df['구분'] = df.apply(group, axis=1)
summary = df.groupby('구분', as_index=False).agg(직업군수=('직업군', 'count'))
summary['직업군 목록'] = summary['구분'].map(df.groupby('구분')['직업군'].apply(lambda x: ', '.join(x)).to_dict())
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader('🏆 직업군 순위')
view = st.radio('정렬 기준', ['AI 사용 비율이 높은 순서', '미국 고용인원이 많은 순서'], horizontal=True)
if view == 'AI 사용 비율이 높은 순서':
    ranked = df.sort_values('AI 사용 비율(%)', ascending=False)
else:
    ranked = df.sort_values('미국 고용인원', ascending=False)
st.dataframe(ranked[['직업군', 'AI 사용 비율(%)', '미국 고용인원(만명)', '구분']], use_container_width=True, hide_index=True)

with st.expander('💡 이 분석에서 얻을 수 있는 생각'):
    st.markdown('''
- AI 사용 비율이 높은 직업과 실제로 사람이 많이 일하는 직업은 항상 같지 않을 수 있습니다.
- 컴퓨터 관련 직업은 AI 사용 비율이 높지만, 고용인원은 사무·행정이나 판매 직업보다 적을 수 있습니다.
- 반대로 사람이 많이 일하는 직업이라도 AI 사용 비율이 낮을 수 있습니다.
- 따라서 AI의 영향은 “얼마나 많이 쓰이는가”와 “얼마나 많은 사람의 일에 관련되는가”를 함께 봐야 합니다.
''')

with st.expander('📚 자료 출처와 주의점'):
    st.markdown('''
**AI 사용 자료:** [Anthropic Economic Index](https://huggingface.co/datasets/Anthropic/EconomicIndex)  
**고용인원 자료:** [미국 노동통계국 BLS, Occupational Employment and Wage Statistics, May 2025](https://www.bls.gov/news.release/ocwage.t01.htm)

- AI 사용 비율은 전체 Claude 사용 중 해당 직업군으로 분류된 사용의 비율입니다.
- 고용인원은 미국에서 해당 직업으로 일하는 사람의 추정 인원입니다.
- 두 자료의 나라와 조사 방법이 다르므로 인과관계를 증명하는 분석은 아닙니다.
''')

st.download_button('⬇️ 분석 데이터 CSV 다운로드', df.drop(columns=['구분']).to_csv(index=False).encode('utf-8-sig'), 'occupation_ai_employment_merged.csv', 'text/csv')
