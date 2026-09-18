import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title='직업별 AI 활용과 업무시간 변화',
    page_icon='📊',
    layout='wide'
)

DATA_FILE = 'bok_occupation_ai_productivity.csv'

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

try:
    df = load_data()
except FileNotFoundError:
    st.error(f'{DATA_FILE} 파일이 app.py와 같은 폴더에 있어야 합니다.')
    st.stop()

st.title('📊 AI를 많이 사용하는 직업은 업무시간도 더 줄었을까?')
st.markdown('''
한국은행 조사자료를 이용해 **직업별 AI 업무 활용률**과 **AI 활용 후 업무시간 감소율**을 비교합니다.
''')

st.info(
    '이 자료는 한국은행이 2025년에 조사한 직업군별 결과입니다. '
    '업무시간 감소가 반드시 AI만의 결과라고 단정할 수는 없으며, 두 지표의 관계를 탐색하는 자료입니다.'
)

st.subheader('🔎 핵심 질문')
st.markdown('> **AI를 많이 사용하는 직업일수록 업무시간이 더 많이 줄어들었을까?**')

# 핵심 수치
highest_use = df.loc[df['AI 업무 활용률(%)'].idxmax()]
highest_reduction = df.loc[df['AI 활용 후 업무시간 감소율(%)'].idxmax()]
correlation = df['AI 업무 활용률(%)'].corr(df['AI 활용 후 업무시간 감소율(%)'])

c1, c2, c3, c4 = st.columns(4)
c1.metric('조사한 직업군', f'{len(df)}개')
c2.metric('AI 활용률 1위', highest_use['직업군'])
c3.metric('업무시간 감소 1위', highest_reduction['직업군'])
c4.metric('두 지표의 함께 움직임', f'{correlation:.2f}')

st.subheader('📈 직업별 AI 활용률')
use_sorted = df.sort_values('AI 업무 활용률(%)', ascending=True)
fig_use = px.bar(
    use_sorted,
    x='AI 업무 활용률(%)',
    y='직업군',
    orientation='h',
    text='AI 업무 활용률(%)',
    color='AI 업무 활용률(%)',
    color_continuous_scale='Blues',
    labels={'AI 업무 활용률(%)': 'AI 업무 활용률 (%)', '직업군': '직업군'},
    title='직업군별 업무 AI 활용률'
)
fig_use.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_use.update_layout(coloraxis_showscale=False, height=520)
st.plotly_chart(fig_use, use_container_width=True)

st.subheader('⏱️ 직업별 업무시간 감소율')
time_sorted = df.sort_values('AI 활용 후 업무시간 감소율(%)', ascending=True)
fig_time = px.bar(
    time_sorted,
    x='AI 활용 후 업무시간 감소율(%)',
    y='직업군',
    orientation='h',
    text='AI 활용 후 업무시간 감소율(%)',
    color='AI 활용 후 업무시간 감소율(%)',
    color_continuous_scale='Oranges',
    labels={'AI 활용 후 업무시간 감소율(%)': '업무시간 감소율 (%)', '직업군': '직업군'},
    title='AI 활용 후 직업군별 업무시간 감소율'
)
fig_time.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_time.update_layout(coloraxis_showscale=False, height=520)
st.plotly_chart(fig_time, use_container_width=True)

st.subheader('🔗 두 지표의 관계')
st.write('점 하나가 직업군 하나입니다. 오른쪽일수록 AI를 많이 사용하고, 위쪽일수록 업무시간 감소율이 높습니다.')
fig_scatter = px.scatter(
    df,
    x='AI 업무 활용률(%)',
    y='AI 활용 후 업무시간 감소율(%)',
    text='직업군',
    hover_name='직업군',
    hover_data={
        'AI 업무 활용률(%)': ':.1f',
        'AI 활용 후 업무시간 감소율(%)': ':.1f',
        '주 40시간 기준 주간 단축 시간(시간)': ':.2f',
        '직업군': False,
    },
    labels={
        'AI 업무 활용률(%)': 'AI 업무 활용률 (%)',
        'AI 활용 후 업무시간 감소율(%)': '업무시간 감소율 (%)',
    },
    title='AI 업무 활용률과 업무시간 감소율의 관계'
)
fig_scatter.update_traces(textposition='top center', marker={'size': 13})
fig_scatter.update_layout(height=600)
st.plotly_chart(fig_scatter, use_container_width=True)

st.info(
    f'이번 자료에서는 두 지표의 상관계수가 **{correlation:.2f}**로 계산되었습니다. '
    '값이 1에 가까울수록 함께 증가하는 경향이 있다는 뜻이지만, 인과관계를 증명하지는 않습니다.'
)

st.subheader('📋 전체 데이터')
st.dataframe(df, use_container_width=True, hide_index=True)

with st.expander('💡 분석에서 얻을 수 있는 의미'):
    st.markdown('''
- 전문가·관리자·사무직은 AI 업무 활용률과 업무시간 감소율이 모두 높은 편입니다.
- 단순노무·서비스·기능직은 두 지표가 상대적으로 낮은 편입니다.
- 생성형 AI의 효과는 모든 직업에서 똑같이 나타나지 않고, 직업의 업무 내용에 따라 달라질 수 있습니다.
- 컴퓨터공학 진로에서는 AI를 사용하는 능력뿐 아니라, AI 결과를 확인하고 업무에 맞게 고치는 능력도 중요합니다.
''')

with st.expander('📚 자료 출처와 주의점'):
    st.markdown('''
**출처:** [한국은행 이슈노트 제2025-22호](https://www.bok.or.kr/portal/bbs/P0002353/view.do?nttId=10093071)  
**조사 대상:** 전국 만 15~64세 취업자 5,512명  
**조사 기간:** 2025년 5월 19일~6월 17일

- 업무시간 감소율은 AI 활용 후 응답한 업무시간 변화에 대한 조사 결과입니다.
- 주 40시간 기준 주간 단축 시간은 감소율을 이용해 계산한 참고값입니다.
- 직업군이 9개뿐이므로 모든 세부 직업에 같은 결과가 적용된다고 볼 수 없습니다.
- 상관관계가 있다고 해서 AI가 업무시간 감소의 유일한 원인이라고 말할 수 없습니다.
''')

st.download_button(
    '⬇️ 분석 데이터 CSV 다운로드',
    df.to_csv(index=False).encode('utf-8-sig'),
    'bok_occupation_ai_productivity.csv',
    'text/csv'
)
