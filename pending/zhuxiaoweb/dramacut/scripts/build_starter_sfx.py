"""Build the original, deterministic synthetic SFX starter pack; no external samples."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys
import wave

sys.dont_write_bytecode = True
from sfx_library import measure, sha, save

RATE = 24000
PACK = [
    ("impact_soft", "轻短触点", .38, "hit", ["impact"], "轻触、落手或次要接触的合成补强", "真实耳光、拳头、枪声；这些需要原声或真实拟音", -3, 165),
    ("impact_body", "中频短冲击", .48, "hit", ["impact"], "已有动作接触原声的中频补强，手机扬声器仍可读", "没有可见接触的普通换镜", -1, 120),
    ("impact_hard", "硬短冲击", .55, "metal", ["impact", "reveal"], "强动作或攻守翻转的单次设计重音", "每句话、普通反应；不冒充真实打斗拟音", -1, 200),
    ("impact_low", "低频带谐波重音", .7, "low", ["impact", "reveal"], "重磅信息落定，叠原声时只作情绪层", "连续密集击打、柔情句尾", -1, 65),
    ("impact_metal", "金属色短强调", .52, "metal", ["impact"], "硬质物件或锋利立场的合成强调", "真实玻璃碎裂、刀剑撞击等具体拟音", -2, 520),
    ("motion_light", "轻划过", .42, "swish", ["motion"], "确有快速转头、视线或物件带动的轻运动强调", "静态脸部跳切遮盖；没有运动的普通正反打", -3, 1600),
    ("motion_fast", "快划过", .28, "swish", ["motion"], "短促可见运动，主能量对动作最快处", "拿文件头替代运动命中点", -2, 2600),
    ("motion_weighted", "带重量划过", .65, "swish_low", ["motion"], "快速逼近、扑压或较重动作的情绪运动层", "细小手势、温和谈话", -1, 900),
    ("motion_reverse", "反向蓄势划过", .7, "reverse", ["motion", "riser"], "揭晓前短促吸入，结尾接独立主重音", "提前泄露秘密的脸部揭晓；单独冒充动作拟音", -2, 1800),
    ("riser_short", "短促升压", 1.5, "riser", ["riser", "dread"], "危险或揭晓前约一秒蓄势，主攻击在后部", "无剧情依据地每隔固定秒数出现", -2, 1200),
    ("recognition_tick", "意识轻敲", .25, "tick", ["recognition"], "角色首次注意到一个细节或话语转义", "普通眨眼、无信息表情", -3, 880),
    ("recognition_glint", "线索微亮", .65, "chime", ["recognition"], "证据或人名变得可辨的一拍", "持续闪光装饰或没有新线索的道具", -3, 1320),
    ("notification_double", "双短电子提示", .55, "double", ["phone"], "画面明确出现通知时可选的非品牌合成提示", "电话铃声、真实手机品牌提示或无手机画面", -3, 1000),
    ("dread_drop", "下沉短低压", 1.15, "drop", ["dread", "reveal"], "人物意识到代价或局势恶化的一次下沉", "喜剧情节、每个近景都放低频", -2, 190),
    ("heart_sink", "心沉空气感", .95, "air_drop", ["dread", "recognition"], "失望或意识受伤，避开关键名字的辅音", "真正心跳、喘息或角色医学状态的拟音", -3, 320),
    ("tension_pulse", "不安双脉冲", 1.1, "pulse", ["dread"], "一次追问或压力递进，两个脉冲属于同一事件", "算成两个独立剧情事件；循环冒充BGM", -2, 140),
    ("reveal_low", "揭晓暗重音", .9, "low", ["reveal"], "秘密成立、反派占上风的暗色落点", "信息尚未清楚时抢先落下", -1, 85),
    ("reveal_bright", "揭晓亮冲击", .8, "bright", ["reveal"], "有利真相、身份揭明或转守为攻", "悲伤或哀悼对白", -1, 560),
    ("reversal_snap", "反转急扣", .46, "snap", ["reveal", "decision"], "立场骤变或一句明确拒绝的短重音", "没有剧情转折的普通剪口", -1, 360),
    ("tail_question", "片尾疑点", 1.25, "question", ["tail", "dread"], "具体未解问题或危险停在片尾", "平静结束、任何集尾都机械放同一声", -2, 440),
    ("decision_knock", "决定轻扣", .42, "knock", ["decision"], "人物作出承诺或明确边界的一拍", "真实敲门；这是情绪提示，不是门拟音", -3, 260),
    ("warm_chime", "关心暖提示", .9, "warm", ["warmth", "decision"], "关心被接受、关系暂时缓和的轻情绪提示", "冲突指责、危险追击", -3, 523.25),
    ("memory_shimmer", "记忆微散", 1.5, "memory", ["recognition", "motion"], "画面确有闪回或记忆入口时的轻声桥", "用来遮盖所有不连贯接点；冒充耳鸣", -3, 660),
    ("resolve_accent", "坚定短音", .75, "resolve", ["decision", "tail"], "明确选择后的收束，保留后一句空间", "复杂旋律BGM、无决定的一般对白", -2, 196),
]


def tone(t, f, decay, harmonics=1):
    return math.sin(2 * math.pi * f * t) * math.exp(-t * decay) + (
        .28 * math.sin(2 * math.pi * f * 2 * t) * math.exp(-t * decay * 1.4) if harmonics else 0)


def synth(identifier, duration, mode, frequency, peak_db):
    rng = random.Random(int(hashlib.sha256(identifier.encode()).hexdigest()[:16], 16))
    result, noise_state, high_state = [], 0., 0.
    length = round(duration * RATE)
    for i in range(length):
        t = i / RATE
        noise = rng.uniform(-1, 1)
        noise_state += .12 * (noise - noise_state)
        high = noise - high_state
        high_state += .25 * (noise - high_state)
        x = 0.
        delay = .035
        v = max(0., t - delay)
        if t >= delay:
            if mode in ("hit", "metal", "low", "knock", "snap"):
                decay = {"hit": 19, "metal": 13, "low": 7, "knock": 25, "snap": 27}[mode]
                x = tone(v, frequency, decay) + .25 * high * math.exp(-v * (35 if mode != "metal" else 22))
                if mode == "metal":
                    x += .5 * math.sin(2 * math.pi * frequency * 1.73 * v) * math.exp(-v * 10)
                if mode == "low":
                    x += .25 * tone(v, frequency * 3, 12)
                if mode == "snap":
                    x += .6 * high * math.exp(-v * 50)
                x *= min(1, v / .0025)
            elif mode in ("swish", "swish_low"):
                center = duration * .49
                env = math.exp(-((t - center) / (duration * .19)) ** 2)
                x = (high * .7 + noise_state * (.75 if mode == "swish_low" else .2)) * env
                if mode == "swish_low":
                    x += .18 * math.sin(2 * math.pi * 140 * t) * env
            elif mode in ("reverse", "riser"):
                at = duration * .8
                if t < at:
                    env = (max(0, (t - delay) / (at - delay))) ** 2.2
                    x = (.5 * high + .3 * math.sin(2 * math.pi * (frequency * v + 400 * v * v))) * env
                else:
                    dt = t - at
                    x = .6 * tone(dt, 140, 18) + .2 * high * math.exp(-dt * 24)
            elif mode == "tick":
                x = (.8 * tone(v, frequency, 35) + .2 * high * math.exp(-v * 65)) * min(1, v / .001)
            elif mode in ("chime", "warm", "bright", "memory", "resolve"):
                notes = {"chime": [1, 2], "warm": [1, 1.25, 1.5], "bright": [1, 1.5, 2],
                         "memory": [1, 1.4983, 2.003], "resolve": [1, 1.5]}[mode]
                attack = .006 if mode != "memory" else .07
                decay = 5 if mode != "memory" else 3.8
                x = sum(tone(v, frequency * n, decay, 0) / len(notes) for n in notes) * min(1, v / attack)
                if mode == "bright":
                    x += .35 * high * math.exp(-v * 30)
            elif mode == "double":
                for at, freq in ((0, frequency), (.19, frequency * 1.25)):
                    if v >= at:
                        z = v - at
                        x += tone(z, freq, 35, 0) * min(1, z / .004)
            elif mode in ("drop", "air_drop"):
                env = min(1, v / .015) * math.exp(-v * 6)
                phase = 2 * math.pi * (frequency * v - 100 * v * v)
                x = (.7 * math.sin(phase) + .22 * math.sin(phase * 2) + .35 * noise_state) * env
                if mode == "air_drop":
                    x += .5 * high * math.exp(-((t - .19) / .09) ** 2)
            elif mode == "pulse":
                for at in (0, .34):
                    if v >= at:
                        z = v - at
                        x += tone(z, frequency, 13) * min(1, z / .01)
            elif mode == "question":
                x = (tone(v, frequency, 5, 0) + .35 * tone(v, frequency * 1.05946, 5, 0)) * min(1, v / .015)
                x += .1 * noise_state * math.exp(-v * 5)
        # Explicit terminal taper prevents a sample discontinuity, not an artificial gate mid-tail.
        x *= min(1, (duration - t) / .045)
        result.append(x)
    maximum = max(abs(v) for v in result)
    gain = 10 ** (peak_db / 20) / maximum
    return [max(-32768, min(32767, round(v * gain * 32767))) for v in result]


def encoded_wave(samples):
    import io
    stream = io.BytesIO()
    with wave.open(stream, "wb") as dest:
        dest.setnchannels(1)
        dest.setsampwidth(2)
        dest.setframerate(RATE)
        dest.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return stream.getvalue()


def build(output, verify=False):
    output = Path(output).expanduser().resolve()
    if not verify:
        output.mkdir(parents=True, exist_ok=True)
    assets = []
    for identifier, name, duration, mode, classes, use, avoid, peak, frequency in PACK:
        path = output / (identifier + ".wav")
        raw = encoded_wave(synth(identifier, duration, mode, frequency, peak))
        checksum = hashlib.sha256(raw).hexdigest()
        if path.exists():
            if sha(path) != checksum:
                raise ValueError(f"Existing generated asset differs; preserve it and choose another output: {path}")
        elif verify:
            raise ValueError(f"Missing generated asset: {path}")
        else:
            path.write_bytes(raw)
        evidence = measure(path, max_seconds=None)
        assets.append({"id": identifier, "file": path.name, "label": name, "sha256": checksum,
                       "event_classes": classes, "tags": [name, mode, *classes], "mix_role": "sfx",
                       "use": use, "avoid": avoid, "synthetic": True,
                       "provenance": "Original deterministic oscillators + seeded noise; no third-party audio samples",
                       "license": "CC0-1.0", "measured": {k: evidence[k] for k in (
                           "analyzed_duration_us", "estimated_onset_us", "estimated_main_attack_us", "estimated_tail_end_us",
                           "peak_sample_us", "peak_dbfs", "rms_dbfs", "crest_db", "attack_candidates")},
                       "listening_status": "not_subjectively_auditioned", "attack_status": "waveform_candidate_requires_picture_and_listening_confirmation"})
    manifest = {"schema_version": 1, "pack_id": "original_short_drama_synthetic_starter_v1",
                "description": "24 original synthetic accents, stingers and motion cues. Not real-world Foley and not BGM.",
                "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "sample_rate": RATE, "channels": 1, "sample_width": 2,
                "generation": "build_starter_sfx.py; standard-library oscillators and seeded noise only",
                "quality_scope": "PCM/peaks/attack estimates verified; subjective listening not asserted",
                "assets": assets}
    if not verify:
        save(output / "manifest.json", manifest)
        (output / "LICENSE.txt").write_text(
            "Original synthetic Short Drama SFX Starter v1\n\n"
            "All 24 WAV files were generated from oscillators and seeded noise by build_starter_sfx.py. "
            "No third-party recordings, songs, film excerpts or other source audio are included.\n\n"
            "The contributor dedicates these generated audio files to the public domain under CC0 1.0 "
            "Universal, to the extent permitted by law. You may copy, modify, distribute and use them "
            "commercially without attribution. No warranty or endorsement is provided.\n"
            "CC0 legal code: https://creativecommons.org/publicdomain/zero/1.0/legalcode\n\n"
            "These are designed sound accents, not authentic recordings of physical actions or medical "
            "sounds. Waveform measurements do not constitute listening or picture/event approval.\n", encoding="utf-8")
    return {"output": str(output), "assets": len(assets), "wav_bytes": sum((output / row["file"]).stat().st_size for row in assets),
            "status": "verified" if verify else "built", "subjective_audio_listening": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(Path(__file__).resolve().parents[1] / "assets/sfx"))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output, args.verify), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Starter pack unavailable: {exc}\n")


if __name__ == "__main__":
    main()
