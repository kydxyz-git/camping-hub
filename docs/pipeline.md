# 공대남자(@kyd_zm) 전체 운영 지도

> 261030 · 무엇이 수동이고 무엇이 자동으로 돌아서, 어떤 경로로 수익까지 가는가.
> 미리보기·편집: [`docs/pipeline.html`](pipeline.html) (같은 소스, 왼쪽 소스 / 오른쪽 그림). 비공개 저장소는 '무엇을 하는지'까지만 적는다 — 토큰·쿠팡 링크·수익 실적 숫자는 넣지 않음.

색: 노랑 사용자 · 파랑 Claude · 회색 시스템 자동 · 보라 정보 소스 · **초록(굵은 테두리) 쌓이는 자산** · 분홍 채널·유입 · 주황 수익 · 하늘 점선 파트너·미정

## 1. 전체 지도

```mermaid
flowchart LR
  subgraph CH["채널"]
    direction TB
    IG["인스타 @kyd_zm<br/>릴스(주력) · 게시물 · 꿀템방<br/>Meta Verified"]:::in
    FB["페이스북<br/>릴스 교차게시"]:::in
    CLIP["네이버 클립<br/>재업로드 + 브랜드커넥트 링크"]:::in
    BLOG["네이버 블로그<br/>후기 (신규)"]:::in
    TH["스레드 · 쿠파스<br/>겨울 집 관리 · 별도 라인"]:::in
    YT["유튜브 (고민 중)"]:::partner
  end

  subgraph INFLOW["유입"]
    direction TB
    DM["소셜비즈 DM<br/>댓글 키워드 → 1차 팔로우 → 2차 링크"]:::in
    SE["구글 · 네이버 검색"]:::in
  end

  HUB[["kydz.kr<br/>캠핑장 · 장비 · 먹거리 · 시리즈(릴스 모음)"]]:::page

  subgraph DEAL["협찬 창구"]
    direction TB
    MK["소셜비즈 마켓 · 아하크리에이터<br/>네이버(푸드 제안만)"]:::src
    MAIL["협찬 메일 → Apps Script 10분<br/>→ 카카오 · 캘린더 · 노션 대장"]:::sys
    META["메타 크리에이터 마켓 (미등록)"]:::partner
  end

  subgraph MONEY["수익"]
    direction TB
    SPON["협찬 · 광고비 · 서포터즈<br/>건당"]:::money
    CP["쿠팡파트너스<br/>클릭 · 구매"]:::money
    NBC["네이버 브랜드커넥트<br/>클릭 · 구매"]:::money
    KUR["컬리 큐레이터<br/>먹거리 일부"]:::money
    CC["클립 크리에이터<br/>월 게시글 2 + 영상 10 → 월 10만원 고정"]:::money
    VIEW["조회수 수익 (예정)<br/>FB 팔로워 1,633 → 1만 · 28일 유효조회 14.6만 → 15만<br/>클립 팔로워 467 → 1,000 · 90일 유효조회 45만 → 300만"]:::partner
  end

  GR["그래가 파트너<br/>수익 ✕ · 예약 유입 계속"]:::partner

  IG --> DM --> HUB
  IG -. 교차게시 .-> FB
  IG -. 재업로드 .-> CLIP
  SE --> HUB
  SE --> BLOG
  BLOG -- 본문 링크 --> HUB
  HUB -- 릴스 모음 · 시리즈 --> IG
  HUB --> CP
  HUB --> NBC
  HUB --> KUR
  HUB -. 예약 .-> GR
  TH --> CP
  CLIP --> NBC
  CLIP --> CC
  FB -.-> VIEW
  CLIP -.-> VIEW
  MK --> SPON
  MAIL --> SPON
  IG -- 협찬 콘텐츠 --> SPON

  classDef user    fill:#FFF3C4,stroke:#B7791F,color:#1a1a1a
  classDef ai      fill:#E3F2FD,stroke:#1E63B4,color:#1a1a1a
  classDef sys     fill:#EEEEEE,stroke:#616161,color:#1a1a1a
  classDef src     fill:#F3E8FF,stroke:#6B21A8,color:#1a1a1a
  classDef page    fill:#DCFCE7,stroke:#15803D,color:#1a1a1a,stroke-width:3px
  classDef in      fill:#FFE4E6,stroke:#BE123C,color:#1a1a1a
  classDef money   fill:#FFEDD5,stroke:#C2410C,color:#1a1a1a
  classDef partner fill:#E0F2FE,stroke:#0369A1,color:#1a1a1a,stroke-dasharray:5 4
```

## 2. 콘텐츠 1건 흐름

```mermaid
flowchart TB
  subgraph MAKE["① 만들기"]
    direction LR
    A["캠핑 · 촬영<br/>[수동]"]:::user
    B["릴스 편집<br/>Claude Code + HyperFrames + kyd-reels<br/>[반자동]"]:::ai
    C{"캡션 · DM 문구 확정<br/>[수동]"}:::user
    A --> B --> C
  end

  subgraph UP["② 올리기 — 업로드에서 갈라짐"]
    direction LR
    D["인스타 업로드<br/>릴스 · 게시물<br/>[수동]"]:::user
    E["소셜비즈 키워드 · 2차 DM 세팅<br/>[수동]"]:::user
    F["페이스북 교차게시<br/>[반자동]"]:::sys
    G["네이버 클립 재업로드<br/>+ 브랜드커넥트 링크 [수동]"]:::user
    D --> E
    D --> F
    D --> G
  end

  subgraph PAGE["③ 쌓기"]
    direction LR
    H["admin 등록 · 시리즈 · 캠핑장 정보<br/>Claude가 정리 [반자동]"]:::ai
    I["GitHub main 커밋 → Actions build-pages<br/>[자동]"]:::sys
    K[["kydz.kr 페이지<br/>캠핑장 · 장비 · 먹거리 · 릴스 모음"]]:::page
    L["네이버 블로그 복붙본<br/>Claude 작성 [반자동]"]:::ai
    M["블로그 발행<br/>[수동]"]:::user
    N[["네이버 블로그 글"]]:::page
    H --> I --> K
    L --> M --> N
    N -- 본문 링크 --> K
  end

  subgraph VIEWER["④ 보는 사람"]
    direction LR
    V1["댓글 키워드"]:::in
    V2["1차 DM 팔로우 → 2차 DM 홈페이지 링크<br/>[자동]"]:::sys
    V3["구글 · 네이버 검색"]:::in
    V1 --> V2
  end

  subgraph MONEY["⑤ 수익"]
    direction LR
    M1["쿠팡파트너스"]:::money
    M2["네이버 브랜드커넥트"]:::money
    M3["컬리 큐레이터"]:::money
    GR["그래가 예약 유입<br/>수익 ✕ · 파트너"]:::partner
  end

  subgraph REPORT["⑥ 성과 — 월말 + 수시"]
    direction LR
    R1["IG 인사이트 CSV<br/>[수동]"]:::user
    R2["Claude 분석<br/>[반자동]"]:::ai
    R3["admin 인사이트 · insights.json<br/>→ 다음 콘텐츠 기획"]:::sys
    R1 --> R2 --> R3
  end

  C --> D
  C --> H
  C --> L
  D --> V1
  V2 --> K
  V3 --> K
  V3 --> N
  G --> M2
  K --> M1
  K --> M2
  K --> M3
  K -.-> GR
  K -- 릴스 모음 · 시리즈 → 다시 인스타 --> D
  D -. 며칠 뒤 .-> R1

  classDef user    fill:#FFF3C4,stroke:#B7791F,color:#1a1a1a
  classDef ai      fill:#E3F2FD,stroke:#1E63B4,color:#1a1a1a
  classDef sys     fill:#EEEEEE,stroke:#616161,color:#1a1a1a
  classDef src     fill:#F3E8FF,stroke:#6B21A8,color:#1a1a1a
  classDef page    fill:#DCFCE7,stroke:#15803D,color:#1a1a1a,stroke-width:3px
  classDef in      fill:#FFE4E6,stroke:#BE123C,color:#1a1a1a
  classDef money   fill:#FFEDD5,stroke:#C2410C,color:#1a1a1a
  classDef partner fill:#E0F2FE,stroke:#0369A1,color:#1a1a1a,stroke-dasharray:5 4
```

## 3. 홈페이지 연결 구조

```mermaid
flowchart LR
  subgraph TOOLS["작업 도구"]
    direction TB
    U["사용자"]:::user
    CC["Claude Code<br/>클라우드 세션"]:::ai
    ADM["admin kydz.kr/kydzm<br/>콘텐츠 · 통계 · 딜 · 스레드 · 쿠팡 실적<br/>GitHub 토큰은 브라우저에만"]:::user
  end

  subgraph GH["GitHub"]
    direction TB
    REPO[("camping-hub · 공개<br/>main = 배포")]:::src
    BP["Actions build-pages<br/>data 바뀌면 → 정적 페이지 · sitemap"]:::sys
    LC["Actions link-check<br/>월 09:10 쿠팡 링크 점검"]:::sys
    CUP[("cupas · 비공개<br/>스레드 예약 게시 · 쿠팡 실적 리포트")]:::src
    CS[("camping-search · 비공개<br/>카페 딜 수집 하루 3번")]:::src
  end

  subgraph CF["Cloudflare"]
    direction TB
    W["Worker kyd-stats<br/>방문 기록 D1 · 집계 KV"]:::sys
    WC["Worker 예약<br/>매시 집계 → stats.json 커밋<br/>매시 05분 → cupas 깨우기"]:::sys
  end

  subgraph WEB["사이트"]
    direction TB
    DNS["가비아 DNS<br/>kydz.kr"]:::sys
    PAGES[["GitHub Pages<br/>kydz.kr"]]:::page
    SA["네이버 서치어드바이저"]:::in
    SC["구글 서치 콘솔"]:::in
    GA["GA (미설치)"]:::partner
  end

  subgraph OUT["바깥 서비스"]
    direction TB
    CPAPI["쿠팡 파트너스 API"]:::src
    THAPI["스레드 API"]:::src
    LINKS["제휴 링크<br/>쿠팡 · 네이버 · 컬리 · 그래가"]:::money
  end

  U --> CC --> REPO
  U --> ADM
  ADM -- 저장 커밋 --> REPO
  ADM -- cupas 토큰 --> CUP
  ADM -- 딜 보드 · TOP 5 --> CS
  REPO --> BP --> REPO
  LC --> REPO
  REPO --> PAGES
  DNS --> PAGES
  PAGES -- 방문 · 클릭 --> W
  WC --> REPO
  WC --> CUP
  CUP <--> CPAPI
  CUP --> THAPI
  PAGES --> LINKS
  SA -. 수집 .-> PAGES
  SC -. 수집 .-> PAGES
  GA -.- PAGES

  classDef user    fill:#FFF3C4,stroke:#B7791F,color:#1a1a1a
  classDef ai      fill:#E3F2FD,stroke:#1E63B4,color:#1a1a1a
  classDef sys     fill:#EEEEEE,stroke:#616161,color:#1a1a1a
  classDef src     fill:#F3E8FF,stroke:#6B21A8,color:#1a1a1a
  classDef page    fill:#DCFCE7,stroke:#15803D,color:#1a1a1a,stroke-width:3px
  classDef in      fill:#FFE4E6,stroke:#BE123C,color:#1a1a1a
  classDef money   fill:#FFEDD5,stroke:#C2410C,color:#1a1a1a
  classDef partner fill:#E0F2FE,stroke:#0369A1,color:#1a1a1a,stroke-dasharray:5 4
```

## 확인 메모 (261030)

- 스레드(cupas): 하루 4개(09·12 정보, 18 정보+링크 1개, 22 질문형) + 토요일 20시 특가. Cloudflare Worker가 매시 05분에 깨움. 홈페이지로 유입되지 않는 별도 라인.
- 딜(camping-search): 하루 3번(08·16·23시) 수집 → admin 딜 보드·오늘의 딜 TOP 5. 꿀템방 게시는 수동.
- 성과 리포트: IG 인사이트 CSV를 수시로(정기는 월말) Claude에게 → admin 인사이트(`data/insights.json`). 노션 성과 기록은 260831 이후 갱신 없음.
- 협찬 메일 Apps Script: 동작 중(노션 협찬관리대장에 10분 주기 생성 흔적), 261030 기준 업체명 중복 0건.
- 사용 안 함(지도 제외): 사진 컬링(Cowork), kydbot, 타임라인 비주얼라이저, 댓글관리대장, 부계정.
- 조회수 수익 기준(261030): 페이스북 팔로워 1만·28일 유효조회 15만 / 네이버 클립 팔로워 1,000·90일 유효조회 300만.
