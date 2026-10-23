import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title='청소년 스마트폰·스트레스 대시보드',
    page_icon='📱',
    layout='wide',
    initial_sidebar_state='expanded',
)

DATA = Path(__file__).parent / 'data'

@st.cache_data
def read(name):
    return pd.read_csv(DATA / name)

# 2025년 질병관리청 원시자료에서 집계한 공식 분석 결과
sex2025 = read('official_2025_gender_summary.csv')
korea_trends = read('korea_stress_trend_2016_2025.csv')
korea_school = read('korea_stress_school_gender_2025.csv')
causes2023 = read('korea_stress_causes_2023.csv')
rel_week = read('smartphone_stress_주중_overall.csv')
rel_week_groups = read('smartphone_stress_주중_groups.csv')
rel_weekend = read('smartphone_stress_주말_overall.csv')
rel_weekend_groups = read('smartphone_stress_주말_groups.csv')

# 색상
BLUE = '#4F86F7'
ORANGE = '#F28E2B'
RED = '#D9534F'
NAVY = '#183B56'

st.markdown('''
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
.dashboard-title {font-size: 2.4rem; font-weight: 800; color: #183B56; margin-bottom: .2rem;}
.dashboard-subtitle {font-size: 1.1rem; color: #607080; margin-bottom: 1.2rem;}
.question-box {background: linear-gradient(135deg,#eef5ff,#fff7ed); border-left: 5px solid #4F86F7; padding: 1rem 1.2rem; border-radius: 0 12px 12px 0; margin: 1rem 0 1.4rem;}
.small-note {color:#667085; font-size:.9rem;}
</style>
''', unsafe_allow_html=True)

# 공통 그래프 함수
def add_text(fig, enabled=True):
    if enabled:
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    else:
        fig.update_traces(text=None)
    return fig

# 사이드바
st.sidebar.title('📱 분석 메뉴')
page = st.sidebar.radio(
    '이동하기',
    ['메인 대시보드', '성별 비교', '학교급 비교', '주중·주말 비교', '스트레스 원인', '자료 출처'],
)
show_text = st.sidebar.checkbox('그래프에 수치 표시', True)
height = st.sidebar.slider('그래프 높이', 360, 700, 500, 20)
st.sidebar.divider()
st.sidebar.caption('자료: 질병관리청 제21차(2025년) 청소년건강행태조사')

if page == '메인 대시보드':
    st.markdown('<div class="dashboard-title">청소년 스마트폰 사용과 스트레스</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">2025년 청소년건강행태조사 원시자료 기반 탐색 대시보드</div>', unsafe_allow_html=True)
    st.markdown('''<div class="question-box"><b>핵심 질문</b><br>스마트폰을 많이 사용하는 학생일수록 높은 스트레스를 느끼는 비율도 높을까?</div>''', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('분석 학생 수', '54,170명')
    k2.metric('전체 높은 스트레스', '41.1%')
    k3.metric('주중 1~3시간 사용', '36.2%')
    k4.metric('주중 8시간 이상 사용', '52.4%', delta='+16.2%p')

    st.subheader('핵심 결과: 스마트폰 사용시간별 높은 스트레스 비율')
    main_period = st.radio('사용시간 기준', ['주중', '주말', '주중·주말 함께 보기'], horizontal=True)
    if main_period == '주중':
        main_rel = rel_week.assign(기간='주중')
    elif main_period == '주말':
        main_rel = rel_weekend.assign(기간='주말')
    else:
        main_rel = pd.concat([rel_week.assign(기간='주중'), rel_weekend.assign(기간='주말')], ignore_index=True)
    fig = px.bar(
        main_rel, x='사용시간구간', y='높은스트레스비율(%)',
        color='기간' if main_period == '주중·주말 함께 보기' else '높은스트레스비율(%)', color_continuous_scale='Oranges',
        text='높은스트레스비율(%)', height=height,
        labels={'사용시간구간':'스마트폰 사용시간', '높은스트레스비율(%)':'높은 스트레스 비율(%)', '기간':''},
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=30,b=20,l=20,r=20))
    add_text(fig, show_text)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.subheader('사용시간과 스트레스 비율의 흐름')
        scatter = px.scatter(
            main_rel, x='평균사용시간(분)', y='높은스트레스비율(%)',
            size='학생수(응답자)', text='사용시간구간',
            color='기간' if main_period == '주중·주말 함께 보기' else '높은스트레스비율(%)', color_continuous_scale='Oranges',
            height=420,
            labels={'평균사용시간(분)':'평균 스마트폰 사용시간(분)', '높은스트레스비율(%)':'높은 스트레스 비율(%)'},
        )
        scatter.update_traces(textposition='top center')
        scatter.update_layout(coloraxis_showscale=False, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(scatter, use_container_width=True)
    with c2:
        st.subheader('핵심 해석')
        st.markdown('''
        **3시간 이상 사용 구간부터** 높은 스트레스 비율이 전반적으로 높아지는 경향이 나타났어.

        특히 **8시간 이상 사용 집단은 52.4%**로, 1~3시간 사용 집단의 36.2%보다 **16.2%p 높아**.

        하지만 이 결과만으로 스마트폰 사용이 스트레스의 원인이라고 단정할 수는 없어. 스트레스가 높은 학생이 스마트폰을 더 많이 사용하는 경우도 가능해.
        ''')
        st.info('이 대시보드는 원인·결과가 아니라 두 지표의 관계를 탐색하는 자료야.')

    st.subheader('분석 기준')
    columns = ['사용시간구간','학생수(응답자)','평균사용시간(분)','높은스트레스비율(%)']
    if main_period == '주중·주말 함께 보기': columns.append('기간')
    st.dataframe(main_rel[columns], use_container_width=True, hide_index=True)

elif page == '성별 비교':
    st.title('성별 비교')
    st.caption('스마트폰 사용시간과 스트레스 인지율의 성별 평균을 비교합니다.')
    long = sex2025.melt(id_vars='성별', value_vars=['평일 스마트폰 사용시간(분)', '스트레스 인지율(%)'], var_name='지표', value_name='값')
    chart = st.selectbox('그래프 종류', ['나란히 막대그래프', '가로 막대그래프'])
    horizontal = chart == '가로 막대그래프'
    fig = px.bar(long, x='값' if horizontal else '성별', y='성별' if horizontal else '값', color='지표', barmode='group', orientation='h' if horizontal else 'v', text='값', height=height, color_discrete_sequence=[BLUE, ORANGE], labels={'값':'값','성별':'','지표':''})
    if show_text: fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    else: fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sex2025, use_container_width=True, hide_index=True)

elif page == '학교급 비교':
    st.title('2025년 학교급·성별 비교')
    chart = st.radio('그래프 종류', ['막대그래프', '히트맵'], horizontal=True)
    if chart == '막대그래프':
        fig = px.bar(korea_school, x='학교급', y='스트레스 인지율(%)', color='성별', barmode='group', text='스트레스 인지율(%)', height=height)
        if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        else: fig.update_traces(text=None)
    else:
        heat = korea_school.pivot(index='성별', columns='학교급', values='스트레스 인지율(%)')
        fig = px.imshow(heat, text_auto='.1f', color_continuous_scale='Reds', aspect='auto', height=height, labels={'color':'스트레스 인지율(%)'})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(korea_school, use_container_width=True, hide_index=True)

elif page == '주중·주말 비교':
    st.title('주중·주말 스마트폰 사용시간 비교')
    st.caption('주중과 주말의 사용시간 구간별 높은 스트레스 비율을 비교합니다.')
    w = rel_week[['사용시간구간','높은스트레스비율(%)']].assign(기간='주중')
    e = rel_weekend[['사용시간구간','높은스트레스비율(%)']].assign(기간='주말')
    compare = pd.concat([w, e], ignore_index=True)
    fig = px.line(compare, x='사용시간구간', y='높은스트레스비율(%)', color='기간', markers=True, text='높은스트레스비율(%)', height=height, color_discrete_sequence=[BLUE, ORANGE], labels={'사용시간구간':'스마트폰 사용시간','높은스트레스비율(%)':'높은 스트레스 비율(%)','기간':''})
    if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='top center')
    else: fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(compare, use_container_width=True, hide_index=True)

elif page == '스트레스 원인':
    st.title('2023년 스트레스 원인 요약')
    st.caption('2025년 공식 요약자료에는 스트레스 원인별 상세표가 확인되지 않아, 확인 가능한 최신 2023년 요약자료를 사용합니다.')
    fig = px.bar(causes2023, x='학교급', y='비율(%)', color='학교급', text='비율(%)', height=height, labels={'학교급':'','비율(%)':'비율(%)'}, color_discrete_sequence=[BLUE, ORANGE])
    if show_text: fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    else: fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(causes2023, use_container_width=True, hide_index=True)
    st.info('중학생은 학업, 고등학생은 성적·진로 부담이 가장 큰 스트레스 원인으로 나타났습니다.')

else:
    st.title('자료 출처와 해석 주의사항')
    st.markdown('''
    **주요 출처**

    - [질병관리청 청소년건강행태조사](https://www.kdca.go.kr/yhs/yhshmpg/main.do)
    - [2025년 청소년건강행태조사 주요결과](https://www.kdca.go.kr/bbs/kdca/41/215505/artclView.do?layout=unknown)
    - [교육정책네트워크 2023년 정신건강 통계](https://edpolicy.kedi.re.kr/edpolicy/webzine/42/842878)

    **해석할 때 주의할 점**

    이 대시보드는 2025년 원시자료에서 같은 학생의 스마트폰 사용시간과 스트레스 응답을 연결해 집계한 결과야. 따라서 성별 평균만 비교할 때보다 관계를 더 직접적으로 볼 수 있지만, 관찰자료이므로 스마트폰 사용이 스트레스의 원인이라고 단정할 수는 없어.

    또한 2025년 공식 요약자료에는 성적·진로·친구관계 등 스트레스 원인별 상세표가 확인되지 않아, 원인 분석은 2023년 요약자료만 사용했어.
    ''')
    st.download_button('⬇️ 관계 분석 집계 CSV 다운로드', rel_week.to_csv(index=False).encode('utf-8-sig'), 'smartphone_stress_relationship.csv', 'text/csv')
