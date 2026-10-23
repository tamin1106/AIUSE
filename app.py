import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='청소년 스마트폰 사용과 스트레스', page_icon='📱', layout='wide')

DATA_FILE = Path(__file__).parent / 'data' / 'official_2025_gender_summary.csv'

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()

st.title('📱 청소년 스마트폰 사용과 스트레스')
st.subheader('스마트폰을 많이 사용하는 학생일수록 스트레스도 높을까?')
st.warning('질병관리청 공개 요약 통계에는 SNS만의 사용시간이 따로 공개되지 않아, 이 앱은 SNS를 포함할 수 있는 전체 스마트폰 사용시간과 스트레스 인지율을 성별로 비교합니다. 따라서 개인별 SNS 사용과 스트레스의 관계를 증명하는 분석은 아닙니다.')

st.markdown('''
### 이 앱에서 비교하는 두 데이터

- **스마트폰 사용시간:** 평일 하루 평균 사용시간(분)
- **스트레스 인지율:** 평소 스트레스를 ‘대단히 많이’ 또는 ‘많이’ 느끼는 학생의 비율
''')

c1, c2, c3 = st.columns(3)
max_phone = df.loc[df['평일 스마트폰 사용시간(분)'].idxmax()]
max_stress = df.loc[df['스트레스 인지율(%)'].idxmax()]
c1.metric('평일 사용시간이 긴 집단', max_phone['성별'], f"{max_phone['평일 스마트폰 사용시간(분)']:.1f}분")
c2.metric('스트레스 인지율이 높은 집단', max_stress['성별'], f"{max_stress['스트레스 인지율(%)']:.1f}%")
c3.metric('여학생-남학생 사용시간 차이', f"{df.loc[df['성별']=='여학생','평일 스마트폰 사용시간(분)'].iloc[0] - df.loc[df['성별']=='남학생','평일 스마트폰 사용시간(분)'].iloc[0]:.1f}분")

st.header('1. 두 지표를 나란히 비교')
fig = go.Figure()
fig.add_bar(name='평일 스마트폰 사용시간(분)', x=df['성별'], y=df['평일 스마트폰 사용시간(분)'], marker_color='#4f86f7', text=df['평일 스마트폰 사용시간(분)'].map(lambda x: f'{x:.1f}분'), textposition='outside', yaxis='y')
fig.add_bar(name='스트레스 인지율(%)', x=df['성별'], y=df['스트레스 인지율(%)'], marker_color='#f28e2b', text=df['스트레스 인지율(%)'].map(lambda x: f'{x:.1f}%'), textposition='outside', yaxis='y2')
fig.update_layout(title='성별 스마트폰 사용시간과 스트레스 인지율', barmode='group', height=500, yaxis=dict(title='사용시간(분)', rangemode='tozero'), yaxis2=dict(title='스트레스 인지율(%)', overlaying='y', side='right', rangemode='tozero'), legend=dict(orientation='h', y=1.12))
st.plotly_chart(fig, use_container_width=True)
st.caption('두 지표는 단위가 다르므로 왼쪽 축은 분, 오른쪽 축은 퍼센트입니다.')

st.header('2. 비교하기 쉬운 상대 점수')
st.write('각 지표에서 남학생 값을 100으로 놓은 비교용 점수입니다. 실제 비율이 아니라 성별 차이를 보기 위한 값입니다.')
score = df.copy()
score['스마트폰 사용시간 점수'] = score['평일 스마트폰 사용시간(분)'] / score.loc[score['성별']=='남학생', '평일 스마트폰 사용시간(분)'].iloc[0] * 100
score['스트레스 인지율 점수'] = score['스트레스 인지율(%)'] / score.loc[score['성별']=='남학생', '스트레스 인지율(%)'].iloc[0] * 100
score_long = score.melt(id_vars='성별', value_vars=['스마트폰 사용시간 점수', '스트레스 인지율 점수'], var_name='지표', value_name='비교 점수')
fig2 = go.Figure()
for name, color in [('스마트폰 사용시간 점수', '#4f86f7'), ('스트레스 인지율 점수', '#f28e2b')]:
    part = score_long[score_long['지표'] == name]
    fig2.add_bar(name=name, x=part['성별'], y=part['비교 점수'], marker_color=color, text=part['비교 점수'].map(lambda x: f'{x:.0f}'), textposition='outside')
fig2.update_layout(barmode='group', height=430, yaxis_title='비교 점수(남학생=100)', yaxis_rangemode='tozero')
st.plotly_chart(fig2, use_container_width=True)

st.header('3. 자료표')
st.dataframe(df, use_container_width=True, hide_index=True)
st.download_button('⬇️ 분석 데이터 CSV 다운로드', df.to_csv(index=False).encode('utf-8-sig'), 'official_2025_gender_summary.csv', 'text/csv')

with st.expander('📌 해석할 때 주의할 점'):
    st.markdown('''
- 이 표는 성별별 평균값을 비교한 것이므로, 같은 학생의 스마트폰 사용시간과 스트레스 응답을 직접 연결한 자료가 아닙니다.
- 따라서 “스마트폰을 많이 사용해서 스트레스가 높아졌다”라고 결론 내릴 수 없습니다.
- 더 정확한 SNS-스트레스 분석을 하려면 질병관리청 원시자료를 내려받아 같은 학생의 사용시간 문항과 스트레스 문항을 교차분석해야 합니다.
- 이 앱의 ‘스마트폰 사용시간’은 SNS만의 사용시간이 아닙니다. 보고서에서는 ‘SNS를 포함할 수 있는 스마트폰 사용시간’이라고 표현하세요.
''')

with st.expander('📚 공식 출처'):
    st.markdown('''
- [질병관리청 청소년건강행태조사](https://www.kdca.go.kr/yhs/yhshmpg/main.do)
- [제21차 2025년 청소년건강행태조사 원시자료 공개 안내](https://www.kdca.go.kr/bbs/kdca/42/304276/download.do)

2025년 조사에서 평일 스마트폰 사용시간은 남학생 253.9분, 여학생 293.2분이었고, 스트레스 인지율은 남학생 32.9%, 여학생 50.3%였습니다.
''')
