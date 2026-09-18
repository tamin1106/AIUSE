import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title='AI 사용량과 학습 계산량', page_icon='🤖', layout='wide')

@st.cache_data
def load_usage():
    df = pd.read_csv('ai_usage.csv')
    df['날짜'] = pd.to_datetime(df['Day'], errors='coerce')
    df['사용 비율'] = pd.to_numeric(df['Estimated share of working-age adults who use generative AI'], errors='coerce')
    df = df.rename(columns={'Entity': '나라'})
    return df.dropna(subset=['날짜', '사용 비율']).copy()

@st.cache_data
def load_compute():
    df = pd.read_csv('ai_training_compute.csv')
    df['발표일'] = pd.to_datetime(df['Publication date'], errors='coerce')
    df['연도'] = df['발표일'].dt.year
    df['학습 계산량 (EFLOP)'] = pd.to_numeric(df['Training compute (FLOP)'], errors='coerce') / 1e18
    df = df.replace([np.inf, -np.inf], np.nan)
    return df.dropna(subset=['발표일', '연도', '학습 계산량 (EFLOP)']).copy()

usage = load_usage()
compute = load_compute()

st.title('🤖 AI 사용량과 AI를 만드는 데 필요한 계산량')
st.caption('공개된 자료를 이용해 AI 사용 비율과 AI 학습에 사용된 계산량을 살펴봅니다.')

use_tab, train_tab, compare_tab, source_tab = st.tabs(['👥 AI 사용량', '🖥️ 학습 계산량', '📊 두 자료 비교', '📚 자료 출처'])

with use_tab:
    st.header('사람들은 AI를 얼마나 사용하고 있을까?')
    st.write('여기서 사용량은 **일하는 나이의 사람 중 생성형 AI를 사용한다고 조사된 사람의 비율**입니다.')
    countries = sorted(usage['나라'].unique().tolist())
    default_country = 'World' if 'World' in countries else countries[0]
    country = st.selectbox('나라 또는 전체 선택', countries, index=countries.index(default_country))
    selected = usage[usage['나라'] == country].sort_values('날짜')
    if selected.empty:
        st.warning('선택한 나라의 자료가 없습니다.')
    else:
        latest = selected.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric('최근 AI 사용 비율', f"{latest['사용 비율']:.1f}%")
        c2.metric('조사 시점', latest['날짜'].strftime('%Y-%m-%d'))
        c3.metric('자료 개수', f"{len(selected)}개")
        fig = px.line(selected, x='날짜', y='사용 비율', markers=True,
                      labels={'날짜': '조사 날짜', '사용 비율': 'AI 사용 비율 (%)'},
                      title=f'{country}의 생성형 AI 사용 비율')
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    with st.expander('사용량 자료 자세히 보기'):
        st.dataframe(usage[['나라', '날짜', '사용 비율']].sort_values(['나라', '날짜']), use_container_width=True)

with train_tab:
    st.header('AI를 만들 때 계산량은 얼마나 필요했을까?')
    st.write('AI를 학습시킬 때 컴퓨터가 처리한 계산량을 비교합니다. 숫자가 클수록 더 많은 계산을 했다는 뜻입니다.')
    min_year, max_year = int(compute['연도'].min()), int(compute['연도'].max())
    years = st.slider('AI 발표 연도', min_year, max_year, (min_year, max_year))
    selected = compute[compute['연도'].between(*years)].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric('분석한 AI 개수', f'{len(selected):,}개')
    c2.metric('계산량 중앙값', f"{selected['학습 계산량 (EFLOP)'].median():,.2f}")
    c3.metric('조사 기간', f'{selected["연도"].min()}–{selected["연도"].max()}')
    yearly = selected.groupby('연도').agg(개수=('Model', 'count'), 계산량=('학습 계산량 (EFLOP)', 'median')).reset_index()
    fig = px.line(yearly, x='연도', y='계산량', markers=True,
                  labels={'연도': 'AI 발표 연도', '계산량': '학습 계산량 중앙값'},
                  title='해마다 AI를 만드는 데 필요한 계산량의 변화')
    fig.update_yaxes(type='log')
    st.plotly_chart(fig, use_container_width=True)
    with st.expander('학습 계산량 자료 자세히 보기'):
        cols = [c for c in ['Model', '발표일', '학습 계산량 (EFLOP)', 'Training compute estimation method'] if c in selected.columns]
        st.dataframe(selected[cols].sort_values('발표일', ascending=False), use_container_width=True)

with compare_tab:
    st.header('AI 이용률과 학습연산량 비교')
    st.write('두 자료의 값 자체는 단위가 다르므로, 각각의 변화 방향을 보기 위해 0~100으로 바꾸어 한 그래프에 표시합니다.')
    world = usage[usage['나라'] == 'World'].copy()
    usage_yearly = world.assign(연도=world['날짜'].dt.year).groupby('연도', as_index=False)['사용 비율'].mean()
    compute_yearly = compute.groupby('연도', as_index=False)['학습 계산량 (EFLOP)'].median()
    comparison = usage_yearly.merge(compute_yearly, on='연도', how='inner')
    if len(comparison) < 2:
        st.warning('두 자료의 기간이 겹치는 연도가 부족해 비교 그래프를 만들 수 없습니다.')
    else:
        def scale_to_100(series):
            low, high = series.min(), series.max()
            if high == low:
                return pd.Series([50.0] * len(series), index=series.index)
            return (series - low) / (high - low) * 100

        comparison['AI 이용률 변화 (0~100)'] = scale_to_100(comparison['사용 비율'])
        comparison['학습연산량 변화 (0~100)'] = scale_to_100(comparison['학습 계산량 (EFLOP)'])
        chart_data = comparison[['연도', 'AI 이용률 변화 (0~100)', '학습연산량 변화 (0~100)']].melt(
            id_vars='연도', var_name='자료', value_name='변화 정도'
        )
        fig = px.line(chart_data, x='연도', y='변화 정도', color='자료', markers=True,
                      labels={'연도': '연도', '변화 정도': '각 자료 안에서의 변화 정도 (0~100)'},
                      title='AI 이용률과 학습연산량의 변화 흐름')
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(comparison[['연도', '사용 비율', '학습 계산량 (EFLOP)']], use_container_width=True)
        st.info('이 그래프는 두 자료의 증가·감소 흐름만 비교합니다. AI 이용률이 학습연산량 때문에 증가했다고 증명하는 그래프는 아닙니다.')

with source_tab:
    st.header('자료 출처')
    st.markdown('''
### AI 사용량
[Our World in Data – Estimated share of working-age adults who use generative AI](https://ourworldindata.org/grapher/estimated-share-people-generative-ai.csv)

이 자료는 전 세계 전체 질문 횟수가 아니라, 조사된 사람 중 생성형 AI를 사용한다고 답한 사람의 비율입니다.

### 학습 계산량
[Epoch AI – Data on AI Models](https://epoch.ai/data/ai-models)

AI 모델을 학습시키는 데 사용된 계산량 자료입니다. 이 앱에서는 금액이나 전기요금으로 바꾸지 않고, CSV에 있는 계산량만 사용합니다.

**주의:** 두 자료는 조사 대상과 기간이 다르므로, 두 수치를 하나의 원인·결과 관계로 단정하지 않습니다.
''')

st.download_button('⬇️ AI 사용량 CSV 다운로드', usage.to_csv(index=False).encode('utf-8-sig'), 'ai_usage.csv', 'text/csv')
st.download_button('⬇️ 학습 계산량 CSV 다운로드', compute.to_csv(index=False).encode('utf-8-sig'), 'ai_training_compute.csv', 'text/csv')
