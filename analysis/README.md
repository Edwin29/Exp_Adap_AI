# analysis

Claude의 분석 환경에서 돌린 체스 분석 스크립트, 요약 JSON, 그림이다. 결과 해석은 [docs/context/04_결과_요약.md](../docs/context/04_결과_요약.md)에 있다.

| 폴더 | 내용 |
|---|---|
| `2018-01/` | 1월 전체 헤더 분석, 사용자별 변화(`user_change/`), 왕 안전 지표(`king_safety/`) |
| `2018-02/` | 2월 후속 분석, 엔진 정확도 확인(`engine/`) |
| `beginners/` | 진짜 초보 984명: 큰 실수 유형(`blunders/`), 지각 사건 연구(`event_perception/`), 3~12월 추적(`mar_dec/`), 관찰되지 않는 경험(`unobserved/`), 예측 기준선과 개인차(`prediction/`) |

주의:
- 스크립트 속 경로(`/mnt/user-data/...`, `/tmp/...`)는 당시 분석 환경의 경로다. PC에서 다시 돌리려면 `data/` 아래 경로로 바꿔야 한다.
- CSV, 압축 파일, 이용자 이름 목록, 대국 ID가 든 파일은 올리지 않았다(`.gitignore`). 필요하면 PC의 `data/derived/`나 Claude 프로젝트 파일에서 가져온다.
