import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='청소년 스마트폰 사용과 스트레스', page_icon='📱', layout='wide')

DATA_FILE = Path(__file__).parent / 'data' / 'official_2025_gender_summary.csv'
REQUIRED_COLUMNS = ['성별', '평일 스마트폰 사용시간(분)', '스트레스 인지율(%)']

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

def add_labels(fig, show_labels, digits=1):
    if show_labels:
        fig.update_traces(texttemplate=f'%{{y:.{digits}f}}', textposition='outside')
    else:
        fig.update_traces(text=None)
    return fig

# -------------------- 데이터 --------------------
try:
    base_df = load_data()
except FileNotFoundError:
    st.error(f'{DATA_FILE} 파일이 app.py와 같은 폴더에 있어야 합니다.')
    st.stop()

st.sidebar.header('⚙️ 시각화 설정')
uploaded = st.sidebar.file_uploader('같은 형식의 CSV로 바꾸기', type=['csv'])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.sidebar.error('필요한 열이 없습니다: ' + ', '.join(missing))
        df = base_df.copy()
    else:
        st.sidebar.success('업로드한 CSV를 사용 중입니다.')
else:
    df = base_df.copy()

metrics = {
    '평일 스마트폰 사용시간(분)': '스마트폰 사용시간',
    '스트레스 인지율(%)': '스트레스 인지율',
}
selected_metrics = st.sidebar.multiselect('비교할 지표', list(metrics), default=list(metrics))
chart_type = st.sidebar.selectbox('그래프 종류', ['나란히 막대그래프', '가로 막대그래프', '상대 점수 그래프', '레이더 그래프', '선그래프', '자료표'])
sort_by = st.sidebar.selectbox('정렬 기준', ['원래 순서'] + selected_metrics)
order = df['성별'].astype(str).tolist()
if sort_by != '원래 순서':
    order = df.sort_values(sort_by, ascending=False)['성별'].astype(str).tolist()
display_df = df.set_index('성별').loc[order].reset_index()
show_labels = st.sidebar.checkbox('막대 위에 수치 표시', True)
height = st.sidebar.slider('그래프 높이', 350, 800, 520, 50)

st.title('📱 청소년 스마트폰 사용과 스트레스')
st.subheader('스마트폰을 많이 사용하는 학생일수록 스트레스도 높을까?')
st.warning('공개 요약 통계에는 SNS만의 사용시간이 따로 없어, SNS를 포함할 수 있는 전체 스마트폰 사용시간과 스트레스 인지율을 비교합니다. 이 자료만으로 원인과 결과를 판단할 수는 없습니다.')

if not selected_metrics:
    st.info('왼쪽에서 비교할 지표를 하나 이상 선택해 주세요.')
    st.stop()

# -------------------- 요약 카드 --------------------
card_cols = st.columns(min(4, len(selected_metrics) + 1))
card_cols[0].metric('비교 집단 수', f'{len(display_df)}개')
for i, col in enumerate(selected_metrics, start=1):
    best = display_df.loc[display_df[col].idxmax()]
    unit = '분' if '시간' in col else '%'
    if i < len(card_cols):
        card_cols[i].metric(metrics[col] + ' 1위', best['성별'], f"{best[col]:.1f}{unit}")

st.header('📊 선택한 그래프')

# -------------------- 그래프 --------------------
if chart_type == '자료표':
    st.dataframe(display_df, use_container_width=True, hide_index=True)

elif chart_type == '나란히 막대그래프':
    long = display_df.melt(id_vars='성별', value_vars=selected_metrics, var_name='지표', value_name='값')
    long['지표'] = long['지표'].map(metrics)
    fig = px.bar(long, x='성별', y='값', color='지표', barmode='group', text='값',
                 labels={'성별': '', '값': '원래 값', '지표': ''}, height=height,
                 color_discrete_sequence=['#4f86f7', '#f28e2b'])
    if show_labels:
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    else:
        fig.update_traces(text=None)
    fig.update_layout(legend=dict(orientation='h', y=1.08, x=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption('두 지표의 단위가 다르므로 사용시간은 분, 스트레스는 %입니다. 크기 자체를 직접 비교하기보다 집단별 순서를 비교하세요.')

elif chart_type == '가로 막대그래프':
    long = display_df.melt(id_vars='성별', value_vars=selected_metrics, var_name='지표', value_name='값')
    long['지표'] = long['지표'].map(metrics)
    fig = px.bar(long, x='값', y='성별', color='지표', barmode='group', orientation='h', text='값',
                 labels={'성별': '', '값': '원래 값', '지표': ''}, height=height,
                 color_discrete_sequence=['#4f86f7', '#f28e2b'])
    if show_labels:
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    else:
        fig.update_traces(text=None)
    fig.update_layout(legend=dict(orientation='h', y=1.08, x=0))
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == '상대 점수 그래프':
    score = display_df[['성별'] + selected_metrics].copy()
    for col in selected_metrics:
        score[metrics[col]] = score[col] / score[col].max() * 100
    long = score.melt(id_vars='성별', value_vars=[metrics[c] for c in selected_metrics], var_name='지표', value_name='비교 점수')
    fig = px.bar(long, x='성별', y='비교 점수', color='지표', barmode='group', text='비교 점수', height=height,
                 labels={'성별': '', '비교 점수': '비교 점수 (최고값=100)', '지표': ''},
                 color_discrete_sequence=['#4f86f7', '#f28e2b'])
    if show_labels:
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    else:
        fig.update_traces(text=None)
    fig.update_layout(yaxis_range=[0, 120], legend=dict(orientation='h', y=1.08, x=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption('각 지표의 가장 큰 값을 100으로 바꾼 비교용 점수입니다. 실제 분·%가 아닙니다.')

elif chart_type == '레이더 그래프':
    if len(selected_metrics) < 2:
        st.info('레이더 그래프는 지표를 2개 이상 선택해야 합니다.')
    else:
        fig = go.Figure()
        for _, row in display_df.iterrows():
            values = [row[col] / display_df[col].max() * 100 for col in selected_metrics]
            fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=[metrics[c] for c in selected_metrics] + [metrics[selected_metrics[0]]], fill='toself', name=str(row['성별'])))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=height, title='지표별 상대 크기 레이더 비교')
        st.plotly_chart(fig, use_container_width=True)
        st.caption('각 지표의 최고값을 100으로 정규화한 그래프입니다.')

elif chart_type == '선그래프':
    long = display_df.melt(id_vars='성별', value_vars=selected_metrics, var_name='지표', value_name='값')
    long['지표'] = long['지표'].map(metrics)
    fig = px.line(long, x='성별', y='값', color='지표', markers=True, height=height,
                  labels={'성별': '비교 집단', '값': '원래 값', '지표': ''})
    st.plotly_chart(fig, use_container_width=True)
    st.caption('현재 자료는 성별 2개 집단 비교이므로 선의 기울기는 참고용으로만 해석하세요.')

# -------------------- 세부 탐색 --------------------
st.header('🔍 세부 탐색')
with st.expander('수치와 차이 계산 보기'):
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    if len(display_df) >= 2:
        a, b = display_df.iloc[0], display_df.iloc[1]
        st.write(f"첫 번째와 두 번째 집단의 차이: **{a['성별']}**와 **{b['성별']}**")
        for col in selected_metrics:
            st.write(f"- {metrics[col]}: {a[col] - b[col]:+.1f}")

with st.expander('📌 해석할 때 주의할 점'):
    st.markdown('''
- 이 자료는 성별별 평균값이므로, 같은 학생의 스마트폰 사용시간과 스트레스 응답을 직접 연결한 자료가 아닙니다.
- 따라서 스마트폰 사용이 스트레스의 원인이라고 결론 내릴 수 없습니다.
- SNS만의 사용시간을 분석하려면 질병관리청 원시자료에서 SNS 관련 문항을 확인하고 학생 개인 단위로 교차분석해야 합니다.
''')

with st.expander('📚 공식 출처'):
    st.markdown('''
- [질병관리청 청소년건강행태조사](https://www.kdca.go.kr/yhs/yhshmpg/main.do)
- [제21차 2025년 청소년건강행태조사 원시자료 공개 안내](https://www.kdca.go.kr/bbs/kdca/42/304276/download.do)

2025년 공개 주요 수치: 평일 스마트폰 사용시간 남학생 253.9분·여학생 293.2분, 스트레스 인지율 남학생 32.9%·여학생 50.3%.
''')

st.download_button('⬇️ 현재 데이터 CSV 다운로드', df.to_csv(index=False).encode('utf-8-sig'), 'official_2025_gender_summary.csv', 'text/csv')
