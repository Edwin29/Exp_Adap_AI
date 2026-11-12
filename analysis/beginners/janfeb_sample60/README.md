# 1~2월 A 150명 표본 엔진 평가 (사람당 60판)

분석 환경에서 2026-10-22에 만든 결과. 기준 코드는 `scripts/reference_container/evalg.py`, `classify.py`와 같다.

| 파일 | 내용 |
|---|---|
| moves.csv.gz | 수별 평가. 열: site, p, win, group, own_nm, ply, clk, cp_before, cp_after, wp_loss, acc. 267,353행, 150명, 8,960판 |
| blunders.csv.gz | 큰 실수와 유형. 열: site, ply, p, win, own_nm, clk, wp_loss, cp_before, cp_after, cat, reply_cap, reply_check, best_cap, was_check, n_legal |
| games_wanted.csv | 평가 대상 대국 목록. 열: site, p, color, group, win, elo, oppelo, score, km(그 달 몇 번째 판), month |

`win`: jan_early = 1월 처음 20판, jan_late = 1월 마지막 20판, feb_late = 2월 마지막 20판.
`site`는 Lichess 대국 ID 8자. 출처는 2018-01, 2018-02 월별 DB.
