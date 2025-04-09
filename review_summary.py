# review_summary.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="과제 요약 리뷰", layout="wide")

# --- 1. 데이터 불러오기 ---
df = pd.read_csv("summary_report.csv")
df = df.fillna("")

# --- 2. 필터 선택 ---
st.sidebar.header("필터 옵션")
team_filter = st.sidebar.multiselect("팀", df["팀"].unique(), default=df["팀"].unique())
status_filter = st.sidebar.multiselect("Status", df["Status"].unique(), default=df["Status"].unique())

filtered_df = df[
    (df["팀"].isin(team_filter)) &
    (df["Status"].isin(status_filter))
].copy()

# --- 3. 코멘트 열 추가 (없으면) ---
if "코멘트" not in filtered_df.columns:
    filtered_df["코멘트"] = ""

st.title("✅ 과제 요약 결과 검토 및 수정")
st.markdown("자동 분류된 과제 상태를 확인하고 필요 시 직접 수정하세요.")

# --- 4. 편집 가능한 테이블 ---
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Status": st.column_config.SelectboxColumn("Status", options=["On-track", "At-risk", "Delayed", "Completed"]),
        "요약": st.column_config.TextColumn("요약", width="medium"),
        "코멘트": st.column_config.TextColumn("코멘트", width="medium")
    }
)

# --- 5. 다운로드 버튼 ---
st.download_button(
    label="📥 수정된 보고서 다운로드 (CSV)",
    data=edited_df.to_csv(index=False),
    file_name="summary_reviewed.csv",
    mime="text/csv"
)
