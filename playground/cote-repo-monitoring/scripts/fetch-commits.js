const { Octokit } = require('@octokit/rest');
const fs = require('fs-extra');
const path = require('path');

// 환경 변수에서 값 가져오기 (GitHub Actions Secret에서 주입됨)
const GITHUB_TOKEN = process.env.MY_GITHUB_PAT;
const ORG_NAME = process.env.ORG_NAME;

if (!GITHUB_TOKEN || !ORG_NAME) {
  console.error('MY_GITHUB_PAT 또는 ORG_NAME 환경 변수가 없습니다.');
  process.exit(1);
}

// Octokit 클라이언트 초기화
const octokit = new Octokit({ auth: GITHUB_TOKEN });

// 최종 JSON 파일이 저장될 경로 (Vue의 public 폴더)
const outputPath = path.resolve(__dirname, '..', 'public', 'commits.json');

// 1년 전 날짜
const oneYearAgo = new Date();
oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

async function main() {
  console.log(`[${ORG_NAME}] 조직의 커밋 데이터 수집을 시작합니다...`);
  const finalData = {};

  try {
    // 1. 조직의 모든 레포 가져오기 (페이징 처리)
    const repos = await octokit.paginate(octokit.repos.listForOrg, {
      org: ORG_NAME,
      type: 'all', // private, public 모두
    });

    console.log(`총 ${repos.length}개의 레포를 찾았습니다.`);

    // 2. 각 레포를 순회하며 커밋 데이터 가져오기
    for (const repo of repos) {
      const repoName = repo.name;
      const dailyCommits = {};

      try {
        // 3. 각 레포의 1년간 커밋 가져오기 (페이징 처리)
        const commits = await octokit.paginate(octokit.repos.listCommits, {
          owner: ORG_NAME,
          repo: repoName,
          since: oneYearAgo.toISOString(),
        });

        if (commits.length === 0) {
          console.log(`[${repoName}] 1년간 커밋이 없습니다. (스킵)`);
          continue;
        }

        // 4. 날짜별로 커밋 횟수 집계
        for (const commit of commits) {
          const commitDate = commit.commit.author.date.split('T')[0];
          dailyCommits[commitDate] = (dailyCommits[commitDate] || 0) + 1;
        }

        // 5. 잔디 라이브러리 형식으로 변환
        const heatmapValues = Object.entries(dailyCommits).map(([date, count]) => {
          return { date, count };
        });

        finalData[repoName] = { values: heatmapValues };
        console.log(`[${repoName}] 데이터 수집 완료 (${commits.length}개 커밋)`);

      } catch (err) {
        // (예: 비어있는 레포 등) 오류 발생 시 스킵
        console.warn(`[${repoName}] 처리 중 오류 (스킵): ${err.message}`);
      }
    }

    // 6. 최종 데이터를 public/commits.json 파일로 저장
    await fs.ensureDir(path.dirname(outputPath));
    await fs.writeJson(outputPath, finalData, { spaces: 2 });

    console.log(`\n🎉 성공! ${Object.keys(finalData).length}개 레포의 데이터를 ${outputPath}에 저장했습니다.`);

  } catch (err) {
    console.error('전체 프로세스 실패:', err);
    process.exit(1);
  }
}

main();