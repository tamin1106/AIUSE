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
factors = read('seoul_stress_factors_2020.csv')
trends = read('seoul_stress_trends.csv')
grades = read('seoul_grade_stress_2020.csv')

st.title('📊 서울 청소년 스트레스 데이터 탐색')
st.subheader('청소년의 스트레스는 학년·성별·원인에 따라 어떻게 다를까?')
st.info('앱에 공식 공개자료를 내장했기 때문에 CSV 업로드 없이 바로 그래프를 선택할 수 있습니다.')

st.sidebar.header('그래프 선택')
page = st.sidebar.radio('분석 주제', ['2025 성별 비교', '2020 스트레스 원인', '2020 학년·성별 비교', '2015~2020 연도 추이', '2025 미디어 과의존', '자료 출처'])
height = st.sidebar.slider('그래프 높이', 350, 800, 520, 50)
show_text = st.sidebar.checkbox('그래프에 수치 표시', True)

if page == '2025 성별 비교':
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

elif page == '2020 스트레스 원인':
    st.header('2020년 서울 청소년의 스트레스 원인')
    factor_cols = ['성적','외모','부모와 갈등','교우관계','건강문제','가정형편 등']
    view = st.radio('보기 방식', ['학년별 원인 비교', '성별별 원인 평균', '원인 순위'], horizontal=True)
    if view == '학년별 원인 비교':
        gender = st.selectbox('성별', ['남','여','전체'])
        d = factors if gender == '전체' else factors[factors['성별'] == gender]
        long = d.melt(id_vars=['성별','학년'], value_vars=factor_cols, var_name='스트레스 원인', value_name='비율(%)')
        fig = px.bar(long, x='학년', y='비율(%)', color='스트레스 원인', barmode='group', text='비율(%)', height=height, labels={'학년':'','스트레스 원인':''})
        if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        else: fig.update_traces(text=None)
        st.plotly_chart(fig, use_container_width=True)
    elif view == '성별별 원인 평균':
        long = factors.melt(id_vars=['성별','학년'], value_vars=factor_cols, var_name='스트레스 원인', value_name='비율(%)').groupby(['성별','스트레스 원인'], as_index=False)['비율(%)'].mean()
        fig = px.bar(long, x='스트레스 원인', y='비율(%)', color='성별', barmode='group', text='비율(%)', height=height)
        if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        else: fig.update_traces(text=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        avg = factors[factor_cols].mean().sort_values(ascending=False).reset_index()
        avg.columns = ['스트레스 원인','평균 비율(%)']
        fig = px.bar(avg, x='평균 비율(%)', y='스트레스 원인', orientation='h', text='평균 비율(%)', color='평균 비율(%)', color_continuous_scale='Oranges', height=height)
        if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        else: fig.update_traces(text=None)
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(factors, use_container_width=True, hide_index=True)

elif page == '2020 학년·성별 비교':
    st.header('2020년 서울 청소년 학년·성별 스트레스 인지율')
    view = st.radio('그래프 종류', ['막대그래프', '히트맵', '상자그림'], horizontal=True)
    if view == '막대그래프':
        fig = px.bar(grades, x='학년', y='스트레스 인지율(%)', color='성별', barmode='group', text='스트레스 인지율(%)', height=height)
        if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    elif view == '히트맵':
        heat = grades.pivot(index='성별', columns='학년', values='스트레스 인지율(%)')
        fig = px.imshow(heat, text_auto='.1f', color_continuous_scale='Reds', aspect='auto', height=height, labels={'color':'스트레스 인지율(%)'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.box(grades, x='성별', y='스트레스 인지율(%)', color='성별', points='all', height=height)
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(grades, use_container_width=True, hide_index=True)

elif page == '2015~2020 연도 추이':
    st.header('서울과 전국 청소년 스트레스 인지율 추이')
    fig = px.line(trends, x='연도', y='스트레스 인지율(%)', color='지역', markers=True, text='스트레스 인지율(%)', height=height)
    if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(trends, use_container_width=True, hide_index=True)
    st.caption('2020년 자료이며, 코로나19 시기 조사 결과가 포함되어 있습니다.')

elif page == '2025 미디어 과의존':
    st.header('2025년 청소년 인터넷·스마트폰 과의존 위험군')
    media = pd.DataFrame({'구분':['초등학생','중학생','고등학생','남자 청소년','여자 청소년'], '위험군 수':[57229,85487,70527,116414,96829]})
    fig = px.bar(media, x='구분', y='위험군 수', text='위험군 수', color='위험군 수', color_continuous_scale='Blues', height=height)
    if show_text: fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    st.metric('전체 위험군', '213,243명')
    st.caption('여성가족부 2025년 청소년 미디어 이용습관 진단조사. 스트레스 자료와 같은 학생 단위로 연결한 값은 아닙니다.')
    st.dataframe(media, use_container_width=True, hide_index=True)

else:
    st.header('자료 출처와 해석 주의사항')
    st.markdown('''
- [질병관리청 청소년건강행태조사](https://www.kdca.go.kr/yhs/yhshmpg/main.do)
- [서울연구원 2020년 서울 청소년 스트레스 분석](https://www.si.re.kr/node/64986)
- [서울시 청소년 정신건강 통계](https://data.seoul.go.kr/dataList/OA-13516/S/1/datasetView.do)
- [여성가족부 2025년 청소년 미디어 이용습관 진단조사](https://www.mogef.go.kr/nw/enw/nw_enw_s001d.do?mid=mda700&bbtSn=712710)
- [지표누리 스마트폰 과의존 현황](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=3061)

서울연구원 자료는 2020년 질병관리청 청소년건강행태조사 마이크로데이터를 분석한 자료입니다. 자치구별 학생 자료가 아니므로 학군 순위를 만들 수 없습니다. KOSIS의 시·군·구별 스트레스는 일반 지역사회건강조사라 학생 전용 자료와 섞으면 안 됩니다.
''')

st.download_button('⬇️ 현재 화면 자료 다운로드', factors.to_csv(index=False).encode('utf-8-sig'), 'seoul_stress_factors_2020.csv', 'text/csv')
