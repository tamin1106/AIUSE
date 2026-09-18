import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="AI 학습연산량 분석", page_icon="🤖", layout="wide")
CSV_FILE = "ai_models_compute_usable.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df["Publication date"] = pd.to_datetime(df["Publication date"], errors="coerce")
    df["year"] = df["Publication date"].dt.year
    df["Parameters (B)"] = pd.to_numeric(df["Parameters"], errors="coerce") / 1e9
    df["Training compute (EFLOP)"] = pd.to_numeric(df["Training compute (FLOP)"], errors="coerce") / 1e18
    df = df.replace([np.inf, -np.inf], np.nan)
    return df.dropna(subset=["Publication date", "Parameters (B)", "Training compute (EFLOP)"]).copy()

df = load_data()
st.title("🤖 AI 모델의 학습연산량은 시간이 지날수록 증가했을까?")
st.caption("Epoch AI 공식 AI Models 데이터 | 실제 기록·추정이 섞인 학습연산량(FLOP) 데이터")
with st.sidebar:
    st.header("🔍 분석 필터")
    years = st.slider("발표 연도", int(df.year.min()), int(df.year.max()), (int(df.year.min()), int(df.year.max())))
    filtered = df[df.year.between(*years)].copy()
    st.info("학습연산량은 FLOP 단위이며, 데이터에 기록된 값만 사용합니다.")

st.subheader("📌 데이터 요약")
c1,c2,c3,c4=st.columns(4)
c1.metric("분석 모델 수", f"{len(filtered):,}개")
c2.metric("연산량 중앙값", f"{filtered['Training compute (EFLOP)'].median():,.2f} EFLOP")
c3.metric("파라미터 중앙값", f"{filtered['Parameters (B)'].median():,.2f}B")
c4.metric("분석 기간", f"{filtered.year.min()}–{filtered.year.max()}")

yearly = filtered.groupby("year").agg(models=("Model","count"), median_compute=("Training compute (EFLOP)","median"), median_parameters=("Parameters (B)","median")).reset_index()
st.subheader("📈 연도별 학습연산량")
fig=px.line(yearly,x="year",y="median_compute",markers=True,labels={"year":"발표 연도","median_compute":"학습연산량 중앙값 (EFLOP)"},title="연도별 학습연산량 중앙값")
fig.update_yaxes(type="log")
st.plotly_chart(fig,use_container_width=True)

st.subheader("🔗 모델 크기와 학습연산량")
fig=px.scatter(filtered,x="Parameters (B)",y="Training compute (EFLOP)",hover_name="Model",color="year",labels={"Parameters (B)":"파라미터 수 (billion)","Training compute (EFLOP)":"학습연산량 (EFLOP)","year":"발표 연도"},title="파라미터 수와 학습연산량")
fig.update_xaxes(type="log")
fig.update_yaxes(type="log")
st.plotly_chart(fig,use_container_width=True)

corr=filtered["Parameters"].corr(filtered["Training compute (FLOP)"])
st.info(f"피어슨 상관계수: **{corr:.3f}**")
with st.expander(f"📄 데이터 보기 ({len(filtered):,}개 행)"):
    cols=[c for c in ["Model","Publication date","Parameters","Training compute (FLOP)","Training compute estimation method"] if c in filtered.columns]
    st.dataframe(filtered[cols].sort_values("Publication date",ascending=False),use_container_width=True)
with st.expander("📚 출처와 주의점"):
    st.markdown("""**출처:** [Epoch AI – Data on AI Models](https://epoch.ai/data/ai-models)  
**공식 CSV:** [all_ai_models.csv](https://epoch.ai/data/all_ai_models.csv)  
**라이선스:** Creative Commons Attribution 4.0

- `Training compute (FLOP)`는 모델 학습에 사용된 부동소수점 연산량입니다.
- 데이터에는 논문에 직접 보고된 값과 Epoch AI가 방법론에 따라 계산한 값이 함께 포함될 수 있습니다.
- FLOP는 기업의 실제 전기요금이나 금액이 아닙니다.
""")
st.download_button("⬇️ 현재 필터 데이터 CSV 다운로드",filtered.to_csv(index=False).encode("utf-8-sig"),"ai_models_compute_filtered.csv","text/csv")
