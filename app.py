import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='학생 생활과 스트레스 데이터 탐색', page_icon='📊', layout='wide')
BASE = Path(__file__).parent
SUMMARY_FILE = BASE / 'data' / 'official_2025_gender_summary.csv'

@st.cache_data
def load_summary():
    return pd.read_csv(SUMMARY_FILE)

def numeric_columns(data):
    return data.select_dtypes(include='number').columns.tolist()

def categorical_columns(data):
    return [c for c in data.columns if data[c].nunique(dropna=True) <= min(100, max(10, len(data) // 2))]

def fmt(v):
    return f'{v:,.1f}' if isinstance(v, float) else f'{v:,}'

st.title('📊 학생 생활과 스트레스 데이터 탐색')
st.markdown('''
**지역·학교급·성별·스트레스 요인**을 직접 선택해 여러 그래프로 비교하는 앱입니다.

현재 기본 데이터는 질병관리청의 2025년 공개 요약 통계입니다. 더 자세한 구별·학군별·학생 개인별 분석을 하려면 공식 원시자료 CSV를 왼쪽에서 업로드하세요.
''')
st.warning('기본 요약 데이터에는 남학생·여학생 2개 행만 있습니다. 따라서 기본 상태에서는 구별·학군별 결과를 만들 수 없습니다. 구별 결과를 임의로 만들지 않도록 원시자료 업로드 방식을 사용합니다.')

# -------------------- 데이터 선택 --------------------
st.sidebar.header('1. 데이터 선택')
uploaded = st.sidebar.file_uploader('원시자료 또는 분석용 CSV 업로드', type=['csv', 'txt'])
if uploaded is None:
    df = load_summary()
    using_raw = False
    st.sidebar.info('현재 기본 데이터: 2025년 성별 요약 통계')
else:
    try:
        df = pd.read_csv(uploaded, low_memory=False)
        using_raw = True
        st.sidebar.success(f'업로드 완료: {len(df):,}행')
    except Exception as e:
        st.error(f'CSV를 읽을 수 없습니다: {e}')
        st.stop()

if df.empty:
    st.error('데이터에 행이 없습니다.')
    st.stop()

# -------------------- 원시자료 분석 모드 --------------------
if using_raw:
    st.header('① 원시자료 분석 설정')
    all_cols = df.columns.tolist()
    nums = numeric_columns(df)
    cats = categorical_columns(df)
    if not nums:
        st.error('숫자로 인식되는 열이 없습니다. 원시자료를 숫자형 CSV로 변환해 주세요.')
        st.stop()

    c1, c2, c3 = st.columns(3)
    with c1:
        group_col = st.selectbox('비교할 집단 열', cats or all_cols, help='예: 지역, 학교급, 성별, 학년')
    with c2:
        value_col = st.selectbox('분석할 숫자 열', nums, help='예: 스트레스 점수, 스마트폰 사용시간')
    with c3:
        chart = st.selectbox('그래프 선택', ['집단별 평균 막대그래프', '집단별 분포 상자그림', '집단별 비율 그래프', '두 숫자 열 산점도', '집단별 히트맵', '원자료 표'])

    clean = df[[group_col, value_col] + [c for c in nums if c != value_col]].copy()
    clean = clean.dropna(subset=[group_col, value_col])
    clean[group_col] = clean[group_col].astype(str)
    if len(clean) == 0:
        st.error('선택한 열에 분석할 값이 없습니다.')
        st.stop()

    if chart == '집단별 평균 막대그래프':
        result = clean.groupby(group_col, as_index=False)[value_col].agg(['mean', 'count']).reset_index()
        result.columns = [group_col, '평균', '응답 수']
        result = result.sort_values('평균', ascending=False)
        fig = px.bar(result, x=group_col, y='평균', text='평균', color='평균', color_continuous_scale='Blues',
                     labels={group_col: '', '평균': f'{value_col} 평균'}, title=f'{group_col}별 {value_col} 평균')
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(result, use_container_width=True, hide_index=True)

    elif chart == '집단별 분포 상자그림':
        fig = px.box(clean, x=group_col, y=value_col, color=group_col, points='outliers',
                     labels={group_col: '', value_col: value_col}, title=f'{group_col}별 {value_col} 분포')
        st.plotly_chart(fig, use_container_width=True)
        st.caption('상자그림은 평균만 보지 않고 학생들의 값이 어느 범위에 모여 있는지 보여줍니다.')

    elif chart == '집단별 비율 그래프':
        threshold = st.number_input('높다고 볼 기준값', value=float(clean[value_col].median()))
        rate = clean.assign(기준초과=clean[value_col] >= threshold).groupby(group_col)['기준초과'].mean().mul(100).reset_index(name='기준 이상 비율(%)')
        rate = rate.sort_values('기준 이상 비율(%)', ascending=False)
        fig = px.bar(rate, x=group_col, y='기준 이상 비율(%)', text='기준 이상 비율(%)', color='기준 이상 비율(%)',
                     color_continuous_scale='Oranges', labels={group_col: ''}, title=f'{group_col}별 기준 이상 학생 비율')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.write(f'기준값: **{threshold:.2f}**')

    elif chart == '두 숫자 열 산점도':
        y_candidates = [c for c in nums if c != value_col]
        if not y_candidates:
            st.info('산점도를 만들려면 숫자형 열이 2개 이상 필요합니다.')
        else:
            y_col = st.selectbox('세로축 숫자 열', y_candidates)
            scatter = df[[group_col, value_col, y_col]].dropna().copy()
            scatter[group_col] = scatter[group_col].astype(str)
            fig = px.scatter(scatter, x=value_col, y=y_col, color=group_col, hover_data=[group_col],
                             labels={group_col: '', value_col: value_col, y_col: y_col},
                             title=f'{value_col}과 {y_col}의 관계')
            st.plotly_chart(fig, use_container_width=True)
            st.info(f'상관계수: **{scatter[value_col].corr(scatter[y_col]):.3f}** (인과관계를 뜻하지 않음)')

    elif chart == '집단별 히트맵':
        second_group = st.selectbox('세로로 나눌 두 번째 집단 열', [c for c in cats if c != group_col] or [group_col])
        heat = df[[group_col, second_group, value_col]].dropna().pivot_table(index=second_group, columns=group_col, values=value_col, aggfunc='mean')
        fig = px.imshow(heat, text_auto='.2f', aspect='auto', color_continuous_scale='Blues', title='두 집단별 평균 히트맵')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(heat, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button('⬇️ 업로드 자료 다운로드', df.to_csv(index=False).encode('utf-8-sig'), 'uploaded_data.csv', 'text/csv')
    st.markdown('''
#### 원시자료에서 찾아볼 수 있는 분석 예시

- 지역 또는 학교 소재지별 스트레스 평균
- 중학교·고등학교별 스트레스 비율
- 성별·학교급별 스트레스 차이
- 스트레스가 높은 학생의 스마트폰 사용시간 비교
- 수면시간, 학업 부담, 가족관계 등 요인과 스트레스의 관계
''')

# -------------------- 기본 요약 모드 --------------------
else:
    st.header('① 기본 공개 요약 통계')
    st.info('기본 파일은 성별별 평균만 포함합니다. 왼쪽에 원시자료 CSV를 업로드하면 지역·학교급·요인 분석 메뉴가 열립니다.')
    metric_cols = [c for c in df.columns if c not in ['성별', '출처연도']]
    selected = st.multiselect('표시할 지표', metric_cols, default=metric_cols)
    chart = st.selectbox('그래프 선택', ['나란히 막대그래프', '가로 막대그래프', '레이더 그래프', '자료표'])
    show_text = st.checkbox('그래프에 수치 표시', True)
    height = st.slider('그래프 높이', 350, 800, 520, 50)

    if selected:
        if chart == '자료표':
            st.dataframe(df, use_container_width=True, hide_index=True)
        elif chart == '레이더 그래프':
            score = df.copy()
            for col in selected:
                score[col] = score[col] / score[col].max() * 100
            fig = go.Figure()
            for _, row in score.iterrows():
                values = [row[col] for col in selected]
                fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=selected + [selected[0]], fill='toself', name=row['성별']))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=height, title='지표별 상대 크기 레이더 비교')
            st.plotly_chart(fig, use_container_width=True)
        else:
            long = df.melt(id_vars='성별', value_vars=selected, var_name='지표', value_name='값')
            fig = px.bar(long, x='성별' if chart == '나란히 막대그래프' else '값', y='값' if chart == '나란히 막대그래프' else '성별',
                         color='지표', barmode='group', orientation='v' if chart == '나란히 막대그래프' else 'h', text='값', height=height,
                         labels={'성별': '', '값': '값', '지표': ''}, color_discrete_sequence=['#4f86f7', '#f28e2b'])
            if show_text:
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            else:
                fig.update_traces(text=None)
            fig.update_layout(legend=dict(orientation='h', y=1.08, x=0))
            st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

with st.expander('📌 데이터의 한계와 올바른 해석'):
    st.markdown('''
- 현재 기본 데이터는 남학생·여학생 2개 집단의 평균값입니다. 구별·학군별 결과가 아닙니다.
- 질병관리청 청소년건강행태조사 원시자료를 공식 절차로 내려받아야 학생 개인 단위 분석이 가능합니다.
- 구 단위 표본 수가 충분하지 않으면 학군별 비교 결과가 불안정할 수 있습니다.
- 상관관계가 나와도 한 요인이 다른 요인의 원인이라고 단정할 수 없습니다.
''')

with st.expander('📚 공식 출처'):
    st.markdown('''
- [질병관리청 청소년건강행태조사](https://www.kdca.go.kr/yhs/yhshmpg/main.do)
- [제21차 2025년 원시자료 공개 안내](https://www.kdca.go.kr/bbs/kdca/42/304276/download.do)
- [KOSIS 시·군·구별 스트레스 인지율](https://kosis.kr/statHtml/statHtml.do?sso=ok&returnurl=https%3A%2F%2Fkosis.kr%3A443%2FstatHtml%2FstatHtml.do%3FtblId%3DDT_H_MENTAL_STRESS%26co%3D%26orgId%3D177%26)
''')
