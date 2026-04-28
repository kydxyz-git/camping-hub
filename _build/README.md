# 캠핑 허브 빌드 자산 백업

이 폴더는 **새 Claude 채팅 세션에서 작업을 이어가기 위한 백업**입니다.

## 파일

- `camping-hub-v4-draft.html` — HTML/CSS/JS 진실소스 (수정은 항상 이 파일에서)
- `sync_data.json` — 노션 4개 DB + 사이트 텍스트 캐시 (5종 동기화 데이터)

## 새 채팅 시작 시 복원 절차

```bash
# 1. Repo clone
cd /home/claude
git clone https://github.com/kydxyz-git/camping-hub.git gh-camping-hub

# 2. 빌드 자산 복원
cp gh-camping-hub/_build/camping-hub-v4-draft.html /mnt/user-data/outputs/
cp gh-camping-hub/_build/sync_data.json /home/claude/
```

이후 Claude는 평소처럼 "동기화해줘" 요청을 처리할 수 있습니다.

## 동기화 절차 (참고)

1. 노션 4개 DB fetch (변경사항 식별)
2. 신규 이미지 다운로드 (signed URL → PIL → JPEG)
3. sync_data.json 갱신
4. HTML 빌드 (re.sub lambda로 5개 동기화 영역 주입)
5. node --check 구문 검증
6. git push → GitHub Pages 배포

자세한 내용은 노션 페이지 "캠핑허브웹사이트_운영가이드_260422" 참조.
