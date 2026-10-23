# 학생용 Python 시각화 예제
# 실행 전: pip install pandas matplotlib
import pandas as pd
import matplotlib.pyplot as plt

# 한글 글꼴이 없을 때도 그래프가 실행되도록 기본 설정
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('data/official_2025_gender_summary.csv')

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(df['성별'], df['평일 스마트폰 사용시간(분)'], color=['#4f86f7', '#f28e2b'])
axes[0].set_title('성별 평일 스마트폰 사용시간')
axes[0].set_ylabel('분')
for i, value in enumerate(df['평일 스마트폰 사용시간(분)']):
    axes[0].text(i, value + 4, f'{value:.1f}분', ha='center')

axes[1].bar(df['성별'], df['스트레스 인지율(%)'], color=['#4f86f7', '#f28e2b'])
axes[1].set_title('성별 스트레스 인지율')
axes[1].set_ylabel('%')
for i, value in enumerate(df['스트레스 인지율(%)']):
    axes[1].text(i, value + 1, f'{value:.1f}%', ha='center')

plt.suptitle('2025년 청소년 스마트폰 사용과 스트레스 비교')
plt.tight_layout()
plt.savefig('smartphone_stress_comparison.png', dpi=180)
plt.show()

print(df)
print('\n여학생과 남학생의 평일 스마트폰 사용시간 차이:', round(df.loc[1, '평일 스마트폰 사용시간(분)'] - df.loc[0, '평일 스마트폰 사용시간(분)'], 1), '분')
print('여학생과 남학생의 스트레스 인지율 차이:', round(df.loc[1, '스트레스 인지율(%)'] - df.loc[0, '스트레스 인지율(%)'], 1), '%p')
