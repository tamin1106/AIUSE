import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title='서울 청소년 스트레스 탐색', page_icon='📊', layout='wide')
DATA = Path(__file__).parent / 'data'

@st.cache_data
def read(name):
    return pd.read_csv(DATA / name)

# 공식 자료 불러오기
sex2025 = read('official_2025_gender_summary.csv')
causes2023 = read('korea_stress_causes_2023.csv')
korea_trends = read('korea_stress_trend_2016_2025.csv')
korea_school = read('korea_stress_school_gender_2025.csv')
rel_week = read('smartphone_stress_주중_overall.csv')
rel_week_groups = read('smartphone_stress_주중_groups.csv')
rel_weekend = read('smartphone_stress_주말_overall.csv')
rel_weekend_groups = read('smartphone_stress_주말_groups.csv')

st.title('📊 서울 청소년 스트레스 데이터 탐색')
st.subheader('청소년의 스트레스는 학년·성별·원인에 따라 어떻게 다를까?')
st.info('앱에 공식 공개자료를 내장했기 때문에 CSV 업로드 없이 바로 그래프를 선택할 수 있습니다.')

st.sidebar.header('그래프 선택')
page = st.sidebar.radio('분석 주제', ['핸드폰 사용-스트레스 관계', '2025 성별 비교', '2025 최신 추이', '2025 학교급·성별', '2023 스트레스 원인 요약', '2025 미디어 과의존', '자료 출처'])
height = st.sidebar.slider('그래프 높이', 350, 800, 520, 50)
show_text = st.sidebar.checkbox('그래프에 수치 표시', True)

if page == '핸드폰 사용-스트레스 관계':
    st.header('2025년 스마트폰 사용시간과 스트레스의 관계')
    st.markdown('같은 학생의 스마트폰 사용시간과 스트레스 응답을 연결해 사용시간 구간별 **높은 스트레스 비율**을 계산했습니다.')
    period = st.radio('사용시간 기준', ['주중', '주말'], horizontal=True)
    chart = st.selectbox('그래프 종류', ['사용시간 구간별 스트레스 비율', '집단별 비교', '사용시간-스트레스 산점도'])
    overall = rel_week if period == '주중' else rel_weekend
    groups = rel_week_groups if period == '주중' else rel_weekend_groups
    if chart == '사용시간 구간별 스트레스 비율':
        fig = px.bar(overall, x='사용시간구간', y='높은스트레스비율(%)', text='높은스트레스비율(%)', color='높은스트레스비율(%)', color_continuous_scale='Oranges', height=height, labels={'사용시간구간':'스마트폰 사용시간','높은스트레스비율(%)':'높은 스트레스 비율(%)'})
        if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        else: fig.update_traces(text=None)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(overall, use_container_width=True, hide_index=True)
    elif chart == '집단별 비교':
        dim = st.selectbox('비교 집단', ['성별', '학교급', '학년'])
        d = groups[groups['구분'] == dim]
        selected = st.multiselect('집단 선택', sorted(d['집단값'].dropna().unique()), default=list(sorted(d['집단값'].dropna().unique())))
        d = d[d['집단값'].isin(selected)]
        fig = px.line(d, x='사용시간구간', y='높은스트레스비율(%)', color='집단값', markers=True, height=height, labels={'사용시간구간':'스마트폰 사용시간','높은스트레스비율(%)':'높은 스트레스 비율(%)','집단값':dim})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(d, use_container_width=True, hide_index=True)
    else:
        fig = px.scatter(overall, x='평균사용시간(분)', y='높은스트레스비율(%)', size='학생수(응답자)', text='사용시간구간', height=height, labels={'평균사용시간(분)':'평균 스마트폰 사용시간(분)','높은스트레스비율(%)':'높은 스트레스 비율(%)'})
        st.plotly_chart(fig, use_container_width=True)
        st.caption('추세선은 사용시간 구간별 집계값을 이용한 참고선입니다. 원인·결과를 증명하지 않습니다.')
    st.success('결과 요약: 주중 스마트폰 사용시간이 1시간 미만인 구간의 높은 스트레스 비율은 38.2%, 8시간 이상 구간은 52.4%입니다.')

elif page == '2025 성별 비교':
    st.header('2025년 성별 스마트폰 사용시간과 스트레스')
    chart = st.selectbox('그래프 종류', ['나란히 막대그래프', '가로 막대그래프', '레이더 그래프'])
    long = sex2025.melt(id_vars='성별', value_vars=['평일 스마트폰 사용시간(분)', '스트레스 인지율(%)'], var_name='지표', value_name='값')
    if chart == '레이더 그래프':
        score = sex2025.copy()
        cols = ['평일 스마트폰 사용시간(분)', '스트레스 인지율(%)']
        for c in cols: score[c] = score[c] / score[c].max() * 100
        fig = px.line_polar(score, r='평일 스마트폰 사용시간(분)', theta='성별', line_close=True, markers=True, height=height)
        st.plotly_chart(fig, use_container_width=True)
        st.caption('레이더 그래프는 지표 단위가 달라 비교용으로 정규화한 그래프입니다.')
    else:
        horizontal = chart == '가로 막대그래프'
        fig = px.bar(long, x='값' if horizontal else '성별', y='성별' if horizontal else '값', color='지표', barmode='group', orientation='h' if horizontal else 'v', text='값', height=height, color_discrete_sequence=['#4f86f7','#f28e2b'], labels={'값':'값','성별':'','지표':''})
        if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        else: fig.update_traces(text=None)
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sex2025, use_container_width=True, hide_index=True)

elif page == '2025 최신 추이':
    st.header('2016~2025 전국 청소년 스트레스 인지율')
    fig = px.line(korea_trends, x='연도', y='스트레스 인지율(%)', color='성별', markers=True, text='스트레스 인지율(%)', height=height)
    if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='top center')
    else: fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)
    latest = korea_trends[korea_trends['연도'] == 2025]
    st.dataframe(latest, use_container_width=True, hide_index=True)
    st.caption('질병관리청 제21차 청소년건강행태조사. 2025년 남학생 32.9%, 여학생 50.3%입니다.')

elif page == '2025 학교급·성별':
    st.header('2025년 학교급·성별 스트레스 인지율')
    chart = st.selectbox('그래프 종류', ['막대그래프', '히트맵'])
    if chart == '막대그래프':
        fig = px.bar(korea_school, x='학교급', y='스트레스 인지율(%)', color='성별', barmode='group', text='스트레스 인지율(%)', height=height)
        if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        else: fig.update_traces(text=None)
    else:
        heat = korea_school.pivot(index='성별', columns='학교급', values='스트레스 인지율(%)')
        fig = px.imshow(heat, text_auto='.1f', color_continuous_scale='Reds', aspect='auto', height=height, labels={'color':'스트레스 인지율(%)'})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(korea_school, use_container_width=True, hide_index=True)

elif page == '2023 스트레스 원인 요약':
    st.header('2023년 청소년의 가장 큰 스트레스 원인')
    fig = px.bar(causes2023, x='학교급', y='비율(%)', color='학교급', text='비율(%)', height=height, labels={'학교급':'','비율(%)':'비율(%)'}, color_discrete_sequence=['#4f86f7','#f28e2b'])
    if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    else: fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(causes2023, use_container_width=True, hide_index=True)
    st.caption('2023년 통계에서 중학생은 학업, 고등학생은 성적·진로 부담이 가장 큰 스트레스 원인으로 보고되었습니다. 2025년 공식 요약자료에는 이 원인별 상세표가 확인되지 않았습니다.')

elif page == '2025 미디어 과의존':
    st.header('2025년 청소년 인터넷·스마트폰 과의존 위험군')
    total_media = 1234587
    total_risk = 213243
    risk_rate = total_risk / total_media * 100
    st.metric('전체 참여자 중 위험군 비율', f'{risk_rate:.2f}%')
    st.caption(f'전체 참여자 {total_media:,}명 중 위험군 {total_risk:,}명입니다.')
    rate_df = pd.DataFrame({'구분':['전체 참여자','과의존 위험군'], '비율(%)':[100, risk_rate]})
    rate_fig = px.bar(rate_df, x='구분', y='비율(%)', text='비율(%)', color='구분', height=350, labels={'구분':'','비율(%)':'비율(%)'}, color_discrete_sequence=['#b8c7e8','#f28e2b'])
    rate_fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(rate_fig, use_container_width=True)
    st.subheader('학교급·성별 위험군 인원')
    media = pd.DataFrame({'구분':['초등학생','중학생','고등학생','남자 청소년','여자 청소년'], '위험군 수':[57229,85487,70527,116414,96829]})
    fig = px.bar(media, x='구분', y='위험군 수', text='위험군 수', color='위험군 수', color_continuous_scale='Blues', height=height, labels={'위험군 수':'위험군 인원(명)'})
    if show_text: fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    st.warning('학교급·성별별 분모가 공개 요약자료에 제시되지 않아, 아래 값은 비율이 아닌 위험군 인원입니다. 전체 비율만 17.27%로 계산했습니다.')
    st.caption('여성가족부 2025년 청소년 미디어 이용습관 진단조사. 스트레스 자료와 같은 학생 단위로 연결한 값은 아닙니다.')
    st.dataframe(media, use_container_width=True, hide_index=True)

else:
    st.header('자료 출처와 해석 주의사항')
    st.markdown('''
- [질병관리청 2025년 청소년건강행태조사](https://www.kdca.go.kr/bbs/kdca/41/215505/artclView.do?layout=unknown)
- [교육정책네트워크 2023년 스트레스 원인 요약](https://edpolicy.kedi.re.kr/edpolicy/webzine/42/842878)
- [여성가족부 2025년 청소년 미디어 이용습관 진단조사](https://www.mogef.go.kr/nw/enw/nw_enw_s001d.do?mid=mda700&bbtSn=712710)
- [지표누리 스마트폰 과의존 현황](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=3061)

앱의 관계 분석은 2025년 청소년건강행태조사 원시자료에서 같은 학생의 스마트폰 사용시간과 스트레스 응답을 연결해 만든 집계 결과입니다. 2020년 상세 원인·학년 메뉴는 최신 공식 자료로 대체할 수 없어 삭제했습니다.
''')

st.download_button('⬇️ 2023년 스트레스 원인 요약 다운로드', causes2023.to_csv(index=False).encode('utf-8-sig'), 'korea_stress_causes_2023.csv', 'text/csv')
