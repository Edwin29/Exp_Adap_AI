# Codex 작업 지시: 내려받은 초보 대국의 엔진 평가 (야간 작업)

## 0. 시작 조건 (먼저 확인)

이 작업은 `docs/codex-task-lichess-user-games.md`의 내려받기가 **끝난 뒤에만** 시작한다. 끝났다는 것은 아래 네 가지가 모두 참이라는 뜻이다. 하나라도 거짓이면 시작하지 말고 10분마다 다시 확인한다. 2시간이 지나도 끝나지 않으면 멈추고 상태를 보고한다.

1. `data/lichess_api/beginners_2018-03_12/manifest.csv`가 있고, 데이터 행이 984개다.
2. 매니페스트에 `account_status`가 비어 있는 행이 없다.
3. `data/lichess_api/beginners_2018-03_12/` 아래에 `.part` 파일이 하나도 없다.
4. 같은 폴더에 `summary.md`가 있다.

## 1. 배경

이 저장소는 경험에 따라 사람의 판단이 어떻게 바뀌는지(적응)를 체스 데이터로 연구한다(`docs/research-plan-v3.md`). 초보 984명의 대국을 엔진으로 평가한다. 이를 위해 수마다 정확도와 큰 실수, 큰 실수의 유형(기물을 공짜로 내줌, 위협 무시, 잡을 기물 놓침 등)을 구한다. 이 결과로 두 가지를 본다.

- 몇 달에 걸친 실력 변화가 사람마다 향상, 정체, 하락 중 어디에 속하는가
- 특정 경험 직후에 같은 실수가 줄어드는가

**이미 분석 환경에서 쓴 것과 똑같은 정의를 써야 한다.** 기준 코드가 `scripts/reference_container/evalg.py`(수별 평가)와 `scripts/reference_container/classify.py`(큰 실수 분류)에 있다. 수식, 기준값, 분류 규칙을 바꾸지 말고, 입출력 경로와 Windows 실행에 필요한 부분만 고친다.

## 2. 엔진 설정 (기준 코드와 동일)

- Stockfish 16. 공식 배포판 https://github.com/official-stockfish/Stockfish/releases/tag/sf_16 에서 Windows용 실행 파일을 받아 `tools/stockfish/` 아래에 둔다. `tools/`는 커밋하지 않도록 `.gitignore`에 추가한다.
- 평가 깊이 10(`Limit(depth=10)`), 엔진 하나당 `Threads=1`, `Hash=64`.
- 병렬화는 **엔진 프로세스 여러 개**로 한다. 프로세스 수는 (물리 코어 수 − 1)로 둔다.

## 3. 평가할 대국 (우선순위대로)

입력은 `data/lichess_api/beginners_2018-03_12/{username}.pgn.gz`와 명단 `data/derived/beginners/beginners_984.csv`이다.

| 우선순위 | 대상 | 대국 | 쓰임 |
|---|---|---|---|
| A | `engine_sample_150 = 1`인 150명 | 2018년 3~12월의 **모든** rated 블리츠 대국 | 연속된 판이 필요한 사건 연구, 장기 궤적 |
| B | 나머지 834명 (아이디를 시드 2026으로 섞은 순서) | 각 달(3~12월)의 **처음 20판** | 사람별 향상·정체·하락 분류 |

A를 모두 끝낸 뒤 B를 시작한다. B는 사람 단위로 끝까지 처리하고, 중간에 멈춰도 그때까지 끝난 사람의 결과는 그대로 쓸 수 있어야 한다.

평가 대상 쪽은 그 대국에서 **명단에 있는 사람의 수**뿐이다. 상대의 수는 평가하지 않는다(기준 코드와 같음). 단, 국면 평가는 기준 코드처럼 매 수마다 연속으로 해야 "수 전 평가"와 "수 후 평가"가 맞는다.

## 4. 출력

| 파일 | 내용 |
|---|---|
| `scripts/engine_eval_user_games.py` | 평가와 분류를 하는 스크립트. 기준 코드의 로직을 그대로 옮김 |
| `data/derived/engine/beginners_2018-03_12/moves/{username}.csv` | 기준 코드 `moves*.csv`와 같은 열: site, p, win, group, own_nm, ply, clk, cp_before, cp_after, wp_loss, acc. `win`에는 우선순위(A 또는 B)와 달을 `A_2018-03`처럼 적고, `group`은 `beg` |
| `data/derived/engine/beginners_2018-03_12/blunders/{username}.csv` | 기준 코드 `blund*.csv`와 같은 열: site, ply, p, win, own_nm, clk, wp_loss, cp_before, cp_after, cat, reply_cap, reply_check, best_cap, was_check, n_legal |
| `data/derived/engine/beginners_2018-03_12/games/{username}.csv` | 대국당 한 행: site, p, utc_datetime, color, elo, opp_elo, result_for_p(1/0.5/0), termination, time_control, event, n_moves_by_p |
| `data/derived/engine/beginners_2018-03_12/progress.csv` | 사람당 한 행: username, priority, status(done/partial/skipped), n_games, n_moves, started_utc, finished_utc |
| `data/derived/engine/beginners_2018-03_12/summary.md` | 아래 6장의 점검 결과 |

사람별 파일은 다 끝난 뒤에 `.part`에서 이름을 바꾼다. `progress.csv`에서 `done`인 사람은 다시 실행할 때 건너뛴다(이어받기).

## 5. 시작 전 점검 (반드시)

1. **기준 코드와 일치 확인:** 아래 FEN에서 수 하나를 평가한다. 그리고 분류 규칙이 기준 코드와 같은 유형을 내는지 확인한다. 기준 결과는 분석 환경에서 나온 값이다.
   - 국면 `r1bqkb1r/ppp2ppp/2np1n2/4p3/2P1P3/3PB2P/PP3PP1/RN1QKBNR b KQkq - 2 5`, 둔 수 `Bg4` → 유형 `moved_piece_hung`, 승률 손실 약 40.
   - 국면 `rnb1kbnr/2p1pp1p/p1q3p1/1p1p4/1P1P1P2/2N1P3/P1P3PP/R1BQKBNR b KQkq - 0 7`, 둔 수 `h5` → 유형 `missed_capture`, 승률 손실 약 38.

   깊이 10은 실행마다 조금씩 달라질 수 있다. 그래서 승률 손실은 ±5 안이면 통과로 본다. 유형이 다르면 멈추고 보고한다.
2. **속도 측정:** A 대상 한 명의 대국으로 1분 동안 몇 판을 처리하는지 재고, 전체 예상 시간을 `summary.md` 맨 위에 적는다.

## 6. 끝나면 summary.md에 적을 것

- A, B 각각: 처리한 사람 수, 대국 수, 수 수, 걸린 시간
- 남은 시간 10초 미만 수를 뺀 뒤의 전체 평균 정확도, 큰 실수 비율(100수당)
- 큰 실수 유형별 비율
- 실패한 사람과 이유

## 7. 하지 말 것

- 기준 코드의 수식(승률 변환, 정확도 식, 큰 실수 기준 30, 분류 순서, "공짜" 기준 2점)을 바꾸지 않는다.
- `data/` 안의 원본 파일(`.pgn.zst`, 내려받은 `.pgn.gz`)을 고치거나 지우지 않는다.
- 결과를 분석하거나 그림을 그리지 않는다. 평가와 저장까지만 한다.
- 데이터 파일은 커밋하지 않는다. 커밋은 사용자가 원할 때만 한다.
