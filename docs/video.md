# 캠핑장 페이지 영상 (직접 올리기, 261031)

릴스를 캠핑장 페이지 **안에서 재생**되게 해서 구글 동영상 검색에 kydz.kr 이름으로 잡히게 한다.
구글은 페이지에서 실제로 재생되는 영상만 동영상으로 본다 — 인스타 링크 카드·인스타 embed는 안 됨(인스타가 영상 수집을 막음), MYBOX 공유 링크도 안 됨(파일 주소가 아니고 만료됨).

## 구조

- 영상 파일: **Cloudflare R2** 버킷 `kydz-media` (무료 10GB, 전송 요금 없음) → 공개 주소 `https://{공개 주소}/v/{파일}.mp4`
- 원본: 네이버 MYBOX(PC) — R2에는 줄인 파일만
- 데이터: 시리즈 EP(`data/series.json`)나 캠핑장 `videos[]`(`data/camps.json`)에 필드 두 개
  - `mp4`: R2 공개 주소
  - `uploaded`: 인스타에 올린 날 `YYYY-MM-DD` (EP는 없으면 `created_at` 날짜를 씀, 캠핑장 `videos`는 필수)
- 렌더: `tools/build_pages.py`(정적 `/camps/{이름}/`)와 `camp.html`이 `mp4`가 있으면 `<video>` 플레이어(포스터 = 썸네일, `preload="none"`) + 인스타 링크, 없으면 예전처럼 썸네일 카드
- 구조화 데이터 `VideoObject`는 **`mp4`·썸네일·날짜가 다 있는 영상만** (name·description·thumbnailUrl·uploadDate·contentUrl). 링크 카드에 VideoObject를 붙이지 않는다 — 서치 콘솔 'thumbnailUrl/uploadDate 누락' 경고 원인이었음(261031).

## R2 처음 한 번 (사용자, Cloudflare 대시보드)

1. Cloudflare 대시보드 → **R2 Object Storage** → (처음이면 결제 수단 등록 — 무료 범위 안에선 청구 없음) → **Create bucket** → 이름 `kydz-media`, 위치 자동
2. 버킷 → **Settings** → **Public access** → **R2.dev subdomain** 허용 → 나오는 `https://pub-….r2.dev` 주소를 이 문서 '공개 주소'에 적기: `(아직 미정)`
   - r2.dev는 Cloudflare가 '개발용(속도 제한)'이라고 함. 영상이 많이 재생되면 나중에 Worker(`*.workers.dev`)로 R2를 내보내는 방식으로 바꾼다 (kydz.kr DNS가 가비아라 사용자 도메인 연결은 안 됨).
3. 키·토큰은 저장소에 넣지 않는다. 올리기는 PC에서 `wrangler login`(브라우저 로그인) 방식.

## 영상 하나 올리기 (PC Claude)

1. MYBOX에서 그 릴스 원본 영상을 찾는다 (없으면 사용자에게 파일을 받는다).
2. 줄이기 (ffmpeg): 세로 720px 폭, 웹 재생용
   ```
   ffmpeg -i 원본.mp4 -vf "scale=720:-2" -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 96k -movflags +faststart 결과.mp4
   ```
   파일 이름: 시리즈 EP는 EP `id`(예: `ep_99fc18b86c.mp4`), 캠핑장 영상은 `{캠핑장 id}-{번호}.mp4`. 한 번 올린 이름은 바꾸지 않는다(구글이 그 주소로 기억) — 영상을 바꾸면 새 이름.
3. 올리기: `npx wrangler r2 object put kydz-media/v/ep_99fc18b86c.mp4 --file 결과.mp4 --content-type video/mp4 --remote`
4. 데이터: 해당 EP(또는 캠핑장 `videos` 항목)에 `mp4`·`uploaded` 추가 + `updated_at` 갱신 → 커밋 `update(code): {이름} 영상 연결` → main. 정적 페이지는 Actions가 다시 만든다.
5. 확인: `/camps/{이름}/`에서 재생되는지, 구글 '리치 결과 테스트'에 그 주소를 넣어 동영상이 잡히는지.

## 우선순위

조회 잘 나온 캠핑장 릴스 5~10개로 시작 → 서치 콘솔 '동영상 페이지'에 잡히는지 2~3주 보고 넓힌다.
