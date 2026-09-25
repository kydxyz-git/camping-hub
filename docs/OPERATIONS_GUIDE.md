# 캠핑허브 웹사이트 운영가이드 (보관본)

> 노션 원문 「📘 캠핑허브웹사이트_운영가이드_260422」(`34a02bbd-cd95-81aa-a5e6-fc8dacd3ca09`, 2026-08-12 기준)을 옮긴 보관본입니다.
> - **현재 유효한 규칙은 루트 `CLAUDE.md`가 기준**입니다. 이 문서와 다르면 `CLAUDE.md`와 실제 코드를 따르세요.
> - 12-3 GitHub Token 섹션은 보안상 삭제했습니다. 토큰·시크릿은 저장소에 절대 넣지 마세요.
> - "⚠️ 폐기" 표시가 있는 섹션은 더 이상 사용하지 않는 절차입니다.

---
제로문(@kyd_zm)의 인스타 바이오 링크 허브 웹사이트의 구조와 운영 방식을 정리한 문서입니다. 이 문서를 기준으로 Claude와 협업하면 동기화·새 콘텐츠 추가·디버깅이 일관된 방식으로 진행됩니다.
---
## 1. 개요
- **목적**: 인스타 바이오 링크에 연결되는 원페이지 허브. 다녀온 캠핑장 / 인스타 시리즈 / 추천 음식 / 추천 템을 한 번에 보여줌
- **배포 URL**: [https://kydxyz-git.github.io/camping-hub/](https://kydxyz-git.github.io/camping-hub/)
- **GitHub 저장소**: [https://github.com/kydxyz-git/camping-hub](https://github.com/kydxyz-git/camping-hub)
- **배포 방식**: GitHub Pages (main 브랜치 자동 배포)
- **소스 파일**: 단일 HTML 파일 `index.html` (약 50KB, 인라인 CSS/JS)
- **노션 허브 페이지**: `34902bbd-cd95-81f8-b57d-e881825e992e` (🏕️ 인스타 프로필)
---
## 2. 아키텍처
> ⚠️ **폐기** — 노션 진실소스 구조는 폐기됨. 현재 진실소스는 admin(kydzm) → `data/*.json` 자동 커밋. 루트 `CLAUDE.md` 참조.
### 2-1. 진실소스(Single Source of Truth)
**모든 콘텐츠 데이터의 원본은 노션**입니다. HTML은 빌드 시점에 노션 DB를 읽어와서 정적 파일로 박제됩니다. 사용자가 데이터를 수정할 때는 노션에서 하고, Claude에게 "동기화해줘"라고 요청하면 빌드가 실행됩니다.
### 2-2. 데이터 흐름
```javascript
노션 DB (4개) → sync_data.json (캐시) → index.html (빌드) → GitHub push → GitHub Pages 배포
```
### 2-3. 왜 이런 구조인가
- 노션 API를 런타임에 직접 호출하지 않음 → 빠른 로딩, 로그인 불필요, 공개 가능
- 정적 파일이라 인프라 비용 0원
- 수정은 노션에서 자연스럽게, 반영은 Claude가 빌드
---
## 3. 노션 데이터 구조
> ⚠️ **폐기** — 노션 DB는 더 이상 사이트 데이터의 진실소스가 아님 (기록용).
### 3-1. 4개의 데이터 소스
<table header-row="true">
<tr>
<td>영역</td>
<td>collection_id</td>
<td>용도</td>
</tr>
<tr>
<td>🏕️ 인스타 프로필 (허브 페이지 자체)</td>
<td>`34902bbd-cd95-81f8-b57d-e881825e992e`</td>
<td>사이트 텍스트 (타이틀, 소개, CTA 등)</td>
</tr>
<tr>
<td>인스타 시리즈 DB</td>
<td>`d867d959-4c1b-487c-b7e0-ae7d82987520`</td>
<td>캠핑이야기 탭의 시리즈별 에피소드</td>
</tr>
<tr>
<td>캠핑장 카탈로그 DB</td>
<td>`b5638d30-2613-4f25-aa76-88b3f65cf9e8`</td>
<td>다녀온 캠핑장 목록</td>
</tr>
<tr>
<td>추천 음식 DB</td>
<td>`fba27f16-acf1-46ff-ae39-17828322229c`</td>
<td>추천 음식 탭</td>
</tr>
<tr>
<td>추천 템 DB</td>
<td>`2e74ca8b-8cdf-45ea-b78c-0b885a2b1ee6`</td>
<td>추천 템 탭</td>
</tr>
</table>
### 3-2. 인스타 시리즈 DB 스키마
- **시리즈** (select): 시리즈명. 같은 시리즈명이면 자동 그룹핑
- **에피소드명** (title): EP 제목 (예: "야키토리 토리야 등")
- **EP번호** (number): 에피소드 번호. 0이면 시리즈 번호 안 붙음
- **인스타링크** (URL): 원본 인스타 포스트/릴스 URL
- **썸네일** (files): 이미지 파일. 여기에 올리면 Claude가 자동 추출·크롭해서 웹페이지에 반영
- **공개** (checkbox): 체크된 것만 사이트에 표시
### 3-3. 캠핑장 카탈로그 DB 스키마 (260425 동기화 완료)
**🆕 자동 동기화 대상으로 승격됨!** 이제 HTML 하드코딩이 아닌 노션 DB가 진실소스.
- **캐핑장명** (title)
- **지역** (select): 강원/경기/충북/충남/경북/경남/전북/전남/제주
- **추천 계절** (multi_select): 봄/여름/가을/겨울/사계절
- **Landscape** (multi_select): 바다/산/숲/계곡/강/호수/폐교/잔디/기타
- **그래가 예약** (checkbox): 그래가 파트너십 여부
- **별점** (number, 0\~5, 0.5 단위) — UI에서 숨김 처리됨지만 데이터는 유지
- **다녀온 횟수** (number)
- **예약 싸이트** (URL): 플랫폼 뱃지 URL 기반 자동 판별
- **기타 태그** (multi_select): 수영장/글램핑/장박/볜꽃/일출/애견동반/노키즈/펜션/개별샤워실/잔디/억새/철쪽
- **이미지** (files): 카드 썸네일 (슬라이드쇼 지원, 복수 파일 가능)
---
## 4. 썸네일 자동화 파이프라인
> ⚠️ **폐기** — 노션 썸네일 파이프라인 폐기. 장비·음식 썸네일 규격은 `CLAUDE.md` 기준(800×800, 흰 배경, 여백 7%).
노션 썸네일 필드에 이미지를 올리면 Claude가 다음 절차로 자동 처리합니다.
### 4-1. 파이프라인 단계
1. **페이지 fetch**: `notion-fetch`로 해당 에피소드/캠핑장 페이지 조회
2. **파일 메타 추출**: 썸네일 필드의 `file://...` URL에서 attachment_id, filename, block_id를 파싱
3. **signed URL 획득**: `https://tropical-individual-34c.notion.site/api/v3/getSignedFileUrls`에 POST 요청
4. **다운로드**: 받은 signed URL로 이미지 바이트 다운로드 (503 발생 시 자동 재시도)
5. **크롭·리사이즈**: PIL로 4:5 비율 **센터 크롭** → **600×750** → JPEG quality 80 저장
6. **커밋**: `gh-camping-hub/images/series/{slug}.jpg`에 저장 후 git push
7. **경로 업데이트**: `sync_data.json`의 thumb 경로를 `./images/series/{slug}.jpg`로 업데이트
### 4-2. 파일명 규칙
- 인스타 시리즈 썸네일: `./images/series/{시리즈슬러그}-ep{번호}.jpg`
	- 예: `summer-ep01.jpg`, `tips-01.jpg`, `gear-01.jpg`, `food-ep01.jpg`
- 캠핑장 이미지: `./images/{캠핑장슬러그}.jpg` 또는 `./images/{캠핑장슬러그}-1.jpg` (다중)
### 4-3. 이미지 규격
- **비율**: 4:5 (세로)
- **해상도**: 600×750 px
- **포맷**: JPEG, quality 80, optimize=True
- **용량**: 통상 100\~150KB
---
## 5. 동기화 절차 (Claude 내부 워크플로우)
> ⚠️ **폐기** — 노션 동기화 + `_build` 템플릿 빌드 절차 폐기. `index.html` 직접 수정 + `data/*.json` 런타임 로드 방식 (14-15 참조).
사용자가 "동기화해줘"라고 했을 때 Claude가 실행하는 단계입니다.
1. **노션 4개 DB fetch**: notion-search/fetch로 최신 데이터 수집
2. **sync_data.json 갱신**: 로컬 캐시 파일 업데이트
3. **신규/변경 썸네일 처리**: 파이프라인 실행 → `gh-camping-hub/images/`에 저장
4. **HTML 빌드**: `camping-hub-v4-draft.html` 템플릿의 4개 동기화 영역에 `re.sub(lambda m: ...)` 방식으로 JS 변수 주입
	- ① 사이트 텍스트(siteConfig), ② 인스타 시리즈(series), ③ 추천 음식(foods), ④ 추천 템(items)
	- **주의**: `re.sub`에 lambda를 반드시 사용해야 `\n`이 이중 이스케이프되지 않음
5. **문법 검사**: `node --check`로 스크립트 에러 사전 차단
6. **git push**: `gh-camping-hub/` 폴더에서 commit + push → GitHub Pages 자동 배포
### 5-1. 빌드 템플릿 파일
- 경로: `/mnt/user-data/outputs/camping-hub-v4-draft.html`
- **이 파일이 레이아웃의 진실소스**. HTML/CSS/JS 수정은 여기서 하고 빌드 후 `index.html`로 복사
### 5-2. 캠핑장 카탈로그의 예외
현재 캠핑장 데이터는 HTML 내부에 **하드코딩된 ****`camps`**** 배열**로 들어가 있습니다. 노션 DB가 진실소스지만, 자동 동기화 경로는 아직 구축되지 않았습니다. 추가/수정은 Claude가 수동으로 반영합니다. (향후 개선 과제)
---
## 6. 새 콘텐츠 추가 방법
> ⚠️ **폐기** — 노션에 추가 후 "동기화해줘" 방식 폐기. 콘텐츠는 admin(kydz.kr/kydzm/)에서 추가.
### 6-1. 새 시리즈 에피소드 추가
1. 노션 인스타 시리즈 DB에 페이지 생성
2. 시리즈/에피소드명/EP번호/인스타링크 입력
3. 썸네일 필드에 이미지 업로드 (4:5 비율 권장, 아니어도 자동 크롭됨)
4. 공개 체크
5. Claude에게 "동기화해줘"
### 6-2. 새 시리즈 자체를 추가
첫 에피소드 추가 시 자동으로 생성됩니다. 시리즈 이모지/색상은 Claude가 임의로 넣으니, 원하는 값이 있으면 사전에 지정해주세요.
### 6-3. 새 캠핑장 추가
1. 노션 캠핑장 카탈로그 DB에 페이지 생성
2. 이름/지역/별점/방문횟수/예약 URL/그래가 체크 등 입력
3. Claude에게 "캠핑장 추가해줘" → HTML의 camps 배열에도 수동 반영됨
### 6-4. 추천 음식/템 추가
노션 해당 DB에 페이지 생성 후 동기화 요청 → 자동 반영됨
---
## 7. UI/UX 세부 규칙
### 7-1. 캠핑장 카드 플랫폼 뱃지
예약 URL을 기준으로 자동 판별 (캠핑장 카드 좌상단 표시):
<table header-row="true">
<tr>
<td>뱃지</td>
<td>색상</td>
<td>조건</td>
</tr>
<tr>
<td>그래가</td>
<td>검정 `#1a1a1a`</td>
<td>`graega: true` 플래그</td>
</tr>
<tr>
<td>네이버</td>
<td>연두 `#03C75A`</td>
<td>URL에 `naver.com` 포함</td>
</tr>
<tr>
<td>캠핏</td>
<td>진녹색 `#2D8F4C`</td>
<td>URL에 `camfit.co.kr` 포함</td>
</tr>
<tr>
<td>땡큐캠핑</td>
<td>주황 `#FF6B2C`</td>
<td>URL에 `thankqcamping.com` 또는 `camperstory.com` 포함</td>
</tr>
<tr>
<td>기타</td>
<td>회색 `#9e9e9e`</td>
<td>URL은 있으나 위 해당 없음</td>
</tr>
<tr>
<td>(없음)</td>
<td>—</td>
<td>URL이 빈 경우</td>
</tr>
</table>
### 7-2. URL 없는 카드
- `<a>` 대신 `<div class="camp-card no-link">`로 렌더링 → 클릭 불가, 커서 기본형
### 7-3. 시리즈 디자인
- 썸네일 크기: 121×151 px
- 시리즈 헤더: 이모지 + 시리즈명 + 색상 포인트 라인 + 우측 chevron 아이콘
- EP 배지: 썸네일 좌하단, 시리즈 색상으로 표시 (EP번호 \> 0일 때)
- 시리즈 가로 스크롤 화살표: 3편 이상일 때만 활성, 151px 높이 bounce 애니메이션
- 화살표 배경색: `var(--point)` (탭 활성화 녹색과 동일, opacity 0.52 → hover 0.82)
### 7-4. 시리즈 아코디언 토글
- 시리즈 제목바 클릭 시 썸네일 영역 접힘/펴짐
- 기본 상태: 모두 펼침
- 각 시리즈 독립 상태 (한 시리즈를 접어도 다른 시리즈는 유지)
- 우측 chevron 아이콘: `v` (펼침) ↔ `>` (접힘) 0.28s 회전 애니메이션
- CSS: `grid-template-rows: 1fr → 0fr` transition 0.3s
- 헤더에 `cursor:pointer` + active 피드백 (opacity 0.7)
### 7-5. 캠핑장 카운트바
- 표시 형식: `{N}개 / {X}회` (예: 69개 / 155회)
- `N`: 필터 적용 후 캠핑장 수
- `X`: 필터 적용된 캠핑장들의 visits 합계 **+ 기본 3회 보정**
- 보정 이유: 삭제된 고아웃 노지 방문 3회 반영
- 코드 위치: `renderGrid()` 함수 내 `+ 3` 상수 (추후 변경 시 이 값만 수정)
### 7-6. 다녀온 캠핑장 정렬 기준 (260425 단순화)
1. 그래가 파트너 (graega:true) 우선
2. 방문 횟수 내림차순 (많이 간 곣 먼저)
3. 이름 가나다 오름차순
- ↔️ 이전(별점 포함 4단계)에서 **별점 기준 제거**. 별점은 UI에서도 숨김 처리됨(7-7 참고).
- 함수: `sortCamps(arr)` 내 3단계 비교
### 7-7. 별점 표시 숨김
- CSS: `.camp-stars { display:none }` → 카드 UI에서 별점 숨김
- 데이터는 노션 DB에 유지 (추후 필요 시 다시 노출 가능)
- 현재 정렬에서도 사용 안 함
### 7-8. 에피소드명 EP 접두사 자동 제거
- 시리즈 카드 에피소드명에서 `EP.\d+ ` 접두사를 정규식으로 자동 제거
- 예: "EP.01 야키토리 토리야 등" → "야키토리 토리야 등"
- EP 배지는 그대로 유지 (시각적 번호는 배지로 전달)
- 코드: `ep.title.replace(/^EP\.\d+\s*/i, '')`
### 7-9. 에피소드 정렬
- ep 있음: EP 번호 내림차순 (최신이 왼쪽)
- ep 없음 (ep=0): 매 페이지 로드마다 랜덤 셀플
- 둘 다 있음: ep 있는 것이 먼저, 나머지 랜덤
- 함수: `renderSeries()` 내 `sortedEps`
### 7-10. 이미지 없는 카드
지형(landscape)별 파스텔 그라디언트 배경 + 캠핑장명 텍스트 표시. 매핑: 바다/강/계곡/호수/숲/산.
---
## 8. 트러블슈팅
### 8-1. 노션 페이지 archived 에러
- **증상**: `update_page` 호출 시 "Can't edit block that is archived" 400 에러
- **원인**: 페이지가 노션에서 아카이브된 상태
- **해결**: 노션에서 해당 페이지 복원 → 다시 동기화. 또는 Claude는 다른 페이지는 계속 진행하고 archived 건만 건너뜀
### 8-2. 브라우저 캐시로 변경사항 안 보임
- **증상**: push 완료했는데 사이트에 반영 안 됨
- **해결**: `Ctrl+Shift+R` (Mac: `Cmd+Shift+R`) 하드 리프레시. 또는 URL 끝에 `?v=N` 파라미터 추가
### 8-3. Notion getSignedFileUrls 503
- **증상**: 썸네일 다운로드 시 HTTP 503
- **해결**: 자동 재시도 로직이 있음 (최대 3회, 시도당 2초 대기 증가). 대부분 한 번의 재시도로 성공
### 8-4. 크롭 결과가 이상함
- **원인**: 원본이 지나치게 가로가 긴 경우 센터 크롭 시 중요 영역이 잘림
- **해결**: 노션 업로드 시 4:5에 가까운 비율로 준비하거나, Claude에게 "크롭 영역 바꿔줘" 요청
### 8-5. node --check 실패
- **원인**: 템플릿 변수 주입 시 이스케이프 실패 (주로 `\n`)
- **해결**: `re.sub`에 문자열 대신 `lambda m: replacement` 사용 (이스케이프 시퀀스 보존)
---
## 9. 기술 스택 & 자산
- **빌드 환경**: Python 3.12 + PIL(Pillow), Node.js (문법 검사용)
- **배포**: GitHub Pages (main 브랜치, index.html 루트)
- **GitHub Token**: 로컬 환경변수 TOKEN. 토큰 노출 시 revoke 필수
- **로컬 작업 폴더**: `/home/claude/gh-camping-hub/` (git 저장소 복제본)
- **템플릿**: `/mnt/user-data/outputs/camping-hub-v4-draft.html`
- **캐시**: `/home/claude/sync_data.json`
---
## 10. 향후 개선 과제
- [ ] 캠핑장 카탈로그를 sync_data.json 기반으로 자동화 (현재 HTML 하드코딩)
- [ ] 중복 캠핑장 정리 (황매산오토/별쿵, 산중오토/산중오토계곡 등) — 제로문님 직접 정리 예정
- [ ] archived 페이지 자동 복원 로직
- [ ] 썸네일 자동 OCR로 에피소드 제목 확인
- [ ] 관리자 모드 (빌드 히스토리 확인용)
- [ ] 방문횟수 +3 보정을 노션 데이터로 대체 (현재 하드코딩)
---
## 11. 업데이트 기록
### 260422 (후반 세션)
- **캠핑장 예약 URL 웹 검색 추가**: 16개 캠핑장 URL 노션 DB + HTML 동시 반영 (합천정양·사천솔섬·산청별천지·함양라온·든해솔계곡·지리산365·양산무릉도원·장성편백힐·단양소풍·경산갓바위·고성상족암·고흥나로힐링·고아웃 안동/부여/몽산포·황매산오토)
	- archived 상태: 황매산오토캠핑장, 고아웃캠핑(부여) — HTML엔 반영됐지만 노션엔 반영 안 됨
- **플랫폼 뱃지 시스템 구축**: URL 기반 5종 자동 판별 (그래가/네이버/캠핏/땡큐캠핑/기타). 44개 캠핑장에 뱃지 표시
- **URL 없는 카드 클릭 방지**: `<a>` → `<div class="no-link">`
- **"또 해먹고 싶은 캠핑 음식" 시리즈 추가**: 🍖 이모지, `#C94A4A` 컬러, EP.01 야키토리 토리야 등
- **썸네일 자동화 파이프라인 실제 작동 확인**: getSignedFileUrls API로 food-ep01.jpg 다운로드/크롭/저장 성공
- **운영 가이드 노션 문서 생성**: 이 문서 (ID 34a02bbd-cd95-81aa-a5e6-fc8dacd3ca09)
- **시리즈 순서 변경**: 또해먹고싶은캠핑음식이 장비소개 위로 이동
- **시리즈 아코디언 토글 기능**: 제목바 클릭 시 접기/펴기
- **화살표 색상 포인트 컬러로 통일**: `rgba(37,99,235,0.52)` → `var(--point)` opacity 0.52
- **캠핑장 카운트바 개선**: `69개` → `69개 / 155회` (visits 합계 + 기본 3회 보정)
### 260422 (전반 세션)
- 시리즈 화살표 UI 개선 (position/top 계산 최종화)
- 다녀온 캠핑장 28→69개 확장 (41개 신규 추가)
- 기존 28개 별점 노션 DB 기준으로 전체 재검토·수정
- 예약 URL 14개 초기 입력 (그래가/네이버/캠핏/땡큐캠핑 혼합)
### 260421
- 여름캠핑장 시리즈 EP.01 릴스 완성
- 캠핑 허브 웹사이트 초기 구축 (Notion 4개 DB 구조 확립)
### 260425 (운영 세션 - 재접속)
- **시리즈 에피소드 정렬 로직**: ep 있음 → 역순, ep 없음 → 매 로드마다 랜덤
- **별점 UI 숨김**: `.camp-stars { display:none }`, 데이터는 유지
- **에피소드명 EP 접두사 자동 제거**: 정규식으로 `EP.\d+ ` 패턴 렌더링 시 제거
- **노션 동기화 1차**: 여름캠핑장 EP.01 URL → 릴스 주소로 업데이트, 제목에서 EP.01 접두사 제거
- **정렬 기준 단순화**: 그래가 → 별점 → 방문횟수 → 가나다 (4단계) → **그래가 → 방문횟수 → 가나다 (3단계)**
- **캠핑장 카탈로그 자동 동기화 구축**: HTML 하드코딩 제거, sync_data.json 기반으로 변경. 64개 캠핑장 + 15장 이미지 자동 동기화
### 260427 (대규모 업데이트)
- **추천 음식 5개로 확장**: 툇골 오리 주물럭(쿠팡 49,400원), 성수동 분식 고추튀김(컬리 30%할인 9,729원), 부산 이가네 떡볶이(컬리 7,490원), 전주 베테랑 김치만두(컬리 5,980원), 니뽕내뽕 크뽕(컬리 10%할인 8,100원)
- **봄·가을에 가기 좋은 캠핑장 시리즈 신설**: EP.01 "철쭉 명소 바로 옆 캠핑장" 추가 (🌸 #E89BB9), 인스타 릴스 URL 등록 완료
- **시리즈 순서 재정렬**: 여름→봄·가을→꿀팁→음식→장비
- **EP 배지 표시 정밀화**: URL 유무 무관 ep\>0이면 항상 표시 (이전: URL 있을 때만)
- **인스타 아이콘 정밀화**: URL이 [instagram.com](http://instagram.com) 포함할 때만 표시 (이전: URL 있으면 무조건)
- **추천 음식/템 그리드 3칸**: 2칸→3칸 변경, 카드 폰트/패딩 비례 축소
- **추천 음식/템 카드 랜덤 셔플**: 매 페이지 로드마다 sort(()=\>Math.random()-0.5)로 카드 순서 랜덤
- **안내문 키 4종 신설 + 노션 진실소스화**:
	- `foodPartnersLine1/2`: 추천 음식 탭 (쿠팡+컬리, 통합 문구)
	- `itemPartnersLine1/2`: 추천 템 탭 (쿠팡+네이버, 통합 문구)
	- `priceNotice`: 추천 음식/템 하단 가격 안내 ("해당 제품 금액은 등록 시기...")
	- 모든 안내문 "구매 시" 통일
- **노션 인스타 프로필 페이지 토글에 안내문 4종 진실소스 등록**: "📢 사이트 텍스트 설정" 토글에 직접 저장 → 향후 노션 수정만으로 동기화 가능
- **가격 표시 버그 수정**: 정가만 있고 할인가 없을 때 같은 가격이 취소선+굵은글씨 두 번 표시되던 버그 → `(item.price_original && item.price_sale)` 조건으로 취소선 표시
- **긴 캠핑장명 좌측 스크롤 마퀴**: 컨테이너 너비 초과 시 자동 감지 → 텍스트 2번 복제 + CSS animation 12초 좌측 슬라이드 (창바우마을 해송피크닉장 등 3개 카드 자동 적용)
### 260428 (이미지 슬라이드쇼 + 데이터 추가)
- **합천호코지캠핑장**: 이미지 1장 → 5장 추가 (그래가, 15회 방문)
- **황매산별쿵캠핑장**: 12회 → 13회, 이미지 1장 → 5장 추가
- **캠핑장 카드 이미지 슬라이드쇼 (다중 이미지일 때)**:
	- (1) 페이지 로드 시 첫 화면 랜덤 1장 선택
	- (2) 5초마다 다음 사진으로 페이드 전환 (CSS opacity 0.7s)
	- (3) 카드별 0\~5초 사이 랜덤 시작 시차 → 모든 카드 동시 전환 방지
	- 함수: `initSlideshow()` (`Math.random() * 5000` 시작 지연 + `setInterval(5000)` 순환)
---
## 12. 새 채팅 세션에서 작업 시작하기
> ⚠️ **폐기** — `_build` 복원·노션 동기화·토큰 푸시 절차 모두 폐기. (12-3 토큰 섹션은 보안상 삭제됨)
새 Claude 채팅에서 동기화 작업을 이어가려면 다음 절차를 따릅니다.
### 12-1. 필수 자산 위치
<table header-row="true">
<tr>
<td>자산</td>
<td>위치</td>
<td>영구성</td>
<td>배포된 사이트</td>
<td>[https://kydxyz-git.github.io/camping-hub/](https://kydxyz-git.github.io/camping-hub/)</td>
<td>영구</td>
</tr>
<tr>
<td>Git 저장소 (index.html, 이미지, 템플릿, sync_data.json)</td>
<td>[https://github.com/kydxyz-git/camping-hub](https://github.com/kydxyz-git/camping-hub)</td>
<td>영구</td>
<td>노션 4개 DB + 인스타 프로필 페이지</td>
<td>이 운영 가이드 3장 참조</td>
<td>영구</td>
</tr>
<tr>
<td>로컬 작업 폴더</td>
<td>/home/claude/gh-camping-hub</td>
<td>**채팅 세션마다 초기화**</td>
<td>HTML 템플릿</td>
<td>/mnt/user-data/outputs/camping-hub-v4-draft.html</td>
<td>**채팅 세션마다 초기화**</td>
</tr>
</table>
### 12-2. 새 채팅 첫 작업 셋업 (Claude가 자동 수행)
```bash
# 1. GitHub repo clone
cd /home/claude
git clone https://github.com/kydxyz-git/camping-hub.git gh-camping-hub

# 2. 백업된 빌드 자산 복원
cp gh-camping-hub/_build/camping-hub-v4-draft.html /mnt/user-data/outputs/
cp gh-camping-hub/_build/sync_data.json /home/claude/
```
빌드 자산은 git repo의 `_build/` 폴더에 백업되어 있습니다. 두 파일만 있으면 모든 동기화 작업 재개 가능.
### 12-4. 새 채팅에서 "동기화해줘" 시 Claude 동작
1. 메모리에서 프로젝트 컨텍스트 자동 로드 (메모리 #14\~22)
2. 12-2 셋업 절차 실행 (git clone + _build/ 복원)
3. sync_data.json 로드 → _metadata.last_sync 확인 + 78개 page_id 사용 가능
4. 노션 4개 DB fetch → 변경사항 식별
5. 신규 이미지 다운로드 + 빌드 + push
### 12-5. 🔑 자동 전체 동기화 (새 채팅에서 "전체 동기화해줘" 요청 시)
**핵심**: sync_data.json에 이미 78개 page_id 모두 저장되어 있으므로, **더 이상 search로 page_id 찾는 무거운 작업 불필요**.
#### 실행 절차
```javascript
1. cd /home/claude && git clone https://github.com/kydxyz-git/camping-hub.git gh-camping-hub
2. cp gh-camping-hub/_build/camping-hub-v4-draft.html /mnt/user-data/outputs/
3. cp gh-camping-hub/_build/sync_data.json /home/claude/
4. sync_data.json 로드 → _metadata.last_sync 읽음 (예: 2026-04-28T08:58:52Z)
5. 78개 page_id로 각각 fetch → 페이지 timestamp가 last_sync보다 최근이면 변경 후보
6. 변경 후보만 차분 처리 (데이터 디프 + 이미지 다운로드)
7. sync_data.json 갱신 + last_sync 타임스탬프 새로고침
8. 빌드 + push
```
#### 소요 시간
- **이전** (page_id 메모리에만 존재): 새 채팅에서 **64최제 캐핑장 search 64회** 필요 → 무거운 작업
- **이후** (sync_data.json에 ID 캠): **fetch 78회만**, search 없음 → 1–2분 내 완료
#### sync_data.json 구조
```json
{
  "_metadata": {
    "last_sync": "2026-04-28T08:58:52Z",
    "page_id_index_complete": true,
    "notion_collections": { "series": "...", "camps": "...", "foods": "...", "items": "...", "profile": "..." }
  },
  "siteConfig": { "foodPartnersLine1": "...", "itemPartnersLine1": "...", "priceNotice": "...", ... },
  "series": [ { ..., "eps": [ { ..., "page_id": "34a02bbd-..." } ] } ],
  "foods":  [ { ..., "page_id": "34f02bbd-..." } ],
  "items":  [ { ..., "page_id": "34a02bbd-..." } ],
  "camps":  [ { ..., "page_id": "34a02bbd-..." } ]
}
```
#### 차분 동기화가 여전히 가능
사용자가 "X 캠핑장에 이미지 추가했어" 같이 알려주면 그 항목 하나만 fetch해서 처리 (가장 가벼움). page_id도 sync_data에 이미 있어서 바로 접근 가능.
---
---
## 13. 260507\~260508 업데이트 (긴 채팅 세션 누적)
2026년 5월 7\~8일 한 번의 긴 Claude 채팅에서 진행된 모든 변경사항. 채팅 길이로 인해 마지막 한 가지가 미완료 (13-3 참조).
### 13-1. 260507 — 차분 동기화 시스템 강화
> ⚠️ **폐기** — 노션 차분 동기화(`tools/`)는 폐기된 구버전.
**문제 의식**: 노션 search API가 의미적 매칭이라 키워드 안 맞으면 신규 ep 누락 (장비소개 "포켓4 악세사리" 사례).
**해결**: tools/ 폴더 신설.
- **tools/SYNC_**[**GUIDE.md**](http://GUIDE.md): 동기화 표준 절차서, 3중 안전망 명시
- **tools/incremental_**[**sync.py**](http://sync.py): 카테고리별 다중 키워드 모듈 (88개 키워드). SEARCH_KEYWORDS, find_new_pages_by_keywords(), detect_changes()
- **tools/refresh_**[**cache.py**](http://cache.py): cached_pages 자동 재계산 유틸
- **sync_data._metadata.cached_pages 신설**: 83개 page_id 캐시 (series 11 / camps 64 / foods 6 / items 2). 직접 fetch로 search 우회.
**3중 안전망**:
1. cached_pages 직접 fetch — 기존 ep 변경 감지 (확실함)
2. 다중 키워드 검색 (5\~20개씩) — 신규 ep 검출
3. created_date_range 필터 — last_sync 이후만 좁힘
**금지 사항**: search 0건 → "변경 없음" 단정 / 캐시 무시하고 search만 사용 / cached_pages 갱신 누락
### 13-2. 260508 — 커스텀 도메인 + UX 개선 + SEO + 헤더 뱃지
**(1) **[**kydz.kr**](http://kydz.kr)** 커스텀 도메인**
- GitHub Pages CNAME 등록 ([kydz.kr](http://kydz.kr))
- 가비아 DNS A 레코드 4개: 185.199.108.153 / 109.153 / 110.153 / 111.153
- 가비아 기존 URL 포워딩 해제 필수
- HTTPS 인증서 자동 발급 대기 → 발급 후 Enforce HTTPS 활성화
- 이전 gabia forwarding은 meta refresh라 해시/path 보존 안됨 → 커스텀 도메인이 답
**(2) 탭 해시 라우팅**
- URL: /#stories, /#camps, /#foods, /#items
- JS: TAB_HASH_MAP, HASH_TAB_MAP, activateTab(), applyHashTab(), hashchange 이벤트 대응
- 인스타 캡션에 짧은 URL로 특정 탭 진입 안내 가능
**(3) 인스타 인앱 브라우저 외부 전환**
- 시나리오: 인스타에서 [kydz.kr](http://kydz.kr) 들어온 사용자가 인스타 카드 누르면 인스타 웹페이지가 떠버리는 문제
- 해결: 외부 브라우저 강제 전환 → Universal Link로 인스타 앱 자연 호출 (팝업 X)
- iOS: x-safari-https:// → Safari 강제
- Android: intent:// + package 미지정 → 사용자 기본 브라우저 (삼성 인터넷/Chrome 모두 대응)
- UA에 Instagram 또는 FBAN/FBAV 포함 시에만 가로채기
- 시도했다 폐기: instagram:// 스킴 직접 → "외부 앱 열기" 팝업 (OS 보안, 우회 불가)
**(4) SEO 강화**
- 메타 태그: title/description/keywords/canonical/OG (10개)/Twitter Card
- JSON-LD: WebSite + Person 스키마
- robots.txt + sitemap.xml (4개 탭 해시 URL 포함)
- 검색봇 허용: googlebot/naverbot/yeti
- 한국어 키워드: 공대남자/오토캠핑/캠핑장 추천 등
- Google Search Console / 네이버 서치어드바이저 등록은 사용자 작업 (보류)
**(5) 헤더 그래가파트너스 뱃지**
- siteConfig.headerBadge 신규 키 ("🤝 그래가파트너스")
- 부제 아래 우측 정렬, 알약형 (border-radius: 100px)
- 노션 가이드: "\[헤더 뱃지\]" 섹션 분리 등록 완료
- ⚠️ 색상 검정 변경 미완료 → 13-3 참조
**(6) 데이터 동기화 다양한 변경**
- 추천 음식: "두릅 튀김, 등갈비 구이 등" 추가 (food-ep02.jpg)
- 여름캠핑장 EP.02: "물이 이렇게 맑다고?" (summer-ep02.jpg)
- 장비소개: "포켓4 악세사리 이거 하나면 끝!" (gear-02.jpg)
- 추천 템: "울란지 PM01 맥세이프 연장 브라켓" (네이버, item-02.jpg, 41,000원)
- 포레스트유 데크팩SET: 가격 정보 추가 (정가 22,310 / 할인가 22,050 / 1%)
- 봉화별 27회 갱신 (26→27)
- 문경 그린스톤·밀양 구만산장 이미지 5장 보강 (각 1→5)
- 타프 치는 방법 썸네일 교체
- 우중철수 꿀팁 인스타 링크 갱신 (post→reel)
**(7) UI 개선**
- 캠핑장 카드 visits 항상 우측 정렬 (justify-content: flex-end)
- 네이버 뱃지 추가 (source="네이버" 자동 인식, #03C75A 그린)
- 파트너스 면책 문구 통일 (음식·템 둘 다 "쿠팡+컬리+네이버" 3종)
**(8) prompts/ 폴더 신설**
- prompts/instagram-profile-3d-diorama.txt: 프롬프트 원본
- prompts/instagram-profile-3d-diorama.html: 모바일 1탭 클립보드 복사 페이지
- 캠핑 허브 본 컨셉과 분리 (정체성 영향 0)
### 13-3. ✅ 헤더 뱃지 색상 변경 완료 (260509)
**헤더 그래가파트너스 뱃지 색상 변경 — 완료**
- 변경 전: `background: var(--point)` (올리브)
- 변경 후: `background: #1a1a1a` (검정)
- 적용 파일: `index.html` + `_build/camping-hub-v4-draft.html` (둘 다 수동 동기화)
- 커밋: `27fd434` ("style: 헤더 그래가파트너스 뱃지 색상 검정으로 변경")
- 처리 일자: 2026-05-09
- 결과: GitHub Pages 자동 배포 → [kydz.kr](http://kydz.kr) 반영 완료
> ⚠️ **폐기** — `_build` 템플릿 양쪽 수정 방식 폐기 (14-15, 14-18 참조).

**처리 흐름** (다음 유사 작업 시 참고):
1. 새 채팅에서 "운영가이드 읽고 이전 작업 진행해줘" 입력
2. Claude가 13-3 미완료 작업 식별 → 방향성 보고
3. 사용자 승인 후 git clone + 색상 변경 + 빌드 없이 직접 push까지 1\~2분 내 완료
**참고**: 데이터 동기화 없이 CSS만 변경하는 경우 별도 빌드 스크립트 실행 불필요. 템플릿(`_build/camping-hub-v4-draft.html`)과 `index.html` 양쪽에 동일 변경을 직접 적용하는 방식이 가장 안전.
### 13-4. 다음 채팅 시작 시 동작
> ⚠️ **폐기** — 노션/메모리 기반 재개 절차 폐기.
새 채팅을 열고 다음 중 하나만 입력:
**옵션 A — 미완료 작업 즉시 처리**: "헤더 뱃지 색상 검정으로 바꿔줘"
→ Claude가 자동으로 운영가이드 fetch → 13-3 확인 → 1분 내 처리
**옵션 B — 컨텍스트 확인 먼저**: "운영가이드 읽고 이전 작업 이어해줘"
→ 13-1, 13-2, 13-3 모두 확인 후 진행
**복원되는 자료**:
- ✅ 노션 운영가이드 (이 문서) — 모든 변경사항 + 미완료 작업 명시
- ✅ git 저장소 — 마지막 push까지 모든 코드/이미지/sync_data 저장
- ✅ tools/ 폴더 — SYNC_[GUIDE.md](http://GUIDE.md) / incremental_[sync.py](http://sync.py) / refresh_[cache.py](http://cache.py)
- ✅ 메모리 #14\~29 — 토큰, 절차, 메타데이터 (이전 채팅에서 박힌 것은 유효)
- ❌ 이번 채팅 메모리 추가 (#30+) — 도구 비활성화로 못 박았음. 단 본 운영가이드가 충실해 영향 미미
---
*최종 업데이트: 2026-05-09*
---
## 14. 260521 업데이트 (Admin 시스템 + 통계 + PC 레이아웃 + 진행중)
거대한 작업 세션 (전세션 컴팩션 1회 발생). Admin CRUD부터 시작해 PC 반응형, Cloudflare 통계 시스템까지 구축. **마지막 Worker v6 race condition 해결만 미완료** (14-9 참조).
### 14-1. Admin CRUD 시스템 (kydzm/)
`kydzm/index.html` (\~5300줄). GitHub Personal Access Token 기반 인증으로 5개 카테고리(시리즈/캠핑장/음식/장비/시간/홈) CRUD 완성.
- 상단 \[+ 추가\] 통일, 토큰 카드 접힘, 캠핑장 메타 뱃지
- 모든 카테고리 정렬 SortableJS (filter + preventOnFilter:false로 select와 충돌 해결)
- 모바일 키보드 자동 등장 방지 (검색어 비어있을 때 setTimeout focus 안 줌)
- 캠핑 허브와 같은 GitHub repo 사용, /kydzm/ 경로
### 14-2. ID 기반 콘텐츠 추적
모든 콘텐츠(camps/foods/items/series/eps)에 영구 ID 부여 + created_at/updated_at 타임스탬프 추가.
- ID 형식: `{type}_{md5(name|timestamp_ns)[:10]}` (예: camp_abc123def4)
- 메인 카드: `data-track-path="/camps/{id}"` 형식, ID 없으면 폴백
- Admin: campById/foodById/itemById/epById 매핑 헬퍼
- 마이그레이션 시각: 2026-05-21T02:53
### 14-3. Admin 대시보드 - 인기 콘텐츠 분리
5개 카테고리별 별도 인셋 카드:
- 🎬 시리즈 EP / 🏕 캠핑장 / 🍖 음식 / 🛠 장비 / 📁 카테고리
- 회색 배경 #f3f4f0 + 컬러 left-border 3px (시리즈 #c97a4a / 캠핑장 #4a7c4e / 음식 #d68d3e / 장비 #5b6d8f)
- 폰트 800/13px 강조
- 헬퍼: `renderPopularSection(label, items, limit, sectionKey)`
### 14-4. PC 화면 반응형 (≥1024px)
모바일 우선 디자인 유지하면서 PC 와이드 활용:
- body `max-width: 420px → 1200px` (단일 폭, 와이드 미디어쿼리 제거)
- 캠핑장/음식/장비 그리드: 3열 → **4열**
- 시리즈 EP 카드: 121×151px → **220×275px** (한 화면에 **5개**, 4:5 비율)
- env-grid: 6열 → 8열
- 헤더/탭/푸터 패딩 32px
- 시리즈 좌우 스크롤 화살표 fix:
	- `.series-body-inner`에 `position:relative` 추가 (절대 위치 기준)
	- height 명시 (모바일 151px / PC 275px)
	- 배경 `rgba(0,0,0,0.4)`, z-index 10
	- window resize 이벤트 + debounce 100ms로 리사이즈 시 화살표 재계산
	- saInit 여러 시점 호출 (50ms/300ms/1000ms + window.load)
### 14-5. Cloudflare Workers KV 통계 시스템 v5
**구성**:
- URL: `https://kyd-stats.kydxyz.workers.dev`
- Account: kydxyz
- KV namespace: `KYDZ_STATS` (binding: STATS_KV)
- 환경변수: GITHUB_TOKEN, GH_OWNER=kydxyz-git, GH_REPO=camping-hub, GH_BRANCH=main, ALLOWED_ORIGIN (콤마구분 다중), SYNC_TOKEN
- Cron: 매시간 정각 GitHub sync + 매일 0시 UTC cleanup
**v5 하이브리드 스키마**:
- `buffer`: 미집계 이벤트 임시
- `aggregate`: 누적 + 일별 730일치 (단일 키 \~2-3MB)
	- 일별 데이터에 pages/clicks/searches/devices/referrers + hourly\[24\] 시간대별 pv
- `events:YYYY-MM-DD`: 일별 raw event 배열 (60일치, 일별 최대 5000건)
	- 각 이벤트: `{ts, type, dev, path?, target?, ctx?, ref?, q?}`
- `last_sync`: 마지막 GitHub sync 시각
**엔드포인트**:
- POST /log (이벤트 수집)
- GET /stats (aggregate)
- GET /events?date=YYYY-MM-DD (raw events)
- GET /health
- POST /sync (SYNC_TOKEN)
- POST /reset (SYNC_TOKEN)
- POST /cleanup (SYNC_TOKEN)
**자동 정리**:
- aggregate: 730일 지난 daily 항목 자동 삭제
- raw events: 60일 지난 키 삭제 (cron + endpoint)
- 봇 차단: `/bot|crawler|spider|crawling|preview|facebookexternalhit|wget|curl|python|axios/i`
### 14-6. 메인 사이트 추적 코드
- `detectDevice()` 클라이언트 측 명시 (모바일 카운팅 0 문제 해결 - sendBeacon이 UA minimal로 보낼 수 있음)
- `classifyReferrer()` 자동 분류 9개: 인스타그램/페이스북/유튜브/구글/네이버/다음·카카오/빙/그래가/direct
	- 자기 사이트([kydz.kr](http://kydz.kr)) referrer는 null
- referrer는 pageview에만 첨부
**카드 클릭 페이지뷰** - 여러 차례 시도:
1. `click` 핸들러 (기본) → 새 탭 navigation 직전 drop
2. `fetch + keepalive` (sendBeacon 대신) → 일부 환경에서도 drop
3. `pointerdown` capture 단계 (`addEventListener('pointerdown', fn, true)`) → ✅ 정상 발송 확인
4. `shouldTrack` dedup: 메모리 1초 + sessionStorage 5분 (30분에서 완화)
5. send() sendBeacon false 반환 시 fetch fallback (keepalive)
**DEBUG 모드**: URL `?debug=1` 또는 `localStorage.setItem('kydzm:debug', '1')`
- console에 단계별 로그: `[kydz stats] card detected: ...` / `sending pageview: ...` / `sendBeacon OK` / `dedup 1s: ...` 등
### 14-7. Admin 통계 대시보드 추가 분석
- **🕐 시간대 히트맵** (요일×24시간, 최근 30일): 7행 × 24열 그리드, rgba(74,124,78, alpha)
- **🔗 유입 경로** (referrer): 누적 TOP 10
- **📈 7일 트렌드** (지난주 vs 이번주 ±5%): up/down/flat 인디케이터
- **📱 디바이스 비율**: 모바일/태블릿/PC 막대 그래프
- 카테고리 한글 뱃지: stories(캠핑이야기 #7e6a8f) / camps(다녀온캠핑장 #4a7c4e) / foods(추천음식 #c97a4a) / items(추천템 #5b6d8f) / 홈 #888
- 캠핑장 플랫폼 뱃지: 그래가 #1a1a1a / 네이버 #03C75A / 캠핏 #2D8F4C / 땡큐캠핑 #FF6B2C / 기타 #9e9e9e
### 14-8. 채팅창 아카이브 워크플로우
사용자가 "삭제예정"이라고 언급하면 즉시 (1) 메모리에 핵심 학습사항·패턴·결정사항 압축 기록 (2) 노션에 채팅창 흐름·결정·학습 정리. 사용자 추가 지시 없이 자동 실행 (단, 진행상황 보고).
**노션 업데이트 규칙**: 사용자가 명시적으로 지시했을 때만 실행. 필요하다고 판단되면 먼저 "지금 노션 업데이트 할까요?" 물어보기. 사용자 승인 없이 임의 쓰기 작업 절대 금지.
### 14-9. ✅ 완료: Worker v6 race condition fix (260521 deploy)
**핵심 진단 결과 (반드시 새 채팅에서 이어가야 함)**:
#### 증상
- 사이트 카드 클릭 시 클릭 이벤트는 정상 카운트 (clicks 21건)
- 카드 페이지뷰만 안 들어옴 (pages: 홈/#stories만)
- devices 합계 28건은 정확 → **Worker가 모든 이벤트를 받긴 함**
#### 디버깅 결과
1. ✅ 메인 사이트 payload 정확 (`{type:"pageview", path:"/series/...", device:"desktop", referrer:"direct", title:"..."}`)
2. ✅ Network 탭: log 요청 200 OK
3. ✅ Console: `[kydz stats] sendBeacon OK`
4. ❌ Worker stats: 카드 페이지뷰가 pages에 안 들어감
#### 진짜 원인: Worker v5의 KV race condition
```javascript
// 현재 v5 코드 - 동시 요청 시 마지막 쓰기가 이전 쓰기 덮어씀
const buffer = await env.STATS_KV.get(KV_KEY_BUFFER, 'json') || [];
buffer.push(event);
await env.STATS_KV.put(KV_KEY_BUFFER, JSON.stringify(buffer));
```
- 카드 클릭 시 거의 동시에 2개 요청 (pointerdown 페이지뷰 + click 외부링크)
- 두 요청 모두 같은 시점에 buffer GET → 각자 자기 event push → PUT
- **두 번째 PUT이 첫 번째 PUT을 덮어씀** (KV는 eventually consistent)
- 결과: 클릭은 들어가고 페이지뷰는 덮어써짐
#### 해결책: Worker v6 - 개별 키 buffer
```javascript
// 새 코드 (race condition 회피)
async function handleLog(request, env, corsHeaders) {
  // ... sanitize ...
  
  // 개별 키로 저장 (race condition 회피)
  const key = `buf:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
  await env.STATS_KV.put(key, JSON.stringify(event), { expirationTtl: 3600 });
  
  return jsonResponse({ ok: true }, corsHeaders);
}
```
그리고 aggregate 시 `buf:*` prefix로 list해서 모두 처리:
```javascript
async function aggregateBuffer(env) {
  const list = await env.STATS_KV.list({ prefix: 'buf:', limit: 1000 });
  if (list.keys.length === 0) return;
  
  const buffer = [];
  for (const k of list.keys) {
    const event = await env.STATS_KV.get(k.name, 'json');
    if (event) buffer.push(event);
  }
  
  // 기존 aggregate 로직 그대로...
  let agg = await env.STATS_KV.get(KV_KEY_AGGREGATE, 'json') || initAggregate();
  // ... pages/clicks/searches 처리 ...
  
  // 처리 끝난 buf:* 키들 삭제
  for (const k of list.keys) {
    await env.STATS_KV.delete(k.name);
  }
  await env.STATS_KV.put(KV_KEY_AGGREGATE, JSON.stringify(agg));
}
```
#### 트리거 변경
- /log: buffer 100건 즉시 aggregate 로직 제거 (개별 키라 카운트 불가)
- /stats: 호출 시 list로 모두 가져와 aggregate (현재처럼)
- /events: 동일하게 buf:\* list 처리
- Cron 매시간: GitHub sync 전 aggregate 실행 (현재처럼)
#### KV write 비용 우려
- 무료 한도: 1,000 writes/day
- 이전: 100건마다 1 write (buffer flush)
- 신규: 매 이벤트마다 1 write
- 트래픽 50/day 기준 → 50 writes/day → 한도 5% 사용 (여유)
- 트래픽 100배 늘어도 5000/day → 무료 한도 초과 시 paid tier로 (월 \$5)
**대안**: buf:N 키 (N=0,1,2...순환)로 100개 분산하여 race 줄이기. 또는 worker durable objects 사용 (복잡).
→ 가장 간단한 해결책이 개별 키. 트래픽 증가 시 paid로 가면 됨.
### 14-10. 새 채팅 시작 가이드
> ⚠️ **폐기** — `/home/claude`·`/mnt/user-data/outputs` 기반 절차는 과거 환경 기준 (v6 배포 완료).
새 채팅 첫 메시지 예시:
> "운영가이드 14-9 읽고 Worker v6 작업 이어해줘"
또는 더 구체적:
> "Worker v5 race condition fix - 14-9 참고해서 worker-v6.js 만들어줘. buf:\{timestamp\}:\{random\} 개별 키 방식"
**Claude가 자동 수행**:
1. 운영가이드 14-9 fetch → 진단 결과 + 해결책 확인
2. `/home/claude/worker/worker-v5.js` clone (또는 GitHub에서)
3. v5 → v6 변경:
	- handleLog: buffer get/push/put → 개별 키 put
	- aggregateBuffer: list로 buf:\* 가져와 처리 후 삭제
	- 100건 즉시 aggregate 로직 제거
4. /mnt/user-data/outputs/worker-v6.js 출력
5. 사용자가 Cloudflare 대시보드에서 deploy
**Worker deploy 후 테스트**:
```bash
# 1. 헬스 체크
curl https://kyd-stats.kydxyz.workers.dev/health
# {"ok":true,"version":"v6",...}

# 2. KV 리셋 (또는 대시보드에서 buffer/aggregate/buf:* 모두 삭제)
curl -X POST https://kyd-stats.kydxyz.workers.dev/reset \
  -H "X-Sync-Token: SYNC_TOKEN_VALUE"

# 3. 시크릿 모드로 https://kydz.kr 접속, EP 카드 5개쯤 클릭

# 4. 5분쯤 후 확인
curl -s https://kyd-stats.kydxyz.workers.dev/stats | python3 -m json.tool
# pages에 /series/series_xxx/ep_xxx 들어가 있어야 정상
```
### 14-11. 이번 세션 push 이력 (참고용)
마지막 commit hash들 (feature/admin-system 브랜치 + main 모두):
- Worker v5 진단 마지막 push: main 브랜치 최신 (sendBeacon false fallback + DEBUG 모드)
- /mnt/user-data/outputs/worker-v5.js 파일 존재 (454 lines)
### 14-12. 트러블슈팅 누적 (해결됨)
1. **SortableJS + select 충돌**: filter + preventOnFilter:false + inline stopPropagation
2. **GitHub Pages 10분 캐시**: meta 캐시 방지 + ?nc=now + 빈 commit 트리거
3. **모바일 키보드 자동 등장**: 검색어 비어있을 때 setTimeout focus 안 줌
4. **CORS preflight 차단**: Content-Type 'text/plain'으로 simple request 우회
5. **Worker path 길이 잘림**: 200→500자 확장 (한글 인코딩 9자/글자)
6. **a 태그 .btn 색상 덮어쓰기**: `.btn, a.btn` 통합 셀렉터
7. **모바일 device 0건**: 클라이언트에서 detectDevice() 명시 (sendBeacon이 UA minimal로 보낼 수 있음)
8. **인코딩 한글 깨짐**: ID 기반으로 전환 (영어 10자라 길이 제한 무관)
9. **시리즈 화살표 안 보임**: `.series-body-inner`에 position:relative 누락 + height:100% 너무 길음 → 명시 height (151/275px)
10. **resize 시 화살표 재계산 안 됨**: window resize 이벤트 + debounce 100ms 추가
11. **새로고침 마다 카운트**: sessionStorage 5분 dedup
12. **sendBeacon false 반환 무시**: 반환값 체크 + fetch fallback (keepalive)
13. **카드 페이지뷰 click 핸들러 navigation 충돌**: pointerdown 단계에서 미리 발송 (capture 단계)
14. **✅ Worker KV race condition (260521 v6 해결)**: 동시 PUT으로 덮어쓰기 → `buf:{ts}:{rand}` 개별 키로 회피
15. **✅ 인스타 릴스 URL이 앱 홈으로 떨어짐 (260521 해결)**: 인스타 앱이 `/reel/` URL을 Universal Link로 잡지만 내부 라우터가 reel + igsh 조합을 못 핸들 → `/reel/`, `/reels/`, `/tv/` → `/p/` 변환 + igsh 등 share 파라미터 제거로 해결
16. **✅ 일반 브라우저에서 인스타 앱 호출 안 잡힘 (260522 해결)**: `window.open`으로 새 탭 열면 Universal Link 트리거 안 잡히는 경우 있음 → anchor href 자체를 정규화 URL로 교체 + DOMContentLoaded 시 사전 정규화
17. **✅ 삼성 인터넷에서 인스타 앱 호출 안 잡힘 (260522 해결)**: anchor href 정규화만으로 일부 Android 브라우저에서 Universal Link 안 잡힘 → Android 일반 브라우저 분기 추가하여 `intent://...package=com.instagram.android` 으로 일괄 처리
18. **⚠️ _build/ 덱레케이티드 발견 (260522)**: 운영가이드 5장 명시 템플릿 vs 실제 코드에서 차이 발견. index.html이 이미 data/\*.json 런타임 fetch 방식으로 전환되어 _build/ 템플릿은 빌드에 사용 안됨. 이후 _build/[README.md](http://README.md)로 대체 명시. 14-15 참조.
---
---
## 14-13. v6 deploy 결과 (260521)
### 배포 확인
- /health: `{"ok":true,"version":"v6"}` 확인
- KV 리셋: Cloudflare 대시보드 직접 삭제로 처리 (윈도우 환경, curl 미사용)
### 테스트 결과 (시크릿 모드 EP 카드 5개 클릭)
**KV pairs (Image 1)**: buf:\* 개별 키 11개 정상 저장 (pageview 6 + click 5)
**/stats 응답 (Image 2)**:
- `total: { pv: 6, click: 5, search: 0 }`
- `devices: { desktop: 11 }` ← 6+5=11 정확
- `referrers: { direct: 6 }` ← 페이지뷰만 referrer 첨부 정상
- `hourly[12]: 6` ← UTC 12시 (KST 21시) 6개 페이지뷰
- **`pages`****에 카드 5개 모두 들어감**:
	- `/series/series_ba7cc89468/ep_ad505df37d`: 1
	- `/series/series_304565fb77/ep_c2e684a351`: 1
	- `/series/series_873cdcaf61/ep_7dd208fe26`: 1
	- `/series/series_e8c17ad5da/ep_e46450a717`: 1
	- `/series/series_c0b82ea145/ep_39cf2ffa99`: 1
	- `/`: 1 (홈)
### 핵심 학습
- **v5 증상**: pages에 홈만 찍히고 카드 페이지뷰 drop → buffer 단일 키 race condition
- **v6 해결**: 개별 키(`buf:{ts}:{rand6}`)로 동시 쓰기 충돌 회피, TTL 1시간
- **검증 방법**: 카드 클릭 시 pageview:click 비율이 1:1이면 race 잡힘 (이전엔 0:1)
- **윈도우 환경 reset**: curl 대신 Cloudflare 대시보드에서 키 직접 삭제 가능
### 패턴화 (다음 KV race 상황 시 참고)
- Cloudflare KV는 eventually consistent → 동일 키 동시 PUT 시 마지막 쓰기 승
- 동시 쓰기 가능성 있는 데이터는 **개별 키 + prefix list 패턴** 사용
- list pagination은 cursor 안전장치 필수 (트래픽 폭증 대비)
- 무료 한도 1000 writes/day → 트래픽 50/day 기준 5% 사용, 여유
---
---
## 14-14. 콘텐츠별 분석 + 모바일 UX 개선 + 인스타 릴스 정규화 + 빌드 흐름 정리 (260521→260522)
v6 deploy 직후 사용자 피드백을 받아 연이은 작업들. 2일간 연속 세션.
### (1) 콘텐츠별 분석 카드 (신규)
- 위치: admin 통계 대시보드 안, 시간대 히트맵 카드 직후 (`#content-analysis-card`)
- 구성:
	- 모드 토글: 📄 콘텐츠 진입 (pageview) / 🔗 외부 링크 (click)
	- 콘텐츠 셀렉트 드롭다운 (누적 카운트 정렬)
	- 기간 토글: 📅 일별 (30일) / 📆 월별 (12개월)
	- 막대 차트 + 시간대 히트맵
- 데이터 소스:
	- 일별: raw events (`/events?date=YYYY-MM-DD`) 30개 병렬 fetch, 5분 메모리 캐시
	- 월별: stats.daily (730일치) — v6 deploy 이전 카드 데이터 부정확 안내 표시
	- 시간대 히트맵: raw events 30일치
- 외부 링크 처리: click 키 `context::target` 분리 후 target별로 합산 (path 노출 X)
- 라벨링: cache에서 직접 lookup
	- `/series/series_xxx/ep_yyy` → 🎬 시리즈명 · EP 제목
	- `/camps/camp_xxx` → 🏕 캐핑장명
	- `/foods/...` / `/items/...` → 🍖 / 🛠
	- `/` → 🏠 홈
### (2) 모바일 UX 개선
- 인기 콘텐츠 TOP 등록일 표시 제거 (모바일 라벨 공간 확보)
- 시간대 히트맵 **24행(시간) × 7열(요일) 세로형 전치** → 모바일 가로 스크롤 제거 (기존 + 신규 카드 모두 적용)
- 토글 **segmented control** 스타일: 회색 trough + active 흰 배경 + 그림자
- 차트 라벨 간격 자동:
	- n ≤ 12 → 모든 라벨 (월별)
	- 13 ≤ n ≤ 30 → n/5 간격 (일별)
	- n \> 30 → n/6 간격
- 월별 차트 라벨: `5월` 형식
- 시리즈 배지 max-width: 130px (PC) / 75px (모바일) + ellipsis
- KST 변환 단순화: 브라우저 로컬 시간 직접 (`getDay`, `getHours`, `getDate`)
### (3) 인스타 릴스 URL 정규화 (모든 환경 적용)
- **증상**: 인스타 앱에서 릴스 카드 클릭 시 앱은 열리지만 홈으로 떨어짐 (게시물은 정상)
- **원인 추정**: 앱이 `/reel/{code}/`를 Universal Link로 잡지만 내부 라우터가 `reel + igsh` 조합을 못 핸들
- **해결**: 클릭 시점에 URL 정규화
	- `/reel/`, `/reels/`, `/tv/` → `/p/` 변환
	- `igsh`, `igshid`, `ig_rid`, `utm_*` 파라미터 제거
- **적용 범위**: 인앱 + 일반 브라우저 모두
	- 인앱(Instagram/FBAN/FBAV): 외부 브라우저 강제 전환 + 정규화 URL
	- 일반: 정규화 URL로 새 탭 (anchor target 유지)
- **파일**: `index.html` + `_build/camping-hub-v4-draft.html` 동시 적용 (13-3 처리 흐름)
### (4) 학습사항
- Worker stats.daily는 v5 race로 일부 drop된 데이터 있어 raw events가 일별 신뢰 소스
- 모바일 우선 디자인 — PC max-width 1200px에서도 컴팩트 디자인이 보기 좋음
- 인스타 reel과 post는 같은 미디어로 해석되지만 라우팅 안정성은 post가 더 높음
- segmented control: 토글이 여러 개일 때 active 상태가 분명히 두드러져야 헷갈림 없음
- KV race 해결 패턴 (14-9)이 다른 동시 쓰기 이슈 해결의 참고교본이 됨
### (5) Push 이력 (260521 4건)
- `4055156`: 콘텐츠 분석 신규 탭 1차
- `0e3048b`: 모바일 가독성 + 일별/월별 + 외부링크 합산
- `ec8cbf8`: 토글 segmented + 차트 라벨 + 배지 truncate
- `9b530bd`: 릴스 URL 정규화
### (6) 260522 이어진 작업
**인스타 URL 정규화 확장**
- 일반 브라우저 (Safari/Chrome PC 등)에서 동작 안 되는 증상 발견 → `window.open` 대신 **anchor href 직접 교체** 방식으로 변경
- `DOMContentLoaded` 시 페이지 내 모든 인스타 anchor 사전 정규화 (이중 안전망)
- `window.normalizeAllInstagramAnchors` 전역 노출 → 동적 렌더 후 호출 가능
- admin (`kydzm/index.html`)에도 동일 핸들러 추가 + `renderStats` 끝에서 재정규화 호출
- Push: `673b31e`
**삼성 인터넷 브라우저 대응**
- 증상: 삼성 인터넷에서 anchor href 정규화만으로 인스타 앱 호출 안 잡힌 (네이버/크롬은 정상)
- 해결: Android 일반 브라우저 분기 추가
	- `intent://...#Intent;...package=com.instagram.android;S.browser_fallback_url=...;end`
	- 인스타 앱 강제 지정, 미설치 시 fallback URL로 웹 페이지 자동 이동
- 파일 3개 모두 적용 (index.html + _build + kydzm)
- Push: `520b3cc`
**페이지뷰 dedup 강화 + 콘텐츠/방문 분리**
- 기존: 메모리 1초 + sessionStorage 5분 (모든 path 동일)
- 신규: path 종류별 분리
	- **방문** (`/`, `/#stories` 등): 1초 + sessionStorage **30분** + localStorage **24시간**
	- **콘텐츠** (`/series/xxx`, `/camps/xxx` 등): 1초 + sessionStorage **5분** (기존 유지)
- 이유: 방문은 자주 보는 자신의 트래픽 제거, 콘텐츠은 반복 조회 데이터가 완화해야 인기 차트에 반영
- `isContentPath()` 트이용: `/^\/(series|camps|foods|items)\/[^/]+/`
- localStorage cleanup: 24시간 지난 `kydzm:pvd:*` 키 페이지 로드 시 자동 삭제
- Push: `17d73ae`, `520b3cc`
**콘텐츠 분석 필터링**
- 증상 (이미지 보고): 콘텐츠 진입 드롭다운에 `/#stories` (탭 방문) / 외부 링크에 카드 안 `인스타DM` (카드 클릭의 부산물) 노출
- 해결:
	- **콘텐츠 진입**: `isContentPath()` 필터로 콘텐츠 path만 → `/series/*`, `/camps/*`, `/foods/*`, `/items/*`
	- **외부 링크**: `context === '__external__'`만 필터 → 명시적 버튼 (인스타 프로필 / DM 보내기 / 메일 보내기 / 그래가파트너스 / Clip Creators)
	- 일별/월별/히트맵 빌드 함수 모두 동일 필터 적용
- Push: `dd1cee4`
**드롭다운 디자인 강조**
- 대상: 콘텐츠별 분석 카드의 분석 대샜 선택 드롭다운
- 증상: 토글(segmented)에 묻혀 잡이지 않음
- 개선:
	- 2px point 컴러 보더 + 랜딤우스 10px
	- 라벨 "🎯 분석할 콘텐츠/외부 링크 선택" 추가 (모드별 텍스트 자동 전환)
	- 폰트 14px / weight 600
	- 우측 chevron SVG 인라인 (point 색상)
	- hover/focus 시 그림자 elevation
- Push: `081317d`
---
## 14-15. ✅ 빌드 흐름 변경 정리 (260522 식별)
**운영가이드 5장/13-3의 빌드 흐름과 실제 현재 흐름이 다름**
### 이전 (운영가이드 5장)
```javascript
_build/camping-hub-v4-draft.html (진실소스 템플릿)
  + sync_data.json (노션 캐시)
  → build.py 실행 (re.sub lambda로 5개 placeholder 교체)
  → index.html 생성
  → GitHub push
```
### 실제 현재
```javascript
index.html (진실소스, 직접 수정)
  + data/{config,series,foods,items,camps}.json (동기화 대상)
  → 배포 시 런타임에 fetch로 로드
```
### 발견 경위
- 260521 작업 중 `_build/camping-hub-v4-draft.html`에 인스타 핸들러 적용 시간 경우 추적 코드 자체가 없음을 관찰
- 260522 점검: index.html 1582 lines vs _build 1035 lines (547줄 차이)
- index.html에는 `let siteConfig = {}; ... await fetch('./data/config.json')`으로 이미 런타임 fetch 방식
- _build의 placeholder `const siteConfig = {...}`는 적용 경로가 있는 채 안 쓰임
### 처리
- `_build/camping-hub-v4-draft.html` **보존** (과거 메모리/운영가이드 참조)
- `_build/README.md` **deprecated 명시** — "이 폴더는 더 이상 빌드에 사용되지 않음"
- Push: `081317d`
### 새 흐름 우영 절차
**HTML/CSS/JS 수정**: `index.html`을 직접 수정 → commit → push (GitHub Pages 자동 배포)
**노션 동기화**: data/\{config,series,foods,items,camps\}.json에만 주입
- camps.json (지역/계절/이미지 등)
- series.json (시리즈/EP)
- foods.json (추천 음식)
- items.json (추천 템)
- config.json (사이트 텍스트)
**그래서 13-3 "템플릿과 index.html 양쪽에 동일 변경" 년월파**
이제 index.html만 수정하면 됨. _build는 고도르지 않음.
→ 14-14 (3)의 _build/도 같이 수정한 건 안전 차원이지만 필수 아님
---
*14번 섹션 추가: 2026-05-21 / Worker v6 + admin 소타리즘 확장 완료: 2026-05-21*
---
## 14-16. 260522 후반 작업 (5개 카테고리 토글 + 커스텀 드롭다운 + 통일 뱃지 + 정렬 기능)
14-14 (6) "드롭다운 디자인 강조" 이후 연이은 작업 5건. admin UX 개선 + 메인 사이트 정렬 강화.
### (1) 5개 카테고리 토글 (콘텐츠별 분석)
- **기존**: 📄 콘텐츠 진입 / 🔗 외부 링크 (2개 토글)
- **신규**: 🎬 시리즈 / 🏕 캠핑장 / 🍖 음식 / 🛠 장비 / 🔗 기타 (5개 토글)
- `_analysisMode`: 'pageview'/'click' → 'series'/'camps'/'foods'/'items'/'external'
- `ANALYSIS_CATEGORIES` 메타 (key, label, pathRegex, isExternal)
- `getCandidatesForCategory()`: 카테고리별 후보 산출 통합
- 5등분 CSS: PC 12px / 모바일 11px, letter-spacing -0.02em
- 빈 카테고리 안내: "아직 🎬 시리즈 데이터가 없어요"
- Push: `210d877`
### (2) 커스텀 드롭다운 (div 기반)
- **증상**: 네이티브 `<select>`는 Android에서 글자 크기/줄바꿈 제어 불가 (`option` CSS 무시) → 큰 글자 + 자동 줄바꿈
- **해결**: button trigger + div panel 커스텀 드롭다운
	- 한 줄 유지 + `text-overflow: ellipsis`로 긴 EP 제목 자동 잘림
	- 모바일 11px / PC 13px
	- 옵션 우측에 누적 카운트 분리 표시
	- 바깥 클릭 시 자동 닫기
	- max-height 320px + 자체 스크롤
- Push: `8e8ef09`
### (3) 드롭다운 배지 통일 (인기 콘텐츠 TOP과 100% 동일)
- **이전**: 카테고리별 단일 컬러 배지 (캠핑장=회녹, 음식=빨강 등)
- **신규**: `renderDropdownBadge(mode, key)` 통합 함수
	- 🎬 시리즈: `cache.series.color` 인라인 style → 시리즈 본래 컬러 (노랑/빨강/녹색/파랑/핑크)
	- 🏕 캠핑장: `campPlatformBadgeHtml()` 호출 → 그래가/네이버/캠핏/땡큐
	- 🍖 음식: `sourcePlatformBadgeHtml()` 호출 → 쿠팡/컬리/네이버
	- 🛠 장비: `sourcePlatformBadgeHtml()` 호출 → 쿠팡/네이버 등
	- 🔗 기타: 회색 단일
- CSS: `.stats-platform-badge` → margin-right 8px / `.ca-cat-prefix.is-series` → `.stats-series-badge`와 동일 형태
- Push: `b65eee4`
### (4) 인기 콘텐츠 TOP 보강
- 시리즈 배지 PC truncate 제거 (모바일은 75px 유지) — PC에서 시리즈명 풀 텍스트
- foods/items에 `source` 필드(쿠팡/컬리/네이버) → 구매 플랫폼 컬러 배지 추가
- `resolveSource()` 헬퍼 추가 (campById/foodById/itemById 패턴)
- `sourcePlatformBadgeHtml(source)`: 쿠팡 #ee2c4d / 컬리 #5f0080 / 네이버 #03C75A / 카카오 #fee500 (배경) + #3b2e2e (텍스트)
- 등록일 표시 제거 (모바일 라벨 공간 확보)
- Push: `de9cf51`
### (5) 메인 사이트 랜덤 + 7일 신규 우선
- **사용자 명시**: "랜덤으로 설정된 곳에만" 적용 (현재 정렬이 아니라 사용자가 random으로 바꿨을 때)
- 적용 대상:
	- 시리즈 EP 중 `sort === 'random'`인 시리즈만 (ep_desc/ep_asc/manual은 그대로)
	- 음식/장비 (기본 random)
	- 캠핑장은 제외 (그래가→방문→가나다 일관성 세계 유지)
- `sortRecentFirst(arr, days = 7)` 헬퍼:
	- `created_at` 기준 7일 이내 → recent 그룹 (셔플)
	- 그 이외 (혹은 created_at 없음) → older 그룹 (셔플)
	- 반환: `[...recent, ...older]`
- admin random 모드 안내에 "✨ 최근 7일 이내 신규 EP는 항상 상위에 노출" 라인 추가 (사용자 인지 강화)
- Push: `d354048`, `d857f8a`
### (6) 음식/장비 정렬 기능 신설 (시리즈와 유사 패턴)
- **3개 모드**:
	- 🎲 랜덤 (기본): 랜덤 + 7일 신규 상위 (메인) / 입력 순서 그대로 (admin)
	- 🔝 최신순: `created_at` 내림차순
	- 📝 수동: 드래그앤드롭으로 순서 변경 (⋮⋮ 핸들)
- `config.json`에 `foodsSort`, `itemsSort` 필드 추가 (기본값 'random')
- `PRODUCT_SORT_MODES` 상수 (시리즈 SORT_MODES와 별도)
- `sortProductsByMode(arr, mode)` 헬퍼 (메인 사이트)
- `changeProductSort(type, newSort)`: config.json 즉시 commit
- `saveProductOrder(type, newOrder)`: foods.json/items.json 즉시 commit
- `renderProductList()`:
	- 정렬 드롭다운 헤더 추가
	- random 모드: "✨ 최근 7일 신규는 상위" 안내
	- manual 모드: ⋮⋮ 좌측 드래그 핸들 + Sortable.create
	- manual + 검색 중: 드래그 비활성화 + 노란 경고 박스
- `getSortedProductsForAdmin()`: 정렬 모드별 admin 표시 (manual/random은 입력 순서, latest는 created_at ↓)
- `productListItem()`에 `opts.manual` 시 `drag-handle--product` 추가
- `drag-handle--product` CSS (drag-handle--ep 패턴 동일, width/height 24px)
- Push: `eebc776`
### (7) 학습사항
- **네이티브 select의 한계**: Android 시스템 UI는 CSS 무시. 폰트 크기/줄바꿈 제어가 필요하면 커스텀 div 드롭다운이 유일 해결책
- **데이터 일관성 통합 패턴**: 같은 데이터 표시에서 다른 위치(인기 콘텐츠 TOP / 드롭다운)는 동일 함수 공유가 정답. renderDropdownBadge가 campPlatformBadgeHtml/sourcePlatformBadgeHtml 그대로 호출
- **"랜덤"이지만 신규 우선**: 사용자 UX 관점에서 흔한 요구. recent/older 그룹별 셔플 후 이어붙이는 게 단순하고 직관적. 7일 cutoff는 신규 EP 노출 기간으로 적절
- **drag-handle 검색 충돌**: 검색 활성화 + 드래그 모드 충돌 (필터된 결과만 보이는 상태에서 드래그 시 원본 인덱스 깨짐). 검색 중에는 명시적으로 비활성화하고 사용자에게 안내가 정답
- **config.json은 사이트 텍스트 + 정렬 설정의 통합 저장소**: 새 정렬 설정도 자연스럽게 config.json에 추가. 별도 파일 만들 필요 없음
### (8) 260522 Push 이력 (총 11건)
- `673b31e`: 일반 브라우저 anchor href 교체 + admin 핸들러
- `520b3cc`: 삼성 인터넷 intent + dedup 분리
- `17d73ae`: dedup 강화 (5분 → 30분 + 24시간)
- `dd1cee4`: 콘텐츠 분석 필터링 (path/**external**)
- `081317d`: 드롭다운 디자인 강조 + _build deprecated
- `210d877`: 5개 카테고리 토글
- `8e8ef09`: 커스텀 드롭다운 (div 기반)
- `de9cf51`: 시리즈 배지 PC 풀 텍스트 + 구매처 배지
- `b65eee4`: 드롭다운 배지 통일
- `d354048`, `d857f8a`: 메인 랜덤 + 7일 신규 우선
- `eebc776`: 음식/장비 정렬 기능
### (9) 다음 채팅 시작 가이드
새 채팅 첫 메시지 예시:
- "운영가이드 14-16 읽고 이어해줘" — 컨텍스트 자동 로드
- "음식 정렬 기능 어디서 변경?" — admin /#foods 헤더 드롭다운 안내
**Claude가 자동 수행**:
1. 운영가이드 14-16 fetch → 5개 카테고리 + 정렬 기능 컨텍스트 확보
2. `cd /home/claude && git clone gh-camping-hub` 으로 코드 복원
3. 작업 진행
---
## 14-17. 트러블슈팅 추가 (260522)
기존 14-12 트러블슈팅 리스트에 이번 작업 발견 사항 추가:
- **19. ✅ 네이티브 select Android CSS 제어 불가**: option 폰트/줄바꿈이 시스템 UI라 CSS 무시 → 커스텀 div 드롭다운 (button trigger + div panel) 으로 교체. 한 줄 + ellipsis 보장
- **20. ✅ 인기 콘텐츠 TOP vs 드롭다운 배지 불일치**: 같은 데이터인데 다른 시각 표현 → renderDropdownBadge() 통합 함수가 campPlatformBadgeHtml/sourcePlatformBadgeHtml 그대로 호출하도록 통일
- **21. ✅ 음식/장비 정렬 기능 부재 (260522 해결)**: 시리즈만 sort 필드 있고 음식/장비는 항상 랜덤 → config.json에 foodsSort/itemsSort 필드 추가 + PRODUCT_SORT_MODES 3개 + 드래그앤드롭 UI 신설
- **22. ⚠️ 검색 + 드래그 모드 충돌**: 검색 활성화 시 필터된 결과만 보이는데 드래그하면 원본 인덱스 깨짐 → 검색 중에는 드래그 비활성화 + 노란 경고 박스로 안내
---
*14-16\~14-17 추가: 2026-05-22*
---
## 14-18. _build/ 폴더 정리 + admin 오늘 활동 카드 + 🔥 7일 트렌딩 (260522 후반)
오늘 작업 마감 후 사용자 요청으로 3가지 개선 작업 진행. 운영 데이터 가시성 + 코드 정리.
### (1) _build/ 폴더 완전 제거 + _cache/로 이동
**문제**: 운영가이드 5장/메모리 #18에서 `_build/` 폴더를 빌드 진실소스로 명시했지만, 실제로는 이미 deprecated 상태. 새 채팅에서 혼란 유발.
**처리**:
- `_build/camping-hub-v4-draft.html` 삭제 (옛 템플릿, 547줄)
- `_build/README.md` 삭제
- `_build/sync_data.json` → **`_cache/sync_data.json`** 이동 (새 채팅 page_id 캐시 용도 보존)
- `_cache/README.md` 신설 (역할 안내 + 사용법)
- `tools/SYNC_GUIDE.md`의 `_build/` 참조 경로 갱신
- 메모리 #18 갱신 (새 복원 절차로)
**새 복원 절차** (이전 메모리 #18 → 갱신):
```bash
cd /home/claude && git clone https://github.com/kydxyz-git/camping-hub.git gh-camping-hub
cp gh-camping-hub/_cache/sync_data.json /home/claude/  # 노션 page_id 캐시
```
빌드 템플릿 복원 불필요 (이제 index.html 직접 수정 방식).
### (2) admin 상단 "오늘 활동" 미니 카드
**의도**: 매일 통계 보러 들어가지 않고도 한눈에 오늘 상태 파악.
**구성**:
- 위치: 요약 카드 4개 직후, 30일 차트 직전
- 디자인: linear-gradient 배경 (#f8fbf6→#f3f8f0) + point 컬러 left-border 3px
- 3개 지표 (좌→우):
	- **방문**: 콘텐츠 외 path 페이지뷰 (홈/탭 등) — `!isContentPath`
	- **카드 클릭**: 콘텐츠 path 페이지뷰 (/series/*, /camps/* 등) — `isContentPath`
	- **외부 링크**: `__external__` 클릭 (인스타 프로필/DM/메일/그래가/Clip Creators)
- 각 지표에 어제 대비 트렌드:
	- ↑ N% (5% 이상 증가)
	- ↓ N% (5% 이상 감소)
	- ─ (변화 미미)
	- 신규 ▲ (어제 0건이었던 신규)
- **🏆 오늘 인기 1위**: 콘텐츠 path 중 가장 많이 본 항목, path → cache lookup으로 이름 변환 (🎬 시리즈명/🏕 캠핑장명/🍖 음식명/🛠 장비명)
- 데이터 0건이면 "오늘 아직 콘텐츠 클릭이 없어요" 안내
**계산 로직**:
```javascript
const yesterday = new Date(todayDate);
yesterday.setDate(yesterday.getDate() - 1);
const todayData = data.daily[today] || { pv: 0, pages: {}, clicks: {} };
const yesterdayData = data.daily[yesterdayStr] || {...};

// 카드 클릭 vs 방문 구분
for (const [p, c] of Object.entries(todayData.pages || {})) {
  if (isContentPathFn(p)) todayCardViews += c;
  else todayVisits += c;
}
// 외부 링크는 __external__:: 접두사 키만
for (const [k, c] of Object.entries(todayData.clicks || {})) {
  if (k.startsWith('__external__::')) todayExternalClicks += c;
}
```
### (3) 🔥 최근 7일 트렌딩 카드 (인기 콘텐츠 TOP 위)
**문제**: 인기 콘텐츠 TOP은 누적 카운트만 기준 → 4월 EP가 계속 1위 (신규 EP 평가 불가).
**해결**: 별도 7일 트렌딩 카드 신설
- 위치: 인기 콘텐츠 TOP 카드 위 (먼저 보임)
- 디자인: linear-gradient 주황 (#fff8f3→#fff3eb) + #d97a3f left-border
- 시리즈/캠핑장/음식/장비 4개 카테고리 (popular와 동일 형태)
- `popular7d`: `data.daily` 최근 7일 pages 합산 → popular path별 lookup
- 데이터 없는 카테고리는 숨김 (조건부 렌더)
- 4개 합쳐 0건이면 카드 자체 숨김
**계산 패턴**:
```javascript
const recent7Pages = {};
for (let i = 0; i < 7; i++) {
  const dt = new Date(todayDate);
  dt.setDate(dt.getDate() - i);
  const dStr = dt.toISOString().slice(0, 10);
  const dayData = data.daily[dStr];
  for (const [p, c] of Object.entries(dayData.pages || {})) {
    recent7Pages[p] = (recent7Pages[p] || 0) + c;
  }
}
// popular 객체 (이미 name/url/플랫폼 정보 있음)에서 path 기준 lookup
for (const cat of ['camps', 'series', 'foods', 'items']) {
  for (const item of popular[cat]) {
    const c7 = recent7Pages[item.path] || 0;
    if (c7 > 0) popular7d[cat].push({ ...item, count: c7 });
  }
}
```
**인기 콘텐츠 TOP 카드**: 라벨에 "(누적)" 추가하여 트렌딩과 명확히 구분
### (4) 메인 사이트 sortRecentFirst와 패턴 일치
메인 사이트의 "랜덤 정렬 + 7일 신규 우선"과 admin 통계의 "7일 트렌딩" 모두 7일 cutoff 사용. 둘 다 `data.daily` 또는 `created_at` 기준이며 신규 EP를 사용자/관리자 양쪽에서 빠르게 노출/평가하는 일관 패턴.
### (5) Push 이력
- `78d4c66`: feat: 오늘 활동 카드 + 7일 트렌딩 + _build/ 폴더 정리 (3건 통합 commit)
### (6) 학습사항
- **누적 카운트의 한계**: 콘텐츠가 쌓이면 신규는 영영 1등 못 함. 시간 윈도우 기반 트렌딩 섹션 분리가 정답
- **path 기반 데이터 lookup**: `popular[cat]`에 이미 name/url/플랫폼 정보 있음 → 7d count로 재계산 시 path를 키로 재사용하면 매우 간단
- **카드 클릭 vs 방문 구분 패턴**: `isContentPath()` 정규식 하나로 통계/dedup/오늘 활동 카드 등 여러 곳에서 일관 사용 — 핵심 헬퍼
- **deprecated 폴더 보존 vs 제거**: 메모리/문서가 참조하더라도 코드와 어긋나면 결국 혼란. 제거하고 새 절차 명시 + 메모리 갱신이 정답. _cache/ 같이 의도 명확한 새 이름으로 이동하면 더 좋음
- **gradient 배경 + 컬러 left-border 조합**: 인기 콘텐츠 TOP 카드와 동일 패턴 — 통일성
---
*14-18 추가: 2026-05-22*
---
## 14-19. 통계 데이터 KST(UTC+9) 완전 전환 (260522 추가)
### 발견된 문제
기존 코드의 일별 집계가 UTC 기준으로 작동 → KST 0\~9시 데이터가 전날로 들어가는 버그:
<table header-row="true">
<tr>
<td>시각 (KST)</td>
<td>시각 (UTC)</td>
<td>UTC 키</td>
<td>KST 키</td>
<td>문제</td>
</tr>
<tr>
<td>2026-05-22 08:00</td>
<td>2026-05-21 23:00</td>
<td>2026-05-21</td>
<td>2026-05-22</td>
<td>UTC 키로 저장되어 어제로 분류</td>
</tr>
<tr>
<td>2026-05-23 03:00</td>
<td>2026-05-22 18:00</td>
<td>2026-05-22</td>
<td>2026-05-23</td>
<td>동일</td>
</tr>
<tr>
<td>2026-05-22 18:00</td>
<td>2026-05-22 09:00</td>
<td>2026-05-22</td>
<td>2026-05-22</td>
<td>정상 (KST 9시 이후)</td>
</tr>
</table>
**증상**:
- admin 오늘 활동 카드의 "오늘" 카운트가 KST 09시 전엔 0으로 보임
- 30일 차트의 날짜 라벨이 KST와 어긋남
- 시간대 히트맵은 이미 KST 기준이라 일관성 깨진 상태
### 해결: 클라이언트 + Worker 양쪽 KST 헬퍼 통일
**클라이언트 (kydzm/index.html)**:
```javascript
const KST_OFFSET_MS = 9 * 60 * 60 * 1000;

// Date → KST 기준 YYYY-MM-DD
function kstDateStr(d) {
  return new Date(d.getTime() + KST_OFFSET_MS).toISOString().slice(0, 10);
}
function kstToday() { return kstDateStr(new Date()); }
function kstDateFromStr(s) { return new Date(s + 'T00:00:00+09:00'); }
```
모든 `toISOString().slice(0, 10)` 호출을 `kstDateStr()` / `kstToday()`로 교체:
- renderStats today/todayDate
- 7일 트렌딩 dStr
- 30일 차트 chartDates
- 오늘 활동 yesterdayStr
- buildDailySeriesFromEvents (localDateStr 통합)
- 시간대 히트맵 (getDay/getHours → KST_OFFSET 명시)
- 시리즈 EP 추가 시 sitemap lastmod
**Worker (worker-v6.js)**:
```javascript
const KST_OFFSET_MS = 9 * 60 * 60 * 1000;

function isoDate(d) {
  return new Date(d.getTime() + KST_OFFSET_MS).toISOString().slice(0, 10);
}

// scheduled cleanup: KST 0시 = UTC 15시
if (now.getUTCHours() === 15) ctx.waitUntil(cleanupOldData(env));

// buffer flush 시 hour도 KST 기준
const kst = new Date(e.ts + KST_OFFSET_MS);
const hour = kst.getUTCHours();
```
### 마이그레이션
**옵션 A 채택 (완전 KST 전환)**. 기존 UTC 키들을 KST 키로 재집계하는 일회성 엔드포인트 추가:
```javascript
POST /migrate-kst
Header: X-Sync-Token: <SYNC_TOKEN>
```
동작:
1. KV에서 모든 `events:*` raw 키 수집 (60일치)
2. 각 이벤트의 epoch ts를 KST 기준으로 다시 묶기
3. aggregate.daily를 KST 기준으로 통째로 교체
4. 백업: `kydz-stats-aggregate:backup-pre-kst` 키로 원본 daily 보존
5. agg.kst_migrated_at 타임스탬프 기록
**반환 예시**:
```json
{
  "ok": true,
  "eventDatesScanned": 12,
  "eventsProcessed": 487,
  "newDailyKeyCount": 13,
  "backupKey": "kydz-stats-aggregate:backup-pre-kst",
  "note": "..."
}
```
### 배포 절차
1. **클라이언트**: 이미 push 완료 (commit `31b95ab`). GitHub Pages 자동 배포 1\~5분
2. **Worker**: Cloudflare 대시보드에서 `worker-v6.js` 재배포 필요
	- Workers → kyd-stats → Quick Edit
	- `/mnt/user-data/outputs/worker-v6.js` 내용 전체 붙여넣기
	- Save and Deploy
3. **마이그레이션** (Worker 배포 후 1회):
	```bash
curl -X POST "https://kyd-stats.kydxyz.workers.dev/migrate-kst" \
  -H "X-Sync-Token: <SYNC_TOKEN>"
	```
4. **검증**: admin 새로고침 → 오늘 활동 카드 + 30일 차트 KST 기준 확인
### 영향 범위
<table header-row="true">
<tr>
<td>항목</td>
<td>영향</td>
</tr>
<tr>
<td>오늘 활동 카드</td>
<td>KST 0시부터 정확히 "오늘" 시작 ✅</td>
</tr>
<tr>
<td>어제 대비 트렌드</td>
<td>정확 ✅</td>
</tr>
<tr>
<td>30일 차트</td>
<td>KST 날짜 라벨 ✅</td>
</tr>
<tr>
<td>시간대 히트맵</td>
<td>명시적 KST (브라우저 로컬 의존성 제거) ✅</td>
</tr>
<tr>
<td>7일 트렌딩 카드</td>
<td>정확 ✅</td>
</tr>
<tr>
<td>메인 사이트 sortRecentFirst</td>
<td>영향 없음 (epoch ms 직접 비교)</td>
</tr>
<tr>
<td>새 EP push 시 sitemap lastmod</td>
<td>KST 날짜 ✅</td>
</tr>
</table>
### 학습사항
- **toISOString()은 항상 UTC**: `new Date().toISOString()`은 timezone 무관하게 UTC 문자열 반환. 한국 한정 서비스라면 첫 설계부터 KST 헬퍼 필수
- **`getHours()`****는 브라우저 로컬**: 사용자 브라우저가 KST 환경이면 동작은 맞지만, 해외 출장 등에서 깨질 수 있음. 명시적 KST 변환이 안전
- **단순한 +9시간 트릭**: `new Date(ts + KST_OFFSET_MS).toISOString().slice(0, 10)` → KST 날짜 문자열 추출 가장 간단한 방법
- **scheduled cron의 시각**: Cloudflare Workers cron은 UTC 기준 트리거. KST 자정 정리하려면 UTC 15시
- **마이그레이션 백업 키**: KV에서 `:backup-pre-kst` 접미사로 원본 보존. 잘못되면 복구 가능
### Push 이력
- 클라이언트: `31b95ab` (kydzm/index.html)
- Worker: 사용자 Cloudflare 수동 배포 + `/migrate-kst` 1회 호출
---
*14-19 추가: 2026-05-22*
---
## 14-20. 한글 IME 검색 버그 + 조회 버튼 도입 (260522 마무리)
### 발견 증상
이미지 보고: admin 캠핑장 검색창에 "소풍" 입력 시 `ㅅㅗㅍㅜㅇ` 자모 분리 상태로 깨짐 → 0건 결과.
### 1차 시도 (실패): compositionstart/end
```javascript
let _isComposing = false;
search.addEventListener('compositionstart', () => { _isComposing = true; });
search.addEventListener('compositionend', (e) => {
  _isComposing = false;
  setSearch(e.target.value);
  rerender();
});
```
→ **여전히 깨짐**. 이유는 input 자체가 새로 생성되니까 IME 컨텍스트가 끊기는 본질적 문제.
### 최종 해결: 조회 버튼 방식
**핵심 원리**: 입력 즉시 rerender 안 하면 IME 깨질 일 없음.
```javascript
const doSearch = () => {
  setSearch(input.value);
  rerender();  // 명시적 트리거에서만 실행
};
btn.onclick = doSearch;

// 엔터키 → 조회 버튼 자동 (한글 조합 중 엔터는 무시)
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.isComposing) {
    e.preventDefault();
    doSearch();
  }
});
```
**`!e.isComposing`**** 체크가 핵심**:
- 한글 조합 중 엔터 → 단순 한글 확정 (rerender X, IME 안 깨짐)
- 조합 완료 후 엔터 → 조회 실행
### UI 디자인 (시행착오)
<table header-row="true">
<tr>
<td>시도</td>
<td>결과</td>
</tr>
<tr>
<td>var(--point) 연녹색 + 13px</td>
<td>너무 흐려서 안 보임 (이미지 1)</td>
</tr>
<tr>
<td>진한 검정 + 14px + 40px height</td>
<td>너무 큼 (이미지 2)</td>
</tr>
<tr>
<td>0 10px / 30px height</td>
<td>너무 작음 (이미지 3)</td>
</tr>
<tr>
<td>**flex stretch + min-height 제거**</td>
<td>정답 ✅ — input 높이에 자동 맞춤</td>
</tr>
</table>
**최종 CSS**:
```css
.search-bar {
  display: flex; gap: 8px;
  align-items: stretch;  /* ← 핵심 */
}
.search-bar-btn {
  padding: 0 16px;
  background: #1a1a1a;
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  /* height 명시 X — stretch가 자동으로 input과 같은 높이로 맞춤 */
}
@media (max-width: 480px) {
  .search-bar { gap: 6px; }
  .search-bar-btn { padding: 0 14px; font-size: 13px; font-weight: 600; }
}
```
### 적용 위치
- 캠핑장 검색 (`/#camps`, `camp-search` + `camp-search-btn`)
- 음식 검색 (`/#foods`, `prod-search` + `prod-search-btn` 공용)
- 장비 검색 (`/#items`, 동일 공용 핸들러)
### Push 이력
- `973d474`: compositionstart/end 1차 시도 (실패)
- `c243c2c`: 조회 버튼 + 엔터키 도입
- `fb6bf86`: 시인성 강화 (검정+흰글씨)
- `a6597e8`, `d251386`: 사이즈 조정 시행착오
- `728776e`: flex stretch 최종 (PC/모바일 분기)
### 학습사항
- **한글 IME + DOM 재생성은 본질적으로 충돌**: input 요소가 새로 만들어지는 순간 IME 조합 상태가 끊김. compositionend로 대응해도 화면에 자모 분리가 잠시 보이는 시각적 깜빡임은 못 막음. 명시적 트리거(버튼/엔터) 방식이 가장 안전
- **`e.isComposing`****은 keydown에서 유효**: 한글 조합 중 엔터 = 단순 확정으로 처리해야 자연스러움. `!e.isComposing` 체크 필수
- **flex stretch는 높이 정렬의 정답**: align-items: stretch + height 명시 안 함 → input 높이에 자동 맞춤. 디바이스/브라우저/폰트 변화에 자동 대응. min-height 명시는 오히려 어긋남
- **모바일 분기는 padding + 폰트만으로 충분**: 높이는 stretch가 자동 처리하니까 모바일에선 padding/font만 살짝 줄이면 충분
- **시인성 첫째, 디자인 둘째**: 처음 var(--point)는 연녹색이라 거의 안 보임. 액션 버튼은 강한 대비(검정+흰글씨)가 정답
---
*14-20 추가: 2026-05-22*
---
## 15. 260811\~260812 대개편 (v3 실험 → 폐기 → index.html 전면 개편)
이틀에 걸친 긴 세션. 캠핑한끼([campinghankki.com](http://campinghankki.com)) 벤치마킹에서 출발해 별도 사이트 v3를 만들었다가 **폐기하고, 거기서 검증된 요소만 index.html에 이식**하는 흐름으로 마무리.
### 15-1. v3 실험과 폐기 결정
> ⚠️ **폐기** — v3 실험 폐기. `v3.html`은 미사용.
**출발점**: 캠핑한끼 사이트 분석. 구조가 Recipes(21개, 유입 자산) / Outdoor Gear / Camera Gear / Contact 4메뉴. 레시피가 검색 유입을 만들고 장비가 수익을 담당하는 구조.
**만든 것**: `v3.html` — 메인 페이지 분리(일러스트 카드 5장) + 캠핑장 상세(`camp.html`) + 영상모음 2뎁스 + 소개협업 플립 카드. 라인 일러스트 4종 + 프로필 2종(라인/컬러)을 ChatGPT로 제작.
**폐기 이유**:
- 스토리 투표 8:2로 기존 사이트 우세 (표본은 작지만 신호)
- 나란히 비교(preview 비교 모드)에서 **첫 화면 열세가 명확**. 기존은 들어오자마자 릴스 썸네일이 보이는데 v3는 헤드라인+일러스트만 보이고 콘텐츠까지 스크롤 필요
- 하위 페이지 구조는 v3가 우수했으나, 한 화면 차이로 전체를 바꾸긴 어려움
**결론**: v3 폐기, **index.html 단일 운영**. v3에서 검증된 것만 이식.
**남은 파일**: `v3.html`, `camp.html`은 저장소에 남아있으나 미사용. `preview.html`은 index 전용으로 정리해 계속 사용.
### 15-2. index.html 개편 내역
**(1) 메뉴명 변경** — config.json
- `tab3`: 추천 음식 → **먹거리**
- `tab4`: 추천 템 → **캠핑용품**
- `tab5`(캠핑여지도): 버튼 `display:none` 처리 (코드는 보존)
- 사유: "추천"은 광고 톤. 사실 서술형이 계정 톤에 맞음
**(2) 지역 선택 UI 신설**
- 기존 `Landscape`(바다/산/숲/계곡...) 섹션을 **REGION**으로 교체
- 전국 9개 도 전부 표시 (경기·강원·충북·충남·전북·전남·경북·경남·제주) + 전체
- **아이콘 = 실제 행정구역 지도 SVG**. `southkorea-maps` GeoJSON에서 shapely로 단순화(`simplify(0.06)`) 후 24x24 viewBox path 추출
- 5열 2행, **단일 선택**, 미방문 지역은 `opacity:.42`
- 필터에서 지역·시즌 행 제거 → **기타 태그(→"태그")만 남김**
**(3) 제품 카드 단순화**
- 부가설명·가격·할인율·구매하기 버튼 전부 제거 → **사진 + 이름 + 배지**만
- 가격 안내 문구(`priceNotice`) 및 "가격·정보 최종 업데이트" 표기 제거
- 캠핑용품은 **세부 분류별 그룹 렌더**(`renderItemGroups`)
**(4) 배지 체계 정리**
- **PICK(추천)**: 노란 별 SVG(#FFC93C, 검정 테두리 0.45), 카드 **좌상단**
- **판매처/예약처**: 카드 **우하단** (캠핑장·제품 동일 배치)
- 판매처에 **알리(#FF4747)·테무(#FF6A00)** 추가, 미인식 도메인은 "기타"
- 캠핑장 예약 배지 원본 규격 복원: 그래가 #1a1a1a / 네이버 #03C75A / 캠핏 #2D8F4C / 땡큐캠핑 #FF6B2C / 기타 #9e9e9e, 8px 알약형
**(5) 캠핑장 팝업에 특징 메모**
- 클릭 팝업 상단에 `notes`를 노란 점 리스트로 표시
- **릴스 없어도 메모만 있으면 팝업 노출** (조건 확장: 17곳 → 28곳)
- 아래에 릴스 목록 + 예약 링크
**(6) 협업 페이지 신설 (****`collab.html`****)**
- 헤더 타이틀 아래 배지 링크 + 푸터 CTA(**"공대남자 소개 · 협업 문의하기"** 단일 버튼, 기존 DM/메일 2버튼 대체)
- 구성: CHANNEL(인스타·페북·네이버클립·[kydz.kr](http://kydz.kr) 4개) / PROCESS(5단계) / NOTE(3항목) / DM·메일 CTA
- 채널 아이콘은 브랜드 컬러 SVG 직접 작성 (원본 파일이 흑백이라 흰 배경에서 안 보임)
- **그래가 파트너스는 제휴이지 운영 채널이 아니므로 제외**
**(7) 기타**
- 먹거리·캠핑용품 상단에 설명 박스(위아래 선만, 중앙 정렬) + `(⭐ 추천)` 범례
- 제품 이미지에 `?v={updated_at}` 캐시 무효화 → 이미지 교체 즉시 반영
- 링크 없는 제품은 `<a>` 대신 `<div>` 렌더 (href="#"로 인한 상단 스크롤 방지)
### 15-3. admin 기능 추가 (kydzm/index.html)
<table header-row="true">
<tr>
<td>기능</td>
<td>설명</td>
</tr>
<tr>
<td>**장비 세부 분류 관리**</td>
<td>`config.itemCats` 배열. 목록 화면에서 추가/이름변경/순서변경/삭제. 제품이 있는 분류는 삭제 차단</td>
</tr>
<tr>
<td>**분류별 접이식 목록**</td>
<td>장비 목록을 분류별 그룹으로 접기/펼치기. 첫 그룹만 기본 열림. 검색·수동정렬 시엔 평면 목록</td>
</tr>
<tr>
<td>**대표 이미지 선택**</td>
<td>이미지마다 라디오. `main_img` 저장. 첫 장이면 저장 안 함</td>
</tr>
<tr>
<td>**이미지 노출 위치**</td>
<td>위/가운데/아래 드롭다운 → `img_pos`</td>
</tr>
<tr>
<td>**소개 게시물 연결**</td>
<td>시리즈 43편 드롭다운 선택 + "기타(직접 입력)" → `video`</td>
</tr>
<tr>
<td>**PICK 체크박스**</td>
<td>장비·캠핑장 각각 `pick: true`</td>
</tr>
<tr>
<td>**캠핑장 INFO 항목**</td>
<td>입실/퇴실/주소/특징메모/명당DM안내</td>
</tr>
<tr>
<td>**장비 URL 필수 해제**</td>
<td>링크 없이도 등록 가능</td>
</tr>
<tr>
<td>**판매처 자동 판별 강화**</td>
<td>저장 시 URL 기준으로 항상 재판정. 수동 "기타"가 쿠팡 링크를 덮어쓰던 버그 수정</td>
</tr>
</table>
### 15-4. 데이터 변경
**캠핑용품 41개 등록** (분류별)
- 물놀이용품 4 / 촬영장비 8 / 텐트 8 / 타프 6 / 테이블·체어 9 / 화로·난방 3 / 수납·기타 2 / 소모품 1
- 분류 목록(11개): 물놀이용품·촬영장비·텐트·타프·테이블·체어·침구·화로·난방·주방용품·조명·전기·수납·기타·소모품
- `itemsSort`: **random** (7일 이내 신규 상위)
- 대부분 구매 링크 미등록 상태 (배지·클릭 없음)
**캠핑장 필드 정리**
- **삭제**: `landscape`(지형), `seasons`(계절), `sites`(사이트구성), `price`(요금)
- **추가**: `pick`(추천), `checkin`/`checkout`, `address`, `notes`, `dm`(명당 DM 안내)
- **백업 위치**: `/mnt/user-data/outputs/camps_backup_260812.json`(전체) + `camps_removed_fields_260812.csv`(삭제 항목만)
- ⚠️ 지형 삭제로 **사진 없는 캠핑장 대체 화면 색이 단일 톤으로 통일**됨
**캠핑장 정보 보강** (여지도 PDF + 노션 + 웹검색)
- 주소 36곳 / 입퇴실 26곳 / 특징메모 28곳 / PICK 19곳 / DM안내 9곳
- 출처: 캠핑여지도 경북 23곳, 노션 DM 페이지(봉화별·단양소풍·우니메이카·반달·구만산장·지리산365·덕풍계곡·산청별천지), 웹검색(합천호코지·황매산별쿵·산중오토 등)
- **공개 기준**: 노션에 세워둔 원칙 그대로 — 캡션에 공개한 정보(주소·입퇴실·사이트 구성)만 사이트에, **명당 자리 번호·계곡 포인트는 DM 전용 유지**
### 15-5. 미해결 / 다음 작업
- [ ] **CSV 일괄 정리 대기**: `/mnt/user-data/outputs/camps_260812.csv` (14개 열, 66행). 사용자가 수정 후 재전달 예정
- [ ] **지역 없는 캠핑장 10곳**: 교육청수련원·나조스트·캠프하다·캠핑느루·안녕오토캠핑장·바람이좋은저녁캠핑장·너와두리농촌캠핑장·산중오토계곡캠핑장·하늘하루펜션앤캠핑장·달서별빛캠핑장 → 지역 미상이라 검색 어려움, 사용자 확인 필요
- [ ] **주소 없는 캠핑장 30곳**
- [ ] **캠핑용품 구매 링크 대량 미등록** (텐트·타프·테이블·체어 등)
- [ ] **헤더 협업 배지 문구** 재검토 (푸터는 "공대남자 소개 · 협업 문의하기"로 확정)
- [ ] **collab.html PROCESS 5단계 → 3단계 축약** 제안했으나 미결정
- [ ] v3.html / camp.html 정리 여부 (현재 방치)
### 15-6. 학습사항
- **첫 화면이 전부다**: 하위 구조가 아무리 좋아도 첫 화면에서 콘텐츠가 안 보이면 진다. v3 폐기의 결정적 이유
- **일러스트는 ChatGPT, 픽토그램은 Claude 한계**: Claude가 SVG로 그리는 건 도형 조합 수준. 풍경 일러스트는 ChatGPT에 프롬프트를 주는 게 정답. 단 **행정구역 지도처럼 좌표 데이터가 있는 건 Claude가 정확**
- **일러스트 프롬프트 핵심**: 배경색·선색·채색 비율(30% 이하)·하단 여백 30%를 명시. "촘촘하게"는 과밀, "최소한으로"는 과소 → 밀도는 말로 조절이 어려움
- **배지는 적을수록 좋다**: 사진 위 요소 2개가 한계. PICK 좌상단 + 판매처 우하단으로 고정
- **`href="#"`****의 함정**: 클릭 핸들러로 막아도 브라우저가 상단으로 스크롤. 링크 아닌 카드는 `<div>`로 렌더해야 함
- **캐시 무효화는 ****`updated_at`**** 기반**: 파일명이 같으면 이미지를 바꿔도 브라우저가 옛것을 씀. `?v={timestamp}`가 정답
- **저장 시 파생값 재계산**: source처럼 URL에서 도출되는 값은 입력 시점이 아니라 **저장 시점에 항상 재판정**해야 수동값이 굳지 않음
- **삭제 전 백업은 CSV+JSON 이중으로**: 되살릴 방법이 백업뿐인 필드는 전체 스냅샷과 해당 필드만 뽑은 CSV를 함께 남김
### 15-7. 다음 채팅 시작 가이드
> "운영가이드 15장 읽고 이어해줘"
주요 진입점:
- CSV 반영: "camps CSV 수정했어" → `data/camps.json`에 병합 (id 기준 매칭, `landscape`/`seasons`/`sites`/`price`는 이미 삭제된 필드)
- 캠핑용품 추가: 이미지 + 이름 + 분류 알려주면 등록 (링크는 선택)
- 협업 페이지 수정: `collab.html` 직접 수정
- 미리보기: `https://kydz.kr/preview.html` (모바일 기본, 자동 새로고침 5초)
---
*15장 추가: 2026-08-12*
