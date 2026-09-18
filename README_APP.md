# 직업별 AI 사용량 앱

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

`app.py`와 `global_occupation_ai_usage.csv`는 같은 폴더에 있어야 합니다.

## 데이터 의미

AI 사용 비율은 전체 Claude 사용 중 해당 직업으로 분류된 사용이 차지하는 비율입니다. 해당 직업 종사자 중 AI를 사용한 사람의 비율은 아닙니다.

출처: Anthropic Economic Index, CC-BY 4.0
