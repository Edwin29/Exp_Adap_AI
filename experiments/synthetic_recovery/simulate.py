"""가짜 사람 시뮬레이터 (0단계: 갱신 규칙 복원 실험의 준비물).

각 가짜 사람은 대국마다 갈림길 국면 P개에서 후보 수 C개 중 하나를 고른다.
후보 수는 특성 2개를 가진다: f[...,0] = 킹 안전, f[...,1] = 기물.
선택 확률은 조건부 로짓:  p(c) ∝ exp(w_king * f_king(c) + w_mat * f_mat(c)).
w_mat = 1로 고정해서 척도를 묶고, w_king만 시간에 따라 변한다.

갱신 규칙 (참값, 모델은 이걸 모른다):
    "킹 공격으로 진 판" 직후에만  w_king <- w_king + alpha * (target - w_king)
    alpha, target, w0는 사람마다 다르다. alpha = 0인 사람(변하지 않는 사람)도 섞는다.
닫힌 고리: 그 판에서 고른 수의 킹 안전 특성 평균이 낮을수록 킹 공격 패배 확률이 커진다.

사용법:
    python simulate.py                       # 기본 설정으로 data/sim_default.npz 생성
    python simulate.py --positions 4 --out data/sim_p4.npz
"""
import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# 대국 결과 코드
WIN, DRAW, LOSS_KING, LOSS_OTHER = 0, 1, 2, 3
OUTCOME_NAMES = ["win", "draw", "loss_king_attack", "loss_other"]


@dataclass
class Config:
    n_players: int = 1000
    n_games: int = 300
    positions: int = 8          # 판당 갈림길 국면 수 (작을수록 신호가 약해짐)
    candidates: int = 3         # 국면당 후보 수
    tradeoff_rho: float = 0.6   # 킹 안전과 기물 특성의 음의 상관 (클수록 '갈림길'다움)
    w_mat: float = 1.0
    w0_mean: float = 0.2        # 처음 킹 안전 가치 (낮게 시작)
    w0_sd: float = 0.3
    target_mean: float = 1.2    # 사건이 끌어당기는 목표 가치
    target_sd: float = 0.3
    p_static: float = 0.2       # alpha = 0인 사람 비율
    alpha_a: float = 2.0        # 나머지의 alpha ~ Beta(a, b), 평균 a/(a+b) ≈ 0.09
    alpha_b: float = 20.0
    # 판 결과 확률: 킹 공격 패배 logit = k0 - k1 * (고른 수 킹 특성 평균)
    k0: float = -1.8
    k1: float = 2.0
    p_win: float = 0.45         # 킹 공격 패배가 아닐 때 나머지 결과 비율
    p_draw: float = 0.05
    drift_sd: float = 0.0       # 판마다 사건과 무관한 무작위 흔들림 (4단계 어렵게 하기용)
    seed: int = 0


def simulate(cfg: Config) -> dict:
    rng = np.random.default_rng(cfg.seed)
    N, G, P, C = cfg.n_players, cfg.n_games, cfg.positions, cfg.candidates

    # 사람별 참값 파라미터
    w0 = rng.normal(cfg.w0_mean, cfg.w0_sd, N)
    target = rng.normal(cfg.target_mean, cfg.target_sd, N)
    alpha = rng.beta(cfg.alpha_a, cfg.alpha_b, N)
    static = rng.random(N) < cfg.p_static
    alpha[static] = 0.0

    # 국면 특성: 킹 특성 z, 기물 특성 = -rho*z + 잡음  (서로 맞바꾸는 관계)
    fk = rng.normal(0, 1, (N, G, P, C))
    fm = -cfg.tradeoff_rho * fk + np.sqrt(1 - cfg.tradeoff_rho**2) * rng.normal(0, 1, (N, G, P, C))
    feats = np.stack([fk, fm], axis=-1).astype(np.float32)  # [N,G,P,C,2]

    w_king = np.zeros((N, G), np.float32)   # 그 판을 두는 동안의 값 (갱신 전)
    choices = np.zeros((N, G, P), np.int8)
    outcome = np.zeros((N, G), np.int8)

    w = w0.copy()
    other = np.array([cfg.p_win, cfg.p_draw, 1 - cfg.p_win - cfg.p_draw])
    for g in range(G):
        w_king[:, g] = w
        util = w[:, None, None] * fk[:, g] + cfg.w_mat * fm[:, g]          # [N,P,C]
        prob = np.exp(util - util.max(-1, keepdims=True))
        prob /= prob.sum(-1, keepdims=True)
        u = rng.random((N, P, 1))
        ch = (prob.cumsum(-1) < u).sum(-1).clip(max=C - 1)                 # [N,P]
        choices[:, g] = ch

        chosen_fk = np.take_along_axis(fk[:, g], ch[..., None], -1)[..., 0].mean(-1)
        p_lk = 1 / (1 + np.exp(-(cfg.k0 - cfg.k1 * chosen_fk)))
        is_lk = rng.random(N) < p_lk
        rest = rng.choice([WIN, DRAW, LOSS_OTHER], size=N, p=other)
        outcome[:, g] = np.where(is_lk, LOSS_KING, rest)

        # 참값 갱신 규칙 (판이 끝난 뒤)
        w = w + is_lk * alpha * (target - w)
        if cfg.drift_sd > 0:
            w = w + rng.normal(0, cfg.drift_sd, N)

    # 사람 단위로 학습/검증/시험 분할 (같은 사람이 두 묶음에 들어가지 않게)
    perm = rng.permutation(N)
    n_tr, n_va = int(0.7 * N), int(0.15 * N)
    split = np.empty(N, np.int8)
    split[perm[:n_tr]], split[perm[n_tr:n_tr + n_va]], split[perm[n_tr + n_va:]] = 0, 1, 2

    return dict(
        feats=feats, choices=choices, outcome=outcome,       # 모델이 보는 것
        w_king=w_king, w0=w0.astype(np.float32),             # 참값 (평가에만 사용)
        target=target.astype(np.float32), alpha=alpha.astype(np.float32),
        static=static, split=split,
    )


def summarize(d: dict, cfg: Config) -> dict:
    lk = d["outcome"] == LOSS_KING
    n_ev = lk.sum(1)
    wk = d["w_king"]
    moving = ~d["static"]
    q = lambda x: [round(float(v), 3) for v in np.quantile(x, [0.1, 0.5, 0.9])]
    G = cfg.n_games
    return {
        "king_attack_loss_rate_first50": round(float(lk[:, :50].mean()), 3),
        "king_attack_loss_rate_last50": round(float(lk[:, -50:].mean()), 3),
        "events_per_player_q10_50_90": q(n_ev),
        "w_start_q": q(wk[:, 0]),
        "w_end_q": q(wk[:, -1]),
        "w_change_moving_q": q(wk[moving, -1] - wk[moving, 0]),
        "w_change_static_q": q(wk[~moving, -1] - wk[~moving, 0]),
        "share_of_change_done_by_game": {
            str(g): round(float(np.median(
                (wk[moving, g] - wk[moving, 0]) / (wk[moving, -1] - wk[moving, 0] + 1e-9))), 3)
            for g in (25, 50, 100, 200) if g < G
        },
        "alpha_moving_q": q(d["alpha"][moving]),
        "n_static": int(d["static"].sum()),
    }


def main():
    ap = argparse.ArgumentParser()
    for k, v in asdict(Config()).items():
        ap.add_argument(f"--{k}", type=type(v), default=v)
    ap.add_argument("--out", default="data/sim_default.npz")
    args = vars(ap.parse_args())
    out = Path(args.pop("out"))
    cfg = Config(**args)

    d = simulate(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **d)
    s = summarize(d, cfg)
    out.with_suffix(".json").write_text(
        json.dumps({"config": asdict(cfg), "summary": s}, indent=2, ensure_ascii=False))
    print(json.dumps(s, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
