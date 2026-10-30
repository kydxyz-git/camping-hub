# 캠핑장 페이지 필드 · 패치 형식

캠핑장 페이지(`/camps/{이름}/`, `camp.html?id=`)는 인스타 게시물의 **풀 버전**이다 (261030 결정).
채팅 세션이 아래 형식의 패치 JSON을 만들면 **Code 세션이 `python tools/apply_camp_patch.py patch.json`으로 적용·커밋**한다(여러 곳은 `[…]` 배열 하나). 사용자가 직접 고칠 때는 admin 캠핑장 상세 맨 위 **📥 패치 붙여넣기**(같은 규칙).
`story`·`guide`는 사용자가 확정한 문장만 넣는다 (Code·채팅이 지어 넣지 않음).

## 필드 (`data/camps.json`, 기존 필드는 그대로 두고 추가)

| 필드 | 형식 | 내용 |
|---|---|---|
| `hook` | 문자열 | 한 줄 훅 (릴스 첫 자막 그대로). 있으면 제목 아래 + `<title>` |
| `story` | 문자열 | 본문. 업로드 캡션을 웹용으로 — 해시태그는 넣고, 협찬 고지·DM 유도·정보 줄은 빼고, '이번에·올해·내년' 같은 시점 표현은 뺀다(261030). 빈 줄 = 단락, 마크다운 처리 없음 |
| `guide` | `[{zone, text, pick}]` | 존별 가이드. `pick: true`는 ★ + 맨 위 |
| `layout_imgs` | `["./images/camps/…jpg"]` | 배치도 (원본 비율, 긴 변 1200 — admin 업로드는 `{hash}-layout-…jpg`) |
| `info` | 객체 | `checkin checkout manner pets max_people facilities[] season notice source{platform,url,checked_at}` — 예약 플랫폼 기준. 입퇴실은 `info`가 최상위 `checkin/checkout`보다 우선 |
| `links` | `[{type, label, url}]` | `type`: `reserve discount event homepage naver_blog etc` (이 순서로 버튼). 예약 링크가 없으면 기존 `url`로 예약 버튼 |
| `gear` / `foods` | `["item_…"]` / `["food_…"]` | 이때 쓴 장비·먹은 것 → 카드 + `/gear/…`·`/foods/…` 상세 링크 |
| `visit_log` | `[{date, note}]` | 선택. `visits` 숫자는 따로 유지 |
| `dm_keyword` | 문자열 | `dm: true`이고 `guide`가 비었을 때 "더 자세한 추천 자리·배치도는 인스타 DM '키워드'" |

릴스는 지금처럼 `videos` + `series.json` EP의 `camp_id`로 붙는다 (새 필드 없음).

## 패치 붙여넣기 규칙

- `id` → 없으면 `name` → 둘 다 없으면 지금 열린 캠핑장.
- 적용 전 미리보기(`기존 → 새 값`). 배열(`guide links gear foods imgs extras`)은 기본 **대체**, 체크하면 **병합**(같은 존/같은 링크는 교체).
- `info`는 항목별로 덮어쓴다 (패치에 없는 info 항목은 유지). 값을 `null`로 주면 그 필드(항목)를 지운다.
- `"visits": "+1"`은 1 증가, 숫자면 그 값.
- 잘못된 JSON·형식 오류는 거부. 모르는 필드는 경고만 하고 저장.
- 저장은 `ghCommitTree`(3-way 병합) 그대로, 커밋 `update(admin): {이름} 패치`. 1~3분 뒤 `build-pages` Actions가 페이지를 다시 만든다.

## 정보 수집 → 패치

`python tools/collect_camp_info.py` → `data/camp_info_raw/{id}.json`(`text` 본문 + `extracted` 후보) → 사람이 확인해 `info` 패치로.
`needs_browser`(네이버·막힌 캠핏)는 채팅 세션에서 본인 크롬으로 읽는다. 고캠핑(관광공사) 데이터는 쓰지 않는다.

## 예시 — 밀양 알프스캠핑

```json
{
  "id": "camp_f60efbd4c7",
  "hook": "가을에도 낮은 더워요, 그래서 찾은 그늘지옥 캠핑장",
  "story": "첫 단락\n\n둘째 단락",
  "guide": [
    { "zone": "A존", "text": "강뷰 명당. 뷰 보러 간다면 여기", "pick": true },
    { "zone": "C·D존", "text": "그늘 좋고 사이트 넓음", "pick": false },
    { "zone": "E·F존", "text": "그늘은 최고(E>F). 도로 쪽이라 차량 소음, 화장실은 민박 쪽", "pick": false }
  ],
  "info": {
    "checkin": "14:00", "checkout": "12:00",
    "manner": "23:00~07:00",
    "pets": "2마리까지",
    "facilities": ["와이파이"],
    "notice": "방문객 출입 불가 · 2026.9.1부터 그래가 앱 전용 예약",
    "source": { "platform": "그래가", "url": "https://www.graega.com/rooms/7143", "checked_at": "2026-10-30" }
  },
  "links": [
    { "type": "reserve", "label": "그래가 앱에서 예약", "url": "https://graega.short.gy/7143kydzm" },
    { "type": "discount", "label": "올해 말까지 20% 할인 · 추천인 코드 공대남자", "url": "https://graega.short.gy/7143kydzm" }
  ],
  "visit_log": [{ "date": "2026-09-11", "note": "E-3 사이트, 1박" }],
  "dm_keyword": "그늘"
}
```
