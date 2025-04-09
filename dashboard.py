# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="과제 진행 현황 대시보드", layout="wide")

# --- 1. 데이터 불러오기 ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("summary_reviewed.csv")
    except FileNotFoundError:
        return pd.read_csv("summary_report.csv")

df = load_data()
df = df.fillna("")

# --- 2. 필터 설정 (좌측 사이드바) ---
st.sidebar.header("🔎 필터")
selected_weeks = st.sidebar.multiselect("주차 선택", df["주차"].unique(), default=df["주차"].unique())
selected_teams = st.sidebar.multiselect("팀 선택", df["팀"].unique(), default=df["팀"].unique())
selected_status = st.sidebar.multiselect("Status", df["Status"].unique(), default=df["Status"].unique())

# --- 3. 필터 적용 ---
filtered_df = df[
    (df["주차"].isin(selected_weeks)) &
    (df["팀"].isin(selected_teams)) &
    (df["Status"].isin(selected_status))
].copy()

# --- 4. 헤더 요약 정보 ---
st.title("✅ 반도체 과제 주간 대시보드")
st.markdown(f"""
**총 과제 수**: {len(filtered_df)}  
**선택된 팀**: {', '.join(selected_teams)}  
**선택된 주차**: {', '.join(selected_weeks)}  
""")

# --- 5. 상태 분포 차트 (막대 그래프) ---
st.subheader("📊 과제 상태 분포")
status_counts = filtered_df["Status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
fig = px.bar(status_counts, x="Status", y="Count", color="Status", text="Count")
st.plotly_chart(fig, use_container_width=True)

# --- 6. 요약 테이블 표시 ---
st.subheader("📝 과제별 요약 테이블")
st.dataframe(filtered_df, use_container_width=True)

# --- 7. 다운로드 버튼 ---
st.download_button(
    label="📥 필터링된 보고서 다운로드 (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_summary_report.csv",
    mime="text/csv"
)
