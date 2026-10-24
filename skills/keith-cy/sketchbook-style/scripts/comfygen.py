"""Generate images on a ComfyUI server (set COMFY_URL; Qwen-Image 2.1 workflow + optional negative/cfg).
usage: python3 -I comfygen.py jobs.json outdir
jobs.json: [{"name","prompt","neg","w","h","steps","cfg","seed"}...]  (skips names already in outdir)
Takes the optional mkdir lock $GPU_LOCK around each job; never removes a live holder's lock."""
import json, os, sys, time, random, urllib.request, urllib.parse
URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
LOCK = os.environ.get("GPU_LOCK", "/tmp/sketchbook-gpu.lock")
def req(path, body=None, timeout=60):
    r = urllib.request.Request(URL + path, data=json.dumps(body).encode() if body is not None else None,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as f: return f.read()
def take():
    while True:
        try:
            os.mkdir(LOCK); open(LOCK + "/owner", "w").write(f"sketchbook {os.getpid()} {int(time.time())}\n"); return
        except FileExistsError:
            try:
                pid = int(open(LOCK + "/owner").read().split()[1]); os.kill(pid, 0)
            except ProcessLookupError:
                try: os.remove(LOCK + "/owner"); os.rmdir(LOCK)
                except OSError: pass
                continue
            except Exception: pass
            time.sleep(0.03)  # other sessions hand the lock straight to their next job; a slow poll starves
def give():
    try:
        if open(LOCK + "/owner").read().startswith(f"sketchbook {os.getpid()} "):
            os.remove(LOCK + "/owner"); os.rmdir(LOCK)
    except OSError: pass
def wf(j, prefix):
    n = lambda c, i: {"class_type": c, "inputs": i}
    return {
        "1": n("UnetLoaderGGUF", {"unet_name": "qwen-image-2.1-Q6_K.gguf"}),
        "2": n("CLIPLoader", {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}),
        "3": n("VAELoader", {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}),
        "4": n("QwenImage21Cache", {"device": "auto", "dtype": "default", "model": ["1", 0]}),
        "12": n("TextEncodeQwenImage21", {"prompt": j["prompt"], "negative_prompt": j.get("neg", ""), "resolution": 0, "clip": ["2", 0], "vae": ["3", 0]}),
        "13": n("EmptyLatentImage", {"width": j.get("w", 1024), "height": j.get("h", 1024), "batch_size": 1}),
        "14": n("KSampler", {"seed": j.get("seed", random.randint(1, 2**31)), "steps": j.get("steps", 20), "cfg": j.get("cfg", 1.0),
                             "sampler_name": j.get("sampler", "euler"), "scheduler": j.get("scheduler", "simple"), "denoise": 1.0,
                             "model": ["4", 0], "positive": ["12", 0], "negative": ["12", 1], "latent_image": ["13", 0]}),
        "15": n("VAEDecode", {"samples": ["14", 0], "vae": ["3", 0]}),
        "16": n("SaveImage", {"filename_prefix": prefix, "images": ["15", 0]}),
    }
def main():
    jobs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    for j in jobs:
        dst = os.path.join(out, j["name"] + ".png")
        if os.path.exists(dst): continue
        j.setdefault("seed", random.randint(1, 2**31))
        take(); t0 = time.time()
        try:
            pid = json.loads(req("/prompt", {"prompt": wf(j, "sketchbook/" + j["name"])}))["prompt_id"]
            while True:
                time.sleep(4)
                h = json.loads(req("/history/" + pid))
                if pid in h:
                    st = h[pid].get("status", {})
                    if st.get("status_str") == "error": print("ERROR", j["name"], json.dumps(st)[:500], flush=True); break
                    imgs = [i for o in h[pid]["outputs"].values() for i in o.get("images", [])]
                    if imgs:
                        q = urllib.parse.urlencode({k: imgs[0][k] for k in ("filename", "subfolder", "type")})
                        open(dst, "wb").write(req("/view?" + q, timeout=120))
                        meta = dict(j, prompt_id=pid, seconds=round(time.time() - t0), engine="ComfyUI qwen-image-2.1-Q6_K.gguf")
                        json.dump(meta, open(dst[:-4] + ".json", "w"), ensure_ascii=False, indent=1)
                        print("done", j["name"], round(time.time() - t0), "s", flush=True); break
                if time.time() - t0 > 1500: print("TIMEOUT", j["name"], flush=True); break
        finally:
            give()
main()
