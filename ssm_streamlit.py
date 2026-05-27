#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SUBGUARD / SubSaver
AI 기반 구독 빈곤 예방 시스템 - Streamlit 버전

Streamlit Community Cloud 배포용 파일입니다.
GitHub에 이 파일을 업로드하고 Main file path를 ssm_streamlit.py로 설정하세요.
"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SUBGUARD - 구독 빈곤 예방 시스템",
    page_icon="💳",
    layout="wide"
)

# -----------------------------
# 기본 샘플 데이터
# -----------------------------
DEFAULT_DATA = [
    {"서비스명": "Netflix", "카테고리": "OTT", "월 이용료": 17000, "월 사용 횟수": 3, "중요도": "보통"},
    {"서비스명": "TVING", "카테고리": "OTT", "월 이용료": 13900, "월 사용 횟수": 1, "중요도": "낮음"},
    {"서비스명": "Melon", "카테고리": "음악", "월 이용료": 10900, "월 사용 횟수": 20, "중요도": "높음"},
    {"서비스명": "Coupang Wow", "카테고리": "쇼핑", "월 이용료": 7890, "월 사용 횟수": 8, "중요도": "보통"},
    {"서비스명": "iCloud", "카테고리": "클라우드", "월 이용료": 3300, "월 사용 횟수": 15, "중요도": "높음"},
]

CATEGORIES = ["OTT", "음악", "쇼핑", "클라우드", "게임", "기타"]
IMPORTANCE = ["낮음", "보통", "높음"]

if "subs" not in st.session_state:
    st.session_state.subs = pd.DataFrame(DEFAULT_DATA)


# -----------------------------
# 분석 함수
# -----------------------------
def service_recommendation(row, category_counts):
    price = int(row["월 이용료"])
    usage = int(row["월 사용 횟수"])
    importance = row["중요도"]
    category = row["카테고리"]

    score = 0
    reasons = []

    if price >= 15000:
        score += 25
        reasons.append("월 이용료가 높은 편입니다")
    elif price >= 10000:
        score += 15
        reasons.append("월 이용료가 중간 이상입니다")

    if usage <= 1:
        score += 35
        reasons.append("최근 사용 횟수가 매우 낮습니다")
    elif usage <= 3:
        score += 25
        reasons.append("최근 사용 횟수가 낮습니다")
    elif usage <= 6:
        score += 10
        reasons.append("사용 빈도를 점검할 필요가 있습니다")

    if importance == "낮음":
        score += 25
        reasons.append("사용자 중요도가 낮습니다")
    elif importance == "보통":
        score += 10

    if category_counts.get(category, 0) >= 2:
        score += 15
        reasons.append("같은 카테고리 구독이 중복되어 있습니다")

    score = min(score, 100)

    if score >= 75:
        rec = "해지 추천"
    elif score >= 55:
        rec = "요금제 변경 추천"
    elif score >= 35:
        rec = "사용 빈도 확인 필요"
    else:
        rec = "유지 추천"

    if not reasons:
        reasons.append("사용 빈도와 중요도가 안정적입니다")

    return score, rec, ", ".join(reasons)


def total_risk(df):
    if df.empty:
        return 0

    total_price = df["월 이용료"].sum()
    count = len(df)
    low_usage_count = (df["월 사용 횟수"] <= 3).sum()
    low_importance_count = (df["중요도"] == "낮음").sum()
    duplicated_categories = (df["카테고리"].value_counts() >= 2).sum()

    risk = 0
    risk += min(total_price / 100000 * 35, 35)
    risk += min(count / 8 * 20, 20)
    risk += min(low_usage_count / max(count, 1) * 25, 25)
    risk += min(low_importance_count / max(count, 1) * 10, 10)
    risk += min(duplicated_categories * 5, 10)

    return int(round(min(risk, 100)))


def risk_level(score):
    if score <= 30:
        return "안정"
    if score <= 60:
        return "주의"
    if score <= 80:
        return "위험"
    return "심각"


# -----------------------------
# 화면 구성
# -----------------------------
st.title("💳 SUBGUARD")
st.subheader("AI 기반 구독 빈곤 예방 시스템")
st.write("OTT, 음악, 쇼핑 멤버십 등 자동결제 구독을 분석해 불필요한 고정지출을 줄이도록 돕는 서비스입니다.")

st.divider()

# 입력 영역
with st.sidebar:
    st.header("구독 서비스 추가")
    service_name = st.text_input("서비스명", placeholder="예: Netflix")
    category = st.selectbox("카테고리", CATEGORIES)
    price = st.number_input("월 이용료(원)", min_value=0, step=1000, value=10000)
    usage = st.number_input("한 달 사용 횟수", min_value=0, step=1, value=3)
    importance = st.selectbox("중요도", IMPORTANCE, index=1)

    if st.button("구독 추가", use_container_width=True):
        if service_name.strip() == "":
            st.warning("서비스명을 입력해 주세요.")
        else:
            new_row = pd.DataFrame([{
                "서비스명": service_name.strip(),
                "카테고리": category,
                "월 이용료": int(price),
                "월 사용 횟수": int(usage),
                "중요도": importance
            }])
            st.session_state.subs = pd.concat([st.session_state.subs, new_row], ignore_index=True)
            st.success("구독 서비스가 추가되었습니다.")

    if st.button("샘플 데이터로 초기화", use_container_width=True):
        st.session_state.subs = pd.DataFrame(DEFAULT_DATA)
        st.success("초기화되었습니다.")

    if st.button("전체 삭제", use_container_width=True):
        st.session_state.subs = pd.DataFrame(columns=["서비스명", "카테고리", "월 이용료", "월 사용 횟수", "중요도"])
        st.warning("전체 데이터가 삭제되었습니다.")


df = st.session_state.subs.copy()

if df.empty:
    st.info("왼쪽 사이드바에서 구독 서비스를 추가해 주세요.")
    st.stop()

# 분석 컬럼 추가
category_counts = df["카테고리"].value_counts().to_dict()
analysis = df.apply(lambda row: service_recommendation(row, category_counts), axis=1)
df["위험 점수"] = [x[0] for x in analysis]
df["AI 추천"] = [x[1] for x in analysis]
df["추천 이유"] = [x[2] for x in analysis]

risk = total_risk(df)
level = risk_level(risk)
saving = df[df["AI 추천"].isin(["해지 추천", "요금제 변경 추천"])] ["월 이용료"].sum()

# 대시보드 카드
col1, col2, col3, col4 = st.columns(4)
col1.metric("월 총 구독 지출", f"{df['월 이용료'].sum():,}원")
col2.metric("총 구독 개수", f"{len(df)}개")
col3.metric("절약 가능 금액", f"{saving:,}원")
col4.metric("구독 과소비 위험도", f"{risk}점 / {level}")

st.progress(risk / 100)

if level == "안정":
    st.success("현재 구독 소비는 안정적인 편입니다.")
elif level == "주의":
    st.warning("구독 지출을 점검할 필요가 있습니다.")
elif level == "위험":
    st.error("불필요한 구독이 누적되고 있을 가능성이 높습니다.")
else:
    st.error("구독 빈곤 위험이 심각합니다. 해지 또는 요금제 조정을 적극 검토하세요.")

st.divider()

# 차트
left, right = st.columns(2)

with left:
    st.subheader("카테고리별 월 지출")
    category_price = df.groupby("카테고리")["월 이용료"].sum().sort_values(ascending=False)
    st.bar_chart(category_price)

with right:
    st.subheader("서비스별 위험 점수")
    risk_chart = df.set_index("서비스명")["위험 점수"].sort_values(ascending=False)
    st.bar_chart(risk_chart)

st.divider()

st.subheader("구독 서비스 목록 및 AI 분석 결과")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("AI 추천 요약")
for _, row in df.sort_values("위험 점수", ascending=False).iterrows():
    with st.container(border=True):
        st.markdown(f"### {row['서비스명']} — {row['AI 추천']}")
        st.write(f"카테고리: {row['카테고리']} / 월 이용료: {int(row['월 이용료']):,}원 / 월 사용 횟수: {int(row['월 사용 횟수'])}회 / 중요도: {row['중요도']}")
        st.write(f"추천 이유: {row['추천 이유']}")

st.caption("※ 본 시스템은 실제 금융정보를 연결하지 않는 과제용 시뮬레이션입니다. 사용자가 입력한 구독 데이터에 기반해 위험도를 계산합니다.")
