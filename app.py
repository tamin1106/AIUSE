import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='직업별 AI 사용량', page_icon='🤖', layout='wide')

@st.cache_data
def load_data():
    df = pd.read_csv('global_occupation_ai_usage.csv')
    df['시작일'] = pd.to_datetime(df['시작일'])
    df['종료일'] = pd.to_datetime(df['종료일'])
    df['기간'] = df['시작일'].dt.strftime('%Y년 %m월')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("global_occupation_ai_usage.csv 파일이 app.py와 같은 폴더에 있어야 합니다.")
    st.stop()

st.title('🤖 직업별 AI 사용량 비교')
st.write('사람들이 Claude를 어떤 직업의 일에 많이 사용했는지 비교해 봅니다.')
st.info('이 자료의 사용 비율은 전체 Claude 사용 중 해당 직업으로 분류된 사용이 차지하는 비율입니다. 그 직업 종사자 중 몇 %가 AI를 썼다는 뜻은 아닙니다.')

periods = sorted(df['기간'].unique())
selected_period = st.sidebar.selectbox('기간 선택', periods, index=len(periods) - 1)
period_df = df[df['기간'] == selected_period].copy()

# 분류 단계 1은 큰 직업군이다. 세부 직업은 기본 화면에서 제외해 비교를 쉽게 한다.
large_groups = period_df[period_df['분류단계'] == 1].sort_values('AI 사용 비율(%)', ascending=False)

st.subheader(f'📊 {selected_period} 직업군별 AI 사용 비율')
if large_groups.empty:
    st.warning('선택한 기간에 큰 직업군 자료가 없습니다.')
else:
    top_group = large_groups.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric('가장 큰 직업군', top_group['직업'])
    c2.metric('사용 비율', f"{top_group['AI 사용 비율(%)']:.2f}%")
    c3.metric('비교한 직업군 수', f'{len(large_groups)}개')

    fig = px.bar(
        large_groups,
        x='AI 사용 비율(%)',
        y='직업',
        orientation='h',
        text='AI 사용 비율(%)',
        color='AI 사용 비율(%)',
        color_continuous_scale='Blues',
        labels={'AI 사용 비율(%)': 'Claude 사용 비율 (%)', '직업': '직업군'},
        title='직업군별 Claude 사용 비율'
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.subheader('🔎 직업군을 직접 비교하기')
choices = large_groups['직업'].tolist()
selected_groups = st.multiselect('비교할 직업군 선택', choices, default=choices[:3])
if selected_groups:
    compare_df = large_groups[large_groups['직업'].isin(selected_groups)]
    st.dataframe(compare_df[['직업', 'AI 사용 비율(%)']].reset_index(drop=True), use_container_width=True)
else:
    st.warning('직업군을 하나 이상 선택해 주세요.')

with st.expander('📄 세부 직업까지 보기'):
    detailed = period_df[period_df['분류단계'] == 0].sort_values('AI 사용 비율(%)', ascending=False)
    st.dataframe(detailed[['직업', '직업코드', 'AI 사용 비율(%)']].head(50), use_container_width=True)

with st.expander('💡 이 자료로 생각해 볼 수 있는 점'):
    st.markdown('''
- 어떤 직업군에서 AI 활용이 많이 나타나는지 비교할 수 있습니다.
- 컴퓨터·수학 관련 직업이 높은 비중을 차지하는지 확인할 수 있습니다.
- 교육, 사무, 예술 등 다른 직업군과 사용 비율을 비교할 수 있습니다.
- 컴퓨터공학 진로를 생각한다면 AI를 사용하는 직업과 업무가 무엇인지 살펴볼 수 있습니다.
''')

with st.expander('📚 자료 출처와 주의점'):
    st.markdown('''
**자료 출처:** [Anthropic Economic Index 공식 데이터셋](https://huggingface.co/datasets/Anthropic/EconomicIndex)  
**원자료:** Anthropic Economic Index 2026-06-26 공개본  
**라이선스:** CC-BY 4.0

이 자료는 모든 AI 서비스의 사용량이 아니라 **Claude 사용량**을 분석한 자료입니다. 또한 사용 비율은 직업 종사자의 이용률이 아니라, 전체 Claude 사용 중 해당 직업으로 분류된 비중입니다.
''')

st.download_button(
    '⬇️ 현재 기간의 데이터 다운로드',
    period_df.to_csv(index=False).encode('utf-8-sig'),
    file_name=f'occupation_ai_usage_{selected_period.replace("년 ", "_").replace("월", "")}.csv',
    mime='text/csv'
)
