<template>
  <div>
    <h1><img src="../public/logo.png" alt="">SESSAC 커밋 잔디</h1>

    <div v-if="isLoading" class="loading">
      데이터 로딩 중...
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="!isLoading && !error" class="container">
      <div v-for="(repo, repoName) in commitData" :key="repoName" class="repo-section">
        <div class="repo-header">
          <h3>{{ repoName }}</h3>
          <div class="commit-summary">
            <span class="commit-lastDay">
              어제: <strong>{{ repo.lastDayCommits }}</strong> 커밋
            </span>
          </div>
        </div>
        <!-- SESAC 테마에 맞는 range-color로 수정 -->
        <calendar-heatmap :values="repo.values" :end-date="endDate" tooltip-unit="commits" :round="2" :range-color="[
          '#f0f0f0',
          '#e8f5e4',
          '#d9f0cf',
          '#c7e9b8',
          '#b3e3a1',
          '#9ddc88',
          '#86d46e',
          '#6fcb54',
          '#54b33c',
          '#3a9d49',
          '#006432'
        ]" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { CalendarHeatmap } from 'vue3-calendar-heatmap';

// 1. 상태 변수
const commitData = ref({});
const isLoading = ref(true);
const error = ref(null);
const endDate = ref(new Date(Date.now() - 86400000).toISOString().split('T')[0]); // 어제 날짜
const lastDayFormatted = ref('');

// 2. 마운트 시 데이터 로드
onMounted(async () => {
  // (신규) 어제 날짜 포맷팅
  const now = new Date();
  lastDayFormatted.value = `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${now.getDate()}일 기준`;

  try {
    // GitHub API가 아닌, 우리 앱과 함께 배포된 public/commits.json을 로드
    const response = await axios.get('./commits.json');
    const rawData = response.data;
    const lastDayString = endDate.value; // YYYY-MM-DD 형식의 어제 날짜

    if (Object.keys(rawData).length === 0) {
      error.value = '표시할 커밋 데이터가 없습니다.';
      commitData.value = {};
    } else {
      // (신규) 각 레포의 연간 총 커밋, 어제 커밋 계산
      for (const repoName in rawData) {
        const repo = rawData[repoName];

        if (repo.values && Array.isArray(repo.values)) {
          // 1. 지난 1년 총 커밋 수 계산
          const total = repo.values.reduce((acc, val) => acc + (val.count || 0), 0);
          repo.totalYearlyCommits = total;

          // 2. 어제 커밋 수 계산
          const lastDayData = repo.values.find(v => v.date === lastDayString);
          repo.lastDayCommits = lastDayData ? lastDayData.count : 0;
        } else {
          // 데이터가 비정상적일 경우 0으로 초기화
          repo.totalYearlyCommits = 0;
          repo.lastDayCommits = 0;
        }
      }
      commitData.value = rawData;
    }

  } catch (err) {
    console.error('데이터 로드 실패:', err);
    error.value = '커밋 데이터를 불러오는 데 실패했습니다.';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style>
/* 1. 전역 설정: SESAC 테마 색상 및 폰트 정의 */
:root {
  /* SESAC 메인 색상 */
  --sesac-primary-green: #006432;
  --sesac-accent-green: #7DC242;

  /* 기본 UI 색상 */
  --color-text: #333333;
  /* 더 선명한 텍스트 색상 */
  --color-bg: #ffffff;
  /* 흰색 배경 */
  --color-card-bg: #ffffff;
  --color-border: #e0e0e0;
  /* 연한 회색 경계선 */
  --color-error: #b91c1c;
  --color-loading: var(--sesac-primary-green);
  /* 로딩 색상 */
  --color-repo-title: var(--sesac-primary-green);
  /* 레포 제목 색상 */
}

img {
  width: 3.8rem;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
  color: var(--color-text);
  margin: 0;
  padding: 0;
  line-height: 1.6;
  font-size: 15px;
  background-color: var(--color-bg);
  min-height: 100vh;
}

/* 2. 메인 앱 컨테이너 */
#app {
  max-width: 1000px;
  margin: 40px auto;
  padding: 20px;
  box-sizing: border-box;
}

/* 3. 헤더 (제목) */
h1 {
  text-align: center;
  font-weight: 800;
  color: var(--sesac-primary-green);
  border-bottom: 3px solid var(--sesac-accent-green);
  padding-bottom: 15px;
  margin-bottom: 10px;
  /* (수정) 날짜와 간격 조절 */
  font-size: 2.5em;
}

/* (신규) 어제 날짜 스타일 */
.lastDay-date {
  text-align: center;
  font-size: 1.1em;
  font-weight: 500;
  color: var(--color-text-light);
  margin-bottom: 40px;
}

/* 4. 로딩 및 에러 상태 */
.loading,
.error {
  text-align: center;
  padding: 60px 20px;
  font-size: 1.1em;
  font-weight: 500;
  border-radius: 12px;
}

.loading {
  color: var(--color-loading);
}

.error {
  color: var(--color-error);
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
}

/* 5. 개별 레포지토리 섹션 (카드 디자인) */
.repo-section {
  margin-bottom: 40px;
  padding: 25px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: var(--color-card-bg);
  overflow-x: auto;
}

/* (신규) 레포 헤더 스타일 (Flexbox) */
.repo-header {
  display: flex;
  justify-content: space-between;
  /* 제목과 요약을 양끝으로 */
  align-items: center;
  /* 세로 중앙 정렬 */
  margin-bottom: 24px;
  flex-wrap: wrap;
  /* 모바일에서 줄바꿈 */
  gap: 10px;
  /* 제목과 요약 사이 최소 간격 */
}

.repo-header h3 {
  margin: 0;
  /* flex 자식이므로 마진 초기화 */
  font-size: 1.5em;
  font-weight: 600;
  color: var(--color-repo-title);
}

/* (신규) 커밋 요약 스타일 */
.commit-summary {
  display: flex;
  flex-direction: column;
  /* 어제/총계 세로 정렬 */
  align-items: flex-end;
  /* 우측 정렬 */
  gap: 4px;
}

.commit-lastDay {
  font-size: 1.1em;
  color: var(--color-text);
}

.commit-lastDay strong {
  color: var(--sesac-accent-green);
  /* 어제 커밋 강조 */
  font-size: 1.2em;
}

.commit-total {
  font-size: 0.9em;
  color: var(--color-text-light);
}


/* 6. vue-calendar-heatmap 라이브러리 스타일 오버라이드 */
.repo-section .vch__container {
  margin: 0 auto;
}

.vch__legend {
  display: flex;
  justify-content: right;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

text.vch__month__label {
  font-size: 12px;
}

text.vch__day__label {
  font-size: 10px;
}

@media (max-width: 600px) {

  #app {
    margin: 20px auto;
    padding: 15px;
  }

  h1 {
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  img {
    width: 2.8rem;
  }

  .repo-section {
    padding: 18px;
    margin-bottom: 28px;
    border-radius: 10px;
  }

  /* 제목 + 요약이 세로로 정렬되도록 */
  .repo-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .repo-header h3 {
    font-size: 1.3rem;
  }

  .commit-summary {
    width: 100%;
    align-items: flex-start;
    margin-top: 6px;
  }

  .commit-lastDay {
    font-size: 1.0rem;
  }

  /* 히트맵이 화면 넘어가도 자연스럽게 스크롤 */
  .repo-section {
    overflow-x: auto;
  }

  /* 월/요일 라벨 크기 축소 */
  text.vch__month__label {
    font-size: 10px;
  }

  text.vch__day__label {
    font-size: 8px;
  }
}

/* 초미니 화면(아이폰 SE 등) */
@media (max-width: 380px) {
  h1 {
    font-size: 1.6rem;
  }
  img {
    width: 2.5rem;
  }
  .repo-header h3 {
    font-size: 1.2rem;
  }
}
</style>