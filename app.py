import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='AI 모델 성장 분석', page_icon='🤖', layout='wide')

CSV_FILE = 'ai_models_usable.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df['Publication date'] = pd.to_datetime(df['Publication date'], errors='coerce')
    df['year'] = df['Publication date'].dt.year
    df['Parameters (B)'] = df['Parameters'] / 1e9
    df['Training cost (million USD)'] = df['Training compute cost (2023 USD)'] / 1e6
    return df.dropna(subset=['Publication date', 'Parameters', 'Training compute cost (2023 USD)'])

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"'{CSV_FILE}' 파일이 없습니다. app.py와 같은 폴더에 CSV를 넣어 주세요.")
    st.stop()

st.title('🤖 AI 모델은 시간이 지날수록 커지고 비싸졌을까?')
st.caption('Epoch AI 공식 AI Models 데이터 | 발표일·파라미터 수·학습 비용 추정치가 모두 있는 모델 분석')

with st.sidebar:
    st.header('🔍 분석 필터')
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.slider('발표 연도', min_year, max_year, (min_year, max_year))
    filtered = df[df['year'].between(year_range[0], year_range[1])].copy()
    st.divider()
    st.info('학습 비용은 실제 지출액이 아니라 Epoch AI의 2023년 달러 기준 추정값입니다.')

st.subheader('📌 선택된 데이터 요약')
col1, col2, col3, col4 = st.columns(4)
col1.metric('분석 모델 수', f'{len(filtered):,}개')
col2.metric('파라미터 중앙값', f"{filtered['Parameters (B)'].median():,.2f}B")
col3.metric('학습 비용 중앙값', f"${filtered['Training cost (million USD)'].median():,.2f}M")
col4.metric('분석 기간', f"{filtered['year'].min()}–{filtered['year'].max()}")

if filtered.empty:
    st.warning('선택한 기간에 분석할 데이터가 없습니다.')
    st.stop()

st.subheader('📈 연도별 변화')
yearly = filtered.groupby('year').agg(
    model_count=('Model', 'count'),
    median_parameters=('Parameters (B)', 'median'),
    median_cost=('Training cost (million USD)', 'median')
).reset_index()

trend_col1, trend_col2 = st.columns(2)
with trend_col1:
    fig = px.line(yearly, x='year', y='median_parameters', markers=True,
                  labels={'year': '발표 연도', 'median_parameters': '파라미터 중앙값 (B)'},
                  title='연도별 파라미터 수 중앙값')
    fig.update_yaxes(type='log', title='파라미터 중앙값 (로그 스케일, billion)')
    st.plotly_chart(fig, use_container_width=True)
with trend_col2:
    fig = px.line(yearly, x='year', y='median_cost', markers=True,
                  labels={'year': '발표 연도', 'median_cost': '학습 비용 중앙값 (million USD)'},
                  title='연도별 학습 비용 중앙값')
    fig.update_yaxes(type='log', title='학습 비용 중앙값 (로그 스케일, million USD)')
    st.plotly_chart(fig, use_container_width=True)

st.subheader('🔗 모델 크기와 학습 비용의 관계')
fig = px.scatter(
    filtered, x='Parameters (B)', y='Training cost (million USD)',
    hover_name='Model', color='year', size='Training compute (FLOP)',
    labels={'Parameters (B)': '파라미터 수 (billion)', 'Training cost (million USD)': '학습 비용 추정치 (million USD)', 'year': '발표 연도'},
    title='파라미터 수가 많을수록 학습 비용도 증가했을까?'
)
fig.update_xaxes(type='log')
fig.update_yaxes(type='log')
st.plotly_chart(fig, use_container_width=True)

corr = filtered['Parameters'].corr(filtered['Training compute cost (2023 USD)'], method='spearman')
st.info(f'스피어만 순위 상관계수: **{corr:.3f}**  |  값이 1에 가까울수록 두 변수가 함께 증가하는 경향이 강합니다.')

with st.expander(f'📄 분석에 사용한 데이터 보기 ({len(filtered):,}개 행)'):
    display_cols = ['Model', 'Publication date', 'Parameters', 'Training compute cost (2023 USD)', 'Training compute (FLOP)', 'Parameters notes']
    display_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[display_cols].sort_values('Publication date', ascending=False), use_container_width=True)

with st.expander('📚 데이터 출처와 해석상의 주의점'):
    st.markdown('''
**출처:** [Epoch AI – Data on AI Models](https://epoch.ai/data/ai-models)  
**공식 CSV:** [all_ai_models.csv](https://epoch.ai/data/all_ai_models.csv)  
**라이선스:** Creative Commons Attribution 4.0 (출처와 저자 표시 필요)

- 이 앱은 발표일, 파라미터 수, 학습 비용 추정치가 모두 있는 모델만 분석합니다.
- 학습 비용은 기업의 실제 회계 비용이 아니라 Epoch AI의 추정값입니다.
- 모델마다 공개 정보의 양이 달라서 결과를 모든 AI 모델 전체의 대표값으로 해석하면 안 됩니다.
- 값의 범위가 매우 크므로 그래프는 로그 스케일을 사용했습니다.
''')

st.download_button(
    '⬇️ 현재 필터 데이터 CSV 다운로드',
    filtered.to_csv(index=False).encode('utf-8-sig'),
    file_name='ai_models_filtered.csv',
    mime='text/csv'
)

st.caption('수업 보고서용 질문: “학습 비용 추정치가 공개된 AI 모델은 시간이 지날수록 파라미터 수가 커지고, 학습 비용도 증가했을까?”')
