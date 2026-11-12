# Codex 작업 지시: 초보 984명의 2018년 3~12월 Lichess 블리츠 대국 내려받기

## 1. 배경 (왜 하는가)

이 저장소는 "경험에 따라 사람의 판단이 어떻게 바뀌는가(적응)"를 체스 데이터로 연구한다. 계획서는 `docs/research-plan-v3.md`에 있다.

지금까지는 Lichess 월별 공개 DB(2018년 1월, 2월, rated 대국만)를 썼다. 여기서 "블리츠를 처음 시작한 초보" 984명을 골랐다. 고른 기준은 2018년 1월 첫 블리츠 대국이 임시 레이팅 1500이고, 30번째 대국에서 1200 이하로 떨어졌으며, 1월에 100판 이상 둔 계정이다.

두 달만으로는 "실력이 정체된 사람"과 "아주 느리게 느는 사람"을 구별할 수 없다. 그래서 **같은 984명을 2018년 3월~12월까지 더 따라가려고 한다.** 월별 DB 전체(월 5GB 이상)를 받는 대신, Lichess API로 이 사람들의 대국만 받는다.

이번 작업은 **내려받기와 기록까지만** 한다. 분석, 필터링, 엔진 평가는 하지 않는다.

## 2. 입력

- `data/derived/beginners/beginners_984.csv` (984행)

| 열 | 뜻 |
|---|---|
| username | Lichess 아이디 (대소문자 그대로) |
| first_blitz_game_utc | 2018년 1월 DB에서 본 첫 블리츠 대국 시각 (UTC) |
| jan_blitz_games, feb_blitz_games | 1월·2월 DB에서 센 rated 블리츠 대국 수 |
| elo_at_game30 | 30번째 블리츠 대국의 레이팅 |
| elo_last_game_feb | 2월 마지막 블리츠 대국의 레이팅 (2월에 안 뒀으면 비어 있음) |
| engine_sample_150 | 엔진 분석 표본에 든 150명이면 1 |

## 3. 할 일

### 3-1. 계정 상태 먼저 확인

`POST https://lichess.org/api/users` 로 한 번에 최대 300개 아이디의 상태를 조회한다(본문은 쉼표로 구분한 아이디, `Content-Type: text/plain`). 응답에 없는 아이디는 `not_found`로 기록한다. 응답에 `disabled: true`나 `tosViolation: true`가 있으면 그 값도 기록한다. 이 정보는 나중에 "중간에 빠진 사람 때문에 생기는 편향(생존 편향)"을 따지는 데 꼭 필요하다. 대국을 못 받더라도 반드시 남긴다.

### 3-2. 사용자별 대국 내려받기

각 아이디마다 아래 요청을 보낸다.

```
GET https://lichess.org/api/games/user/{username}
  ?since=1519862400000      # 2018-03-01T00:00:00Z (ms)
  &until=1546300800000      # 2019-01-01T00:00:00Z (ms), 이 시각 미만
  &perfType=blitz
  &rated=true               # 기존 DB가 rated 대국만이므로 맞춤
  &clocks=true              # [%clk] 남은 시간 주석. 분석에 필수
  &evals=false
  &opening=true
  &sort=dateAsc
Accept: application/x-chess-pgn
```

- 응답은 PGN 스트림이다. `data/lichess_api/beginners_2018-03_12/{username}.pgn.gz` 로 gzip 압축해 저장한다.
- 쓰는 동안은 `.part` 이름으로 쓰고, 끝까지 받으면 이름을 바꾼다. 중간에 끊긴 파일이 완료된 것처럼 보이면 안 된다.
- 대국이 0판이어도 정상이다. 빈 파일을 만들고 상태는 `ok`, 대국 수는 0으로 기록한다.

### 3-3. 속도 제한과 오류 처리 (반드시 지킬 것)

- **한 번에 한 요청만 보낸다.** 병렬 요청은 금지다. Lichess는 동시 요청을 막는다.
- HTTP 429를 받으면 **최소 60초** 기다린 뒤 같은 사용자를 다시 시도한다.
- 5xx나 네트워크 오류가 나면 10초, 30초, 90초 간격으로 최대 3번 다시 시도한다. 그래도 실패하면 `error`로 기록하고 다음 사람으로 넘어간다.
- 404는 `not_found`로 기록하고 넘어간다.
- 토큰은 선택이다. 환경 변수 `LICHESS_TOKEN`이 있으면 `Authorization: Bearer <토큰>` 헤더를 붙인다(속도가 초당 약 20판에서 30판으로 오른다). **토큰을 코드, 로그, 매니페스트, 커밋 어디에도 쓰거나 출력하지 않는다.**

### 3-4. 이어받기

- 매니페스트에서 `ok`인 사용자는 건너뛴다. 스크립트를 몇 번 다시 실행해도 같은 결과가 나와야 한다.
- 전체 예상량은 최대 수십만 판이고, 몇 시간이 걸릴 수 있다. 진행 상황(몇 번째 사람인지, 누적 대국 수, 경과 시간)을 주기적으로 출력한다.

## 4. 출력

| 파일 | 내용 |
|---|---|
| `scripts/fetch_user_games.py` | 내려받기 스크립트. 입력 CSV, 기간, 출력 폴더를 인자로 받음. 기본값은 위 설정 |
| `data/lichess_api/beginners_2018-03_12/*.pgn.gz` | 사용자별 PGN |
| `data/lichess_api/beginners_2018-03_12/manifest.csv` | 사용자당 한 행: username, account_status(ok/not_found/disabled/tos_violation/error), disabled, tos_violation, http_status, n_games, first_game_utc, last_game_utc, n_games_with_clock, bytes, downloaded_at_utc, error_message |
| `data/lichess_api/beginners_2018-03_12/summary.md` | 아래 5장의 점검 결과 |

`data/*`는 `.gitignore`로 제외돼 있다. 데이터 파일은 커밋하지 않는다. 스크립트만 커밋 대상이며, 커밋은 사용자가 원할 때만 한다.

## 5. 점검 (summary.md에 적을 것)

1. **시험 실행:** 처음에 5명만 받아서 PGN 머리말(`[Event]`, `[UTCDate]`, `[WhiteElo]`, `[TimeControl]`)과 수마다 `[%clk ...]`가 있는지 확인한다.
2. **기존 DB와 맞는지 확인:** `engine_sample_150=1`인 사람 중 10명을 골라, 같은 API로 기간만 2018-01-01~2018-02-01로 바꿔 받는다. 받은 판 수를 `jan_blitz_games`와 비교한다. 이 비교용 파일은 `data/lichess_api/check_2018-01/`에 따로 둔다. 차이가 10%를 넘으면 차이 나는 대국의 `TimeControl`과 `Event`를 적는다. 이 점검이 실패하면 전체 실행 전에 멈추고 보고한다.
3. **전체 결과:**
   - 상태별 사람 수(ok/not_found/disabled/tos_violation/error)
   - 총 대국 수
   - 월별 대국 수(3월~12월)
   - 월별로 1판 이상 둔 사람 수
   - `[%clk]`이 없는 대국 비율
   - 전체 용량과 걸린 시간

## 6. 하지 말 것

- `data/` 안의 기존 파일(월별 `.pgn.zst`, `.part`, `.resume.json` 등)은 건드리거나 지우지 않는다. 지금 2018년 3월 DB를 받는 중일 수 있다.
- 대국을 거르거나(취소된 대국, 시간패 등) 분석하지 않는다. 받은 그대로 저장한다.
- 984명 외의 사용자 대국은 받지 않는다.
- 요청 속도를 높이려고 병렬화하거나 여러 토큰을 쓰지 않는다.

## 7. 끝나면 사용자에게 알려 줄 것

summary.md의 핵심 숫자를 보고한다(상태별 인원, 총 대국 수, 월별 활동 인원, 기존 DB 대비 일치 여부). 실패하거나 건너뛴 사람이 있으면 그 수와 이유를 함께 알린다.
