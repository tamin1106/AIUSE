import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='직업별 AI 활용과 업무시간 변화', page_icon='📊', layout='wide')
DATA_FILE = 'bok_occupation_ai_productivity.csv'

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

try:
    df = load_data()
except FileNotFoundError:
    st.error(f'{DATA_FILE} 파일이 app.py와 같은 폴더에 있어야 합니다.')
    st.stop()

st.title('📊 AI 활용률과 업무시간 감소율 비교')
st.markdown('한국은행 조사자료로 **직업별 AI 업무 활용률**과 **AI 활용 후 업무시간 감소율**을 비교합니다.')
st.info('두 수치는 단위가 다릅니다. AI 활용률은 전체 직업군 중 AI를 업무에 활용한 비율이고, 업무시간 감소율은 AI 활용 후 줄어든 업무시간의 비율입니다.')

st.subheader('🔎 핵심 질문')
st.markdown('> **AI를 많이 사용하는 직업일수록 업무시간이 더 많이 줄었을까?**')

highest_use = df.loc[df['AI 업무 활용률(%)'].idxmax()]
highest_reduction = df.loc[df['AI 활용 후 업무시간 감소율(%)'].idxmax()]
correlation = df['AI 업무 활용률(%)'].corr(df['AI 활용 후 업무시간 감소율(%)'])

c1, c2, c3, c4 = st.columns(4)
c1.metric('조사한 직업군', f'{len(df)}개')
c2.metric('AI 활용률 1위', highest_use['직업군'], f"{highest_use['AI 업무 활용률(%)']:.1f}%")
c3.metric('업무시간 감소 1위', highest_reduction['직업군'], f"{highest_reduction['AI 활용 후 업무시간 감소율(%)']:.1f}%")
c4.metric('상관계수', f'{correlation:.2f}', '함께 증가하는 정도')

# 두 값의 크기가 크게 다르므로, 같은 직업 순서의 두 그래프를 나란히 배치한다.
order = df.sort_values('AI 업무 활용률(%)', ascending=True)['직업군'].tolist()
left, right = st.columns(2)
with left:
    st.subheader('① AI 업무 활용률')
    use_sorted = df.set_index('직업군').loc[order].reset_index()
    fig_use = px.bar(
        use_sorted, x='AI 업무 활용률(%)', y='직업군', orientation='h',
        text='AI 업무 활용률(%)', color_discrete_sequence=['#2563eb'],
        labels={'AI 업무 활용률(%)': '활용률 (%)', '직업군': ''}
    )
    fig_use.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_use.update_layout(xaxis_range=[0, 80], height=570, margin=dict(l=0, r=25, t=20, b=20))
    st.plotly_chart(fig_use, use_container_width=True)
with right:
    st.subheader('② 업무시간 감소율')
    time_sorted = df.set_index('직업군').loc[order].reset_index()
    fig_time = px.bar(
        time_sorted, x='AI 활용 후 업무시간 감소율(%)', y='직업군', orientation='h',
        text='AI 활용 후 업무시간 감소율(%)', color_discrete_sequence=['#f97316'],
        labels={'AI 활용 후 업무시간 감소율(%)': '감소율 (%)', '직업군': ''}
    )
    fig_time.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_time.update_layout(xaxis_range=[0, 3.5], height=570, margin=dict(l=0, r=25, t=20, b=20))
    st.plotly_chart(fig_time, use_container_width=True)

st.caption('두 그래프는 직업군 순서를 똑같이 맞췄습니다. 왼쪽 값과 오른쪽 값이 각각 얼마나 큰지 직업별로 바로 비교할 수 있습니다.')

st.subheader('③ 상대적인 크기 비교')
st.write('두 지표의 단위가 달라서, 각 지표의 최고값을 100으로 놓고 상대적인 크기를 비교합니다. 실제 퍼센트가 아니라 비교용 점수입니다.')
normalized = df[['직업군', 'AI 업무 활용률(%)', 'AI 활용 후 업무시간 감소율(%)']].copy()
normalized['AI 활용 점수'] = normalized['AI 업무 활용률(%)'] / normalized['AI 업무 활용률(%)'].max() * 100
normalized['업무시간 감소 점수'] = normalized['AI 활용 후 업무시간 감소율(%)'] / normalized['AI 활용 후 업무시간 감소율(%)'].max() * 100
long = normalized.melt(id_vars='직업군', value_vars=['AI 활용 점수', '업무시간 감소 점수'], var_name='지표', value_name='비교 점수')
fig_norm = px.bar(long, x='비교 점수', y='직업군', color='지표', barmode='group', orientation='h', text='비교 점수',
                  color_discrete_map={'AI 활용 점수': '#2563eb', '업무시간 감소 점수': '#f97316'},
                  labels={'비교 점수': '최고값=100인 비교 점수', '직업군': '', '지표': ''})
fig_norm.update_traces(texttemplate='%{text:.0f}', textposition='outside')
fig_norm.update_layout(xaxis_range=[0, 115], height=600, legend=dict(orientation='h', y=1.08, x=0))
st.plotly_chart(fig_norm, use_container_width=True)

st.subheader('④ 관계를 확인하는 산점도')
st.write('오른쪽 위에 있는 직업군일수록 AI 활용률과 업무시간 감소율이 모두 높은 편입니다.')
fig_scatter = px.scatter(df, x='AI 업무 활용률(%)', y='AI 활용 후 업무시간 감소율(%)', text='직업군',
    hover_name='직업군', hover_data={'AI 업무 활용률(%)': ':.1f', 'AI 활용 후 업무시간 감소율(%)': ':.1f', '주 40시간 기준 주간 단축 시간(시간)': ':.2f', '직업군': False},
    labels={'AI 업무 활용률(%)': 'AI 업무 활용률 (%)', 'AI 활용 후 업무시간 감소율(%)': '업무시간 감소율 (%)'})
fig_scatter.update_traces(textposition='top center', marker={'size': 14, 'color': '#7c3aed'})
fig_scatter.update_layout(height=560)
st.plotly_chart(fig_scatter, use_container_width=True)

st.info(f'상관계수는 **{correlation:.2f}**입니다. 두 지표가 함께 증가하는 경향을 보여주지만, 이것만으로 AI가 업무시간 감소의 원인이라고 단정할 수는 없습니다.')

st.subheader('📋 직업별 수치')
st.dataframe(df[['직업군', 'AI 업무 활용률(%)', 'AI 활용 후 업무시간 감소율(%)', '주 40시간 기준 주간 단축 시간(시간)']], use_container_width=True, hide_index=True)

with st.expander('💡 분석에서 얻을 수 있는 의미'):
    st.markdown('- 전문가·관리자·사무직은 두 지표가 모두 높은 편입니다.\n- 단순노무·서비스·기능직은 두 지표가 상대적으로 낮습니다.\n- 직업의 업무 내용에 따라 AI의 효과가 다르게 나타날 수 있습니다.')
with st.expander('📚 자료 출처와 주의점'):
    st.markdown('''**출처:** [한국은행 이슈노트 제2025-22호](https://www.bok.or.kr/portal/bbs/P0002353/view.do?nttId=10093071)  
**조사 대상:** 전국 만 15~64세 취업자 5,512명  
**조사 기간:** 2025년 5월 19일~6월 17일

업무시간 감소율은 응답자의 업무시간 변화에 대한 조사 결과입니다. 상관관계는 인과관계를 증명하지 않습니다.''')
st.download_button('⬇️ 분석 데이터 CSV 다운로드', df.to_csv(index=False).encode('utf-8-sig'), 'bok_occupation_ai_productivity.csv', 'text/csv')
