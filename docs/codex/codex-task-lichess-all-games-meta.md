# Codex 작업 지시: 초보 984명의 블리츠 밖 경험 기록 + A 150명 1~2월 엔진 평가

이 문서는 세 부분으로 되어 있다.

- **2장 목표:** 반드시 만들어야 하는 결과물이다.
- **3장 절대 규칙:** 어떤 경우에도 바꾸면 안 되는 것이다.
- **5장 참고 방법:** 권장하는 방법일 뿐이다. 더 효율적인 방법이 있으면 바꿔도 된다. 바꿨다면 무엇을 왜 바꿨는지 `summary.md`에 적는다.

## 1. 배경 (왜 하는가)

이 저장소는 경험에 따라 사람의 판단이 어떻게 바뀌는지(적응)를 체스 데이터로 연구한다. 계획서는 `docs/research-plan-v3.md`에 있다.

지금까지는 초보 984명의 **rated 블리츠** 대국만 분석했다. 그런데 실력 변화가 블리츠 판 수보다 지난 날짜를 더 잘 따라간다는 결과가 나왔다. 이유로 두 가지를 의심한다.

1. **블리츠 밖 경험:** 같은 사람이 불릿, 래피드, 비레이팅 대국, 컴퓨터 상대 대국을 두었을 수 있다. 우리는 그것을 보지 못했다.
2. **간격 효과:** 같은 판 수라도 며칠에 나눠 두면 더 많이 는다. 이것을 시험하려면 실력 곡선이 가파른 1~2월의 모든 대국이 엔진 평가되어 있어야 한다. 지금은 사람당 60판만 평가되어 있다.

이 작업은 두 의심을 가르는 데 필요한 데이터를 만든다. **내려받기, 평가, 표 정리까지만** 한다. 분석은 하지 않는다.

## 2. 목표 (반드시 만들 결과물)

### 목표 1. 블리츠 밖 대국 목록

984명 각자가 **2018-01-01 00:00 UTC 이상 2019-01-01 00:00 UTC 미만**에 Lichess에서 둔 대국 중 **rated 블리츠를 뺀 모든 대국**의 목록을 만든다. 불릿, 울트라불릿, 래피드, 클래식, 통신 체스, 변형 체스, 비레이팅 블리츠, 컴퓨터 상대 대국, 특정 국면에서 시작한 대국이 모두 포함된다. rated 블리츠는 이미 갖고 있으므로 받지 않아도 된다. 받았다면 표에서 표시만 해 두면 된다.

**"rated 블리츠"의 정의:** `rated=true`이고 `perf=blitz`인 대국(정통 체스 블리츠 레이팅 대국)이다. 이것이 기존 데이터와 같은 범위다. 변형 체스는 블리츠 시간이라도(`speed=blitz`, `perf=atomic` 등) rated 여부와 관계없이 **포함한다.** `speed`만으로 판단하지 않는다.

수(기보)는 필요 없다. 필요한 것은 "언제, 어떤 종류를 두었는가"다.

결과물:

| 파일 | 내용 |
|---|---|
| `data/derived/beginners/all_games_meta_2018.csv.gz` | 대국당 한 행. 아래 열을 **이 이름 그대로** 둔다 |
| `data/lichess_api/beginners_2018_all_meta/` | 원본 응답(형식 자유)과 `manifest.csv`, `summary.md` |

`all_games_meta_2018.csv.gz`의 열:

| 열 | 설명 |
|---|---|
| username | 984명 명단의 아이디 (대소문자 그대로) |
| game_id | Lichess 대국 ID (8자) |
| created_at_utc | 대국 시작 시각, ISO 8601 UTC |
| last_move_at_utc | 마지막 수 시각, ISO 8601 UTC |
| rated | true/false |
| variant | standard, chess960, fromPosition 등 Lichess 값 그대로 |
| speed | ultraBullet, bullet, blitz, rapid, classical, correspondence |
| perf | Lichess 값 그대로 |
| status | mate, resign, outoftime, aborted 등 Lichess 값 그대로 |
| color | white/black (username의 색) |
| user_rating | username의 대국 당시 레이팅. 없으면 빈칸 |
| opp_rating | 상대의 레이팅. 없으면 빈칸 |
| opp_is_ai | 상대가 컴퓨터면 true |
| winner_is_user | username이 이겼으면 1, 졌으면 0, 무승부·미결이면 빈칸 |
| is_rated_blitz | `rated=true`이고 `perf=blitz`면 true. 변형 체스는 speed가 blitz여도 false |

`manifest.csv`에는 사람당 최소한 아래를 남긴다: username, priority(A/B), status(ok/not_found/skipped_404/error), n_games, error_message. 여러 요청으로 나눠 받았다면 요청별 행을 써도 된다.

### 목표 2. A 150명의 1~2월 rated 블리츠 전체 엔진 평가

`beginners_984.csv`에서 `engine_sample_150 = 1`인 사람 중 계정이 살아 있는 사람(지난 매니페스트에서 404가 아닌 사람)이 대상이다. 이들이 **2018-01-01 이상 2018-03-01 미만 UTC**에 둔 **모든** rated 블리츠를 평가한다.

결과물은 지난 평가 `data/derived/engine/beginners_2018-03_12/`와 **같은 구조와 같은 열**로 `data/derived/engine/beginners_2018-01_02_A/`에 둔다: `moves/`, `blunders/`, `games/`, `progress.csv`, `summary.md`. `win` 열에는 `A_2018-01`, `A_2018-02`를 적는다. 원본 PGN을 새로 받았다면 `data/lichess_api/beginners_2018-01_02_A/`에 둔다.

## 3. 절대 규칙 (바꾸면 안 됨)

### Lichess 이용

1. **Lichess 요청은 전체에서 항상 한 번에 하나만 보낸다.** 병렬 요청, 여러 프로세스의 동시 요청, 여러 토큰 사용은 금지다. Lichess는 동시 요청을 막고, 어기면 계정이나 IP가 차단될 수 있다.
2. **HTTP 429를 받으면 최소 60초 기다린다.**
3. **토큰은 환경 변수 `LICHESS_TOKEN`에서만 읽는다.** 코드, 로그, 매니페스트, 요약, 커밋 어디에도 쓰거나 출력하지 않는다.
4. **984명 명단 밖의 사용자 대국은 받지 않는다.** 지난번 404였던 107명은 다시 요청하지 않고 `skipped_404`로 남긴다.

### 데이터 보존

5. **`data/` 안의 기존 파일은 고치거나 지우지 않는다.** 새 파일만 만든다.
6. **대국을 거르지 않는다.** aborted, 짧은 대국, 컴퓨터 상대 대국도 모두 표에 남긴다. 거르는 것은 분석 단계에서 한다.
7. **기간 경계를 지킨다.** 목표 1은 2018-01-01 ~ 2019-01-01, 목표 2는 2018-01-01 ~ 2018-03-01 (UTC, 시작 포함·끝 미포함).
8. **목표 2장의 열 이름과 뜻을 바꾸지 않는다.** 분석 코드가 이 이름에 의존한다. 열을 더하는 것은 괜찮다.

### 엔진 평가 (목표 2)

9. **기준 코드와 같은 정의를 쓴다.** `scripts/engine_eval_user_games.py`(지난번에 만든 것)와 `scripts/reference_container/`의 수식을 바꾸지 않는다. 구체적으로 아래가 그대로여야 한다.
   - Stockfish 16, 깊이 10, 엔진 하나당 Threads=1, Hash=64
   - 승률 변환식, 정확도 식, 큰 실수 기준 30, 분류 순서, "공짜" 기준 2점
   - 국면 평가는 매 수 연속으로 하고, 평가 대상은 명단에 있는 사람의 수만
   - 시계가 없는 수는 지난번과 같이 999초로 취급
10. **평가 전에 두 FEN 검증을 다시 통과한다** (`docs/codex-task-engine-eval-overnight.md` 5장). 유형이 다르면 멈추고 보고한다.

### 기타

11. **분석이나 그림은 하지 않는다.** 평가, 저장, 표 정리, 점검까지만 한다.
12. **데이터는 커밋하지 않는다.** 스크립트 커밋도 사용자가 원할 때만 한다.

## 4. 확인 기준 (끝났다고 보려면)

`summary.md`에 아래를 적는다.

목표 1:

- 984명 전원이 manifest에 있고, 상태 공란과 남은 임시 파일이 없다.
- 상태별 사람 수
- 총 대국 수, speed × rated별 대국 수, variant별 대국 수, 컴퓨터 상대 대국 수 (전체와 A 150명 각각)
- **rated 블리츠 일치 점검:** rated 블리츠도 받았다면, 사람·월별 수를 기존 기록(3~12월은 `beginners_2018-03_12/manifest.csv`의 `monthly_games`, 1~2월은 `beginners_984.csv`)과 비교해 차이를 적는다. 받지 않았다면 표에 `is_rated_blitz=true`인 행이 0인지 확인한다.
- 같은 `game_id`가 한 사람 안에서 두 번 나오지 않는다.

목표 2:

- 사람별 1월 판 수가 `beginners_984.csv`의 `jan_blitz_games`, 2월이 `feb_blitz_games`와 맞는지. 다른 사람과 차이를 적는다.
- 기존 1~2월 표본(사람당 60판)과 겹치는 대국에서 수별 승률 손실 평균 차이
- 지난번 summary와 같은 형식의 처리량, 정확도, 큰 실수 비율, 유형별 비율

공통:

- 실패한 사람과 이유
- 5장의 참고 방법에서 바꾼 것과 이유
- 걸린 시간

## 5. 참고 방법 (바꿔도 됨)

아래는 권장 방법이다. 효율에 따라 바꿔도 되지만, 3장 규칙과 4장 확인 기준은 지켜야 한다.

### 목표 1: 요청 방식

rated 블리츠를 빼고 받으면 대국 수가 크게 준다. Lichess는 수를 빼도 **대국 수 기준**으로 속도를 제한한다(토큰 없이 초당 약 20판, 있으면 약 30판). 그래서 받는 대국 수를 줄이는 것이 시간을 줄이는 핵심이다. 사람마다 두 요청을 차례로 보내는 방식을 권한다.

공통 인자:

```
GET https://lichess.org/api/games/user/{username}
  ?since=1514764800000      # 2018-01-01T00:00:00Z
  &until=1546300800000      # 2019-01-01T00:00:00Z
  &moves=false&pgnInJson=false&clocks=false&evals=false&opening=false
  &sort=dateAsc
Accept: application/x-ndjson
```

| 요청 | 추가 인자 | 받는 것 |
|---|---|---|
| other | `perfType=ultraBullet,bullet,rapid,classical,correspondence,chess960,crazyhouse,antichess,atomic,horde,kingOfTheHill,racingKings,threeCheck` | 블리츠가 아닌 모든 대국 (rated, 비레이팅 모두) |
| casual_blitz | `perfType=blitz&rated=false` | 비레이팅 블리츠 |

NDJSON 필드와 표의 열은 다음과 같이 대응한다: `id`→game_id, `createdAt`/`lastMoveAt`(ms)→시각, `rated`, `variant`, `speed`, `perf`, `status`, `players.white/black.user.name`과 `rating`, `players.*.aiLevel`→opp_is_ai, `winner`→winner_is_user.

이 필터 조합이 실제로 "rated 블리츠만 빼고 전부"를 돌려주는지는 처음 몇 명으로 확인하기를 권한다. 예를 들어 `other`에 blitz가 섞이지 않는지, 두 요청이 겹치지 않는지, fromPosition·컴퓨터 대국이 어느 쪽에든 들어오는지 본다. 필터가 기대와 다르게 동작하면 필터 없이 전체를 받아도 된다. 그 경우 시간이 몇 배 걸린다.

### 목표 1: 순서와 이어받기

A 150명을 먼저 처리하면 그 결과로 첫 분석을 일찍 시작할 수 있다. 오류 처리로는 5xx나 네트워크 오류 때 10초, 30초, 90초 간격으로 다시 시도하는 방식을 권한다. 완료한 사람은 다시 실행할 때 건너뛰게 하고, 쓰는 중인 파일은 임시 이름으로 썼다가 끝나면 바꾼다.

### 목표 2: 내려받기와 평가

1~2월 PGN은 지난 작업(`docs/codex-task-lichess-user-games.md` 3-2)과 같은 요청에 `since=1514764800000&until=1519862400000`을 쓰면 받을 수 있다. 이미 PC에 있는 2018-01, 2018-02 월별 DB(`.pgn.zst`)에서 뽑아도 된다. 어느 쪽이든 `[%clk]` 주석이 있어야 한다.

평가는 지난번처럼 엔진 프로세스 여러 개로 병렬화하면 된다. 엔진 평가는 컴퓨터 자원을, 목표 1은 네트워크를 쓰므로 둘을 동시에 돌려도 된다. 단 Lichess 요청은 3장 1번대로 전체에서 하나씩이어야 한다.

### 규모 참고

- 목표 1: 블리츠 밖 대국 수는 모른다. 1월 분석에서 많이 두는 사람은 한 시간제한에 98%를 몰아 두었으므로 rated 블리츠(1~12월 약 90만 판)보다 훨씬 적을 것으로 본다.
- 목표 2: 약 135명 × 330판 = 4~5만 판. 지난 평가 속도로 1시간 안팎이다.
