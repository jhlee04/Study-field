# generate_summary.py
import pandas as pd
import requests
from tqdm import tqdm

# --- 0. 내부 LLaMA API 설정 ---
API_URL = "http://your-internal-api-endpoint"
HEADERS = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}

def query_llama(prompt: str, max_tokens: int = 1024) -> str:
    payload = {
        "model": "llama-3.3-70b-instruct",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["completion"]

# --- 1. 입력 데이터 불러오기 ---
input_df = pd.read_csv('data/report_data.csv')  # 날짜, 팀, 과제명, 보고 내용 포함
input_df = input_df.fillna('')  # NaN 방지

# --- 2. Few-shot 프롬프트 템플릿 ---
few_shot_template = """
당신은 반도체 부서의 주간 회의 보고서를 정리하는 업무를 맡았습니다.
다음은 팀별 회의 보고 내용입니다.
각 항목에 대해 다음과 같이 요약해 주세요:

출력 형식:
- 주차: yyyy-mm-dd 형식
- 팀: 팀 이름
- 과제명: 프로젝트/과제 이름
- Status: 다음 중 하나 선택 (On-track, At-risk, Delayed, Completed)
- 요약: 핵심 진행 상황을 1~2문장으로 정리

---

[예시 1]
보고 내용:
날짜: 2025-03-24
팀: TCAD팀
과제명: Transistor 예측 시스템 구축
내용: 모델 구조를 개선하여 예측 정확도는 0.88까지 향상됨. 기존 대비 학습 시간은 10% 증가. 일부 edge-case에서 성능 저하 관찰됨. 전체 데이터 분포에 대한 추가 분석이 필요. 고정 변수 조건 검토 예정.

→ 출력:
- 주차: 2025-03-24
- 팀: TCAD팀
- 과제명: Transistor 예측 시스템 구축
- Status: At-risk
- 요약: 예측 정확도는 향상되었으나 일부 케이스에서 성능 저하 발생. 추가 분석 및 변수 검토 필요.

---

다음 보고 내용을 위와 같은 형식으로 정리해 주세요:

날짜: {date}
팀: {team}
과제명: {project}
내용: {content}
"""

# --- 3. LLaMA 호출 함수 ---
def summarize_report(date, team, project, content):
    prompt = few_shot_template.format(date=date, team=team, project=project, content=content)
    try:
        result = query_llama(prompt)
        return result
    except Exception as e:
        return f"ERROR: {e}"

# --- 4. 출력 파싱 함수 ---
def parse_summary(result_text):
    result = {"주차": "", "팀": "", "과제명": "", "Status": "", "요약": ""}
    for line in result_text.split('\n'):
        if line.startswith("- 주차:"):
            result["주차"] = line.replace("- 주차:", "").strip()
        elif line.startswith("- 팀:"):
            result["팀"] = line.replace("- 팀:", "").strip()
        elif line.startswith("- 과제명:"):
            result["과제명"] = line.replace("- 과제명:", "").strip()
        elif line.startswith("- Status:"):
            result["Status"] = line.replace("- Status:", "").strip()
        elif line.startswith("- 요약:"):
            result["요약"] = line.replace("- 요약:", "").strip()
    return result

# --- 5. 전체 처리 루프 ---
results = []
for idx, row in tqdm(input_df.iterrows(), total=len(input_df)):
    gpt_output = summarize_report(row['날짜'], row['팀'], row['과제명'], row['보고 내용'])
    parsed = parse_summary(gpt_output)
    results.append(parsed)

# --- 6. 결과 저장 ---
summary_df = pd.DataFrame(results)
summary_df.to_csv('summary_report.csv', index=False)
print("✅ summary_report.csv 생성 완료 (내부 LLaMA API 기반)")
