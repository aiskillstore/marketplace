/**
 * image-gen.js — 多模式生图工具
 * 
 * 支持四种模式:
 *   auto(默认)  智能选择
 *   fast        硅基流动 API（快速，需 API Key）
 *   enhanced    SDXL 本地（GPU，支持 seed/img2img）
 *   lightweight  SD 1.5 本地（CPU/GPU 兜底）
 *   flux        Flux.1-dev（4-bit，最高画质，需下载模型）
 * 
 * 用法:
 *   node image-gen.js "提示词"
 *   node image-gen.js "提示词" --seed 42
 *   node image-gen.js "提示词" --mode enhanced
 *   node image-gen.js --setup
 *   node image-gen.js --set-default enhanced
 *   node image-gen.js --show-config
 */

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execSync, exec } = require("child_process");
const readline = require("readline");

// ============================================================
//  路径配置
// ============================================================
const TOOLS_DIR = __dirname;
const BACKENDS_DIR = path.join(TOOLS_DIR, "backends");
const CONFIG_PATH = path.join(TOOLS_DIR, "config.json");
const DEFAULT_OUTPUT = path.join(TOOLS_DIR, "..", "outputs");
const NODE_PATH = process.execPath;

// .env 查找顺序: 脚本目录旁 .env → 上级 tools/.env
const ENV_PATH = fs.existsSync(path.join(TOOLS_DIR, ".env"))
    ? path.join(TOOLS_DIR, ".env")
    : path.join(TOOLS_DIR, "..", "..", "tools", ".env");

function loadEnvKey(name) {
    try {
        if (process.env[name]) return process.env[name].trim();
        if (fs.existsSync(ENV_PATH)) {
            const env = fs.readFileSync(ENV_PATH, "utf-8");
            const m = env.match(new RegExp(name + "\\s*=\\s*(.+)"));
            if (m) return m[1].trim();
        }
    } catch (_) {}
    return null;
}

// ============================================================
//  配置加载与保存
// ============================================================
function loadConfig() {
    if (fs.existsSync(CONFIG_PATH)) {
        try {
            const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
            // .env 中的 SILICONFLOW_API_KEY 优先级最高（与代理共用同一份 key）
            const envKey = loadEnvKey("SILICONFLOW_API_KEY");
            if (envKey) cfg.siliconflow.apiKey = envKey;
            return cfg;
        } catch (e) {
            console.error(`[image-gen] 配置加载失败: ${e.message}`);
        }
    }
    return {
        mode: "auto",
        default_mode: "auto",
        siliconflow: { enabled: false, apiKey: "", defaultModel: "Tongyi-MAI/Z-Image-Turbo", size: "1280x720" },
        sdxl: { enabled: false, modelPath: "", size: "1024x1024" },
        sd15: { enabled: false, modelPath: "", size: "512x512" },
        flux: { enabled: false, modelPath: "", size: "1024x1024" }
    };
}

function saveConfig(config) {
    const dir = path.dirname(CONFIG_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), "utf-8");
    console.log(`[image-gen] 配置已保存: ${CONFIG_PATH}`);
}

// ============================================================
//  设置向导 (--setup)
// ============================================================
function detectGPU() {
    try {
        const out = execSync("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", { encoding: "utf-8", timeout: 5000 });
        const match = out.trim().match(/(.+),\s*(\d+)\s*MiB/);
        if (match) {
            const name = match[1].trim();
            const vramMB = parseInt(match[2]);
            return { name, vramMB };
        }
    } catch (_) {}
    try {
        const out = execSync("wmic path Win32_VideoController get Name", { encoding: "utf-8", timeout: 5000 });
        const lines = out.split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("Name"));
        if (lines.length > 0) return { name: lines[0], vramMB: 0 };
    } catch (_) {}
    return null;
}

function recommendMode(gpu) {
    if (!gpu) return "lightweight";
    if (gpu.vramMB >= 12000) return "flux";
    if (gpu.vramMB >= 8000) return "enhanced";
    if (gpu.vramMB >= 4000) return "lightweight";
    return "lightweight";
}

function askQuestion(query) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    return new Promise(resolve => rl.question(query, answer => { rl.close(); resolve(answer.trim()); }));
}

async function setupWizard() {
    console.log("");
    console.log("╔══════════════════════════════════════════════════╗");
    console.log("║        image-gen.js 安装向导                     ║");
    console.log("╚══════════════════════════════════════════════════╝");
    console.log("");

    // 检测 GPU
    const gpu = detectGPU();
    if (gpu) {
        console.log(`  检测到显卡: ${gpu.name} (${gpu.vramMB} MB VRAM)`);
    } else {
        console.log("  未检测到 NVIDIA 显卡，将使用 CPU 兜底模式");
    }

    const recommended = recommendMode(gpu);
    console.log(`  推荐默认模式: ${recommended}`);
    console.log("");

    // 模式选择
    console.log("  可选默认模式:");
    console.log("    [1] enhanced      — SDXL 本地，1024×1024，画质最高 (推荐)");
    console.log("    [2] fast          — 硅基流动 API，需 API Key，速度快");
    console.log("    [3] lightweight   — SD 1.5 本地，512×512，轻量兜底");
    console.log("    [4] flux          — Flux.1-dev 本地，最高画质（需下载模型）");
        console.log("    [5] auto          — 智能选择");
    console.log("");

    const modeNames = { "1": "enhanced", "2": "fast", "3": "lightweight", "4": "flux", "5": "auto" };
    let defaultMode = recommended;
    
    if (process.stdin.isTTY) {
        const answer = await askQuestion(`  请输入编号 [1-4]，回车使用推荐值 (${recommended}): `);
        if (modeNames[answer]) defaultMode = modeNames[answer];
    } else {
        console.log("  (非交互环境，使用推荐值)");
    }

    // 加载现有配置，更新 default_mode
    const config = loadConfig();
    config.default_mode = defaultMode;
    
    // 根据选择的模式自动启用对应的后端
    if (defaultMode === "enhanced") {
        config.sdxl.enabled = true;
    } else if (defaultMode === "lightweight") {
        config.sd15.enabled = true;
    }
    config.mode = defaultMode;

    saveConfig(config);
    console.log("");
    console.log("  ✅ 安装完成！");
    console.log(`  默认模式已设为: ${defaultMode}`);
    console.log("  现在可以直接使用:");
    console.log(`    node image-gen.js "提示词"`);
    console.log("  或指定模式:");
    console.log(`    node image-gen.js --mode enhanced "提示词"`);
    console.log("");
}

// ============================================================
//  设置默认模式 (--set-default)
// ============================================================
function setDefaultMode(mode) {
    const valid = ["enhanced", "fast", "lightweight", "auto"];
    if (!valid.includes(mode)) {
        console.error(`[image-gen] 无效模式: ${mode}，可选: ${valid.join(", ")}`);
        process.exit(1);
    }
    const config = loadConfig();
    config.default_mode = mode;
    config.mode = mode;
    
    // 自动启用对应的后端
    if (mode === "enhanced") config.sdxl.enabled = true;
    if (mode === "lightweight") config.sd15.enabled = true;

    saveConfig(config);
    console.log(`[image-gen] 默认模式已设为: ${mode}`);
}

// ============================================================
//  显示配置 (--show-config)
// ============================================================
function showConfig() {
    const config = loadConfig();
    console.log("");
    console.log("  当前配置:");
    console.log(`    默认模式:        ${config.default_mode || config.mode}`);
    console.log(`    硅基流动:        ${config.siliconflow.enabled ? "已启用" : "未启用"}`);
    console.log(`    SDXL 本地:        ${config.sdxl.enabled ? "已启用" : "未启用"}`);
    console.log(`    SD 1.5 本地:      ${config.sd15.enabled ? "已启用" : "未启用"}`);
    console.log(`    输出目录:         ${DEFAULT_OUTPUT}`);
    console.log(`    配置文件:         ${CONFIG_PATH}`);
    if (config.siliconflow.apiKey) {
        const key = config.siliconflow.apiKey;
        console.log(`    硅基 API Key:     ${key.substring(0, 8)}...${key.substring(key.length - 4)}`);
    }
    console.log("");
}

// ============================================================
//  参数解析
// ============================================================
function parseArgs(argv) {
    const args = argv.slice(2);
    const opts = {
        prompt: "",
        mode: null,
        size: null,
        seed: null,
        img2img: null,
        strength: 0.7,
        output: DEFAULT_OUTPUT,
        filename: null,
        model: null,
        config: CONFIG_PATH,
        setup: false,
        setDefault: null,
        negativePrompt: null,
        steps: null,
        cfgScale: null,
        scheduler: null,
        batch: 1,
        refiner: false,
        open: false,
        showConfig: false
    };

    let i = 0;
    while (i < args.length) {
        if (args[i] === "--mode" && args[i + 1]) {
            opts.mode = args[++i];
        } else if (args[i] === "--size" && args[i + 1]) {
            opts.size = args[++i];
        } else if (args[i] === "--seed" && args[i + 1]) {
            opts.seed = parseInt(args[++i]);
        } else if (args[i] === "--img2img" && args[i + 1]) {
            opts.img2img = args[++i];
        } else if (args[i] === "--strength" && args[i + 1]) {
            opts.strength = parseFloat(args[++i]);
        } else if (args[i] === "--negative-prompt" && args[i + 1]) {
            opts.negativePrompt = args[++i];
        } else if (args[i] === "--steps" && args[i + 1]) {
            opts.steps = parseInt(args[++i]);
        } else if (args[i] === "--cfg-scale" && args[i + 1]) {
            opts.cfgScale = parseFloat(args[++i]);
        } else if (args[i] === "--scheduler" && args[i + 1]) {
            opts.scheduler = args[++i];
        } else if (args[i] === "--refiner") {
            opts.refiner = true;
        } else if (args[i] === "--batch" && args[i + 1]) {
            opts.batch = parseInt(args[++i]);
        } else if (args[i] === "--output" && args[i + 1]) {
            opts.output = args[++i];
        } else if (args[i] === "--filename" && args[i + 1]) {
            opts.filename = args[++i];
        } else if (args[i] === "--config" && args[i + 1]) {
            opts.config = args[++i];
        } else if (args[i] === "--model" && args[i + 1]) {
            opts.model = args[++i];
        } else if (args[i] === "--setup") {
            opts.setup = true;
        } else if (args[i] === "--set-default" && args[i + 1]) {
            opts.setDefault = args[++i];
        } else if (args[i] === "--show-config") {
            opts.showConfig = true;
        } else if (args[i] === "--open") {
            opts.open = true;
        } else if (!opts.prompt) {
            opts.prompt = args[i];
        }
        i++;
    }

    return opts;
}

// ============================================================
//  模式选择
// ============================================================
function selectMode(opts, config) {
    // 手动指定模式
    if (opts.mode === "fast") return "siliconflow";
    if (opts.mode === "enhanced") return "sdxl";
    if (opts.mode === "lightweight") return "sd15";
    if (opts.mode === "flux") return "flux";

    // auto 模式：读 config 中的默认设置
    let defaultMode = config.default_mode || "auto";
    
    if (opts.mode === "auto" || opts.mode === null) {
        if (defaultMode !== "auto") {
            // 用户设置了固定默认
            if (defaultMode === "fast") return "siliconflow";
            if (defaultMode === "enhanced") return "sdxl";
            if (defaultMode === "lightweight") return "sd15";
            if (defaultMode === "flux") return "flux";
        }
    }

    // 需要 seed/img2img 时强制本地
    const needLocal = opts.img2img || opts.seed !== null;

    if (needLocal) {
        if (config.sdxl.enabled) return "sdxl";
        if (config.sd15.enabled) return "sd15";
        console.error("[image-gen] seed/img2img 需要本地模型 (SDXL/SD 1.5)，请先运行 --setup");
        process.exit(1);
    }

    // 智能选择：API > SDXL > SD15
    if (config.siliconflow.enabled && config.siliconflow.apiKey) return "siliconflow";
    if (config.sdxl.enabled) return "sdxl";
    if (config.sd15.enabled) return "sd15";

    console.error("[image-gen] 没有可用的生图模式。运行 node image-gen.js --setup 进行安装配置");
    process.exit(1);
}

// ============================================================
//  模式 A: 硅基流动 API
// ============================================================
function runSiliconFlow(opts, config) {
    const size = opts.size || config.siliconflow.size || "1280x720";
    const model = opts.model || config.siliconflow.defaultModel;
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").substring(0, 19);
    const filename = opts.filename || `imagegen-${timestamp}.png`;
    const outputPath = path.join(opts.output, filename);
    const apiKey = config.siliconflow.apiKey;

    // 硅基流动 API 不支持 seed 固定
    const seed = Math.floor(Math.random() * 2147483647);

    return new Promise((resolve, reject) => {
        const requestBody = JSON.stringify({
            model: model,
            prompt: opts.prompt,
            image_size: size
        });

        const req = https.request({
            hostname: "api.siliconflow.cn",
            path: "/v1/image/generations",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            }
        }, (res) => {
            const chunks = [];
            res.on("data", c => chunks.push(c));
            res.on("end", () => {
                const data = JSON.parse(Buffer.concat(chunks).toString());
                if (data.data && data.data[0] && data.data[0].url) {
                    downloadImage(data.data[0].url, outputPath).then(() => {
                        resolve({ path: outputPath, seed: seed });
                    }).catch(reject);
                } else {
                    reject(new Error("API 返回异常: " + JSON.stringify(data)));
                }
            });
        });
        req.on("error", reject);
        req.write(requestBody);
        req.end();
    });
}

function downloadImage(url, dest) {
    return new Promise((resolve, reject) => {
        const proto = url.startsWith("https") ? https : http;
        proto.get(url, (res) => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                return downloadImage(res.headers.location, dest).then(resolve).catch(reject);
            }
            const file = fs.createWriteStream(dest);
            res.pipe(file);
            file.on("finish", () => { file.close(); resolve(); });
            file.on("error", reject);
        }).on("error", reject);
    });
}

// ============================================================
//  模式 B/C: 本地模型 (SDXL / SD 1.5)
// ============================================================
function runLocalModel(opts, config, mode) {
    const scriptName = mode === "sdxl" ? "sdxl_gen.py" : (mode === "flux" ? "flux_gen.py" : "sd15_gen.py");
    const scriptPath = path.join(BACKENDS_DIR, scriptName);
    const defaultSize = mode === "sdxl" || mode === "flux" ? "1024x1024" : "512x512";
    const size = opts.size || (config[mode] && config[mode].size) || defaultSize;
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").substring(0, 19);
    const filename = opts.filename || `imagegen-${timestamp}.png`;
    const outputPath = path.join(opts.output, filename);

    const args = [
        scriptPath,
        "--prompt", opts.prompt,
        "--size", size,
        "--output", outputPath
    ];
    if (opts.seed !== null) {
        args.push("--seed", String(opts.seed));
    }
    if (opts.img2img) {
        args.push("--img2img", opts.img2img);
        args.push("--strength", String(opts.strength));
    }
    if (opts.negativePrompt) {
        args.push("--negative-prompt", opts.negativePrompt);
    }
    if (opts.steps) {
        args.push("--steps", String(opts.steps));
    }
    if (opts.cfgScale) {
        args.push("--cfg-scale", String(opts.cfgScale));
    }
    if (opts.scheduler) {
        args.push("--scheduler", opts.scheduler);
    }
    if (opts.refiner) {
        args.push("--refiner");
    }

    return new Promise((resolve, reject) => {
        const proc = exec(`python "${args.join('" "')}"`, {
            cwd: BACKENDS_DIR,
            maxBuffer: 10 * 1024 * 1024
        }, (error, stdout, stderr) => {
            if (error) {
                console.error(stderr);
                reject(error);
                return;
            }
            console.log(stdout);
            const pathMatch = stdout.match(/OUTPUT_PATH=(.+)/);
            const seedMatch = stdout.match(/SEED=(\d+)/);
            const resultPath = pathMatch ? pathMatch[1].trim() : null;
            const resultSeed = seedMatch ? parseInt(seedMatch[1]) : null;
            if (resultPath) {
                resolve({ path: resultPath, seed: resultSeed });
            } else {
                reject(new Error("未获取到输出路径"));
            }
        });
    });
}

// ============================================================
//  格式化耗时
// ============================================================
function formatTime(ms) {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}秒`;
    const min = Math.floor(ms / 60000);
    const sec = ((ms % 60000) / 1000).toFixed(0);
    return `${min}分${sec}秒`;
}

// ============================================================
//  主流程
// ============================================================
async function main() {
    const startTime = Date.now();
    const opts = parseArgs(process.argv);

    // 特殊命令: 安装向导
    if (opts.setup) {
        await setupWizard();
        return;
    }

    // 特殊命令: 设置默认模式
    if (opts.setDefault) {
        setDefaultMode(opts.setDefault);
        return;
    }

    // 特殊命令: 显示配置
    if (opts.showConfig) {
        showConfig();
        return;
    }

    // 没有提示词时显示帮助
    if (!opts.prompt) {
        console.log("");
        console.log("  用法: node image-gen.js \"提示词\" [选项]");
        console.log("");
        console.log("  选项:");
        console.log("    --mode auto|fast|enhanced|lightweight    模式选择");
        console.log("    --seed NUM                               固定随机种子");
        console.log("    --img2img PATH                           图生图参考图");
        console.log("    --strength 0.0-1.0                       img2img 强度");
        console.log("    --negative-prompt TEXT                   负提示词（用引号括起来）");
        console.log("    --steps NUM                              推理步数（默认: 40）");

        console.log("    --cfg-scale NUM                         引导强度（默认: 7.0）");
        console.log("    --scheduler euler|dpm++|dpm++_karras     调度器类型（默认: dpm++_karras）");
        console.log("    --batch NUM                              批量生成张数（默认: 1）");
        console.log("    --refiner                                启用 SDXL refiner 细化");
        console.log("    --size WxH                               输出尺寸");
        console.log("    --output DIR                             输出目录");
        console.log("    --filename NAME                          输出文件名");
        console.log("    --model MODEL                            指定模型名");
        console.log("    --setup                                  运行安装向导");
        console.log("    --set-default MODE                       设置默认模式");
        console.log("    --show-config                            查看当前配置");
        console.log("    --open                                  生成后自动打开图片");
        console.log("");
        console.log("  示例:");
        console.log("    node image-gen.js \"一只小猫\"");
        console.log("    node image-gen.js \"海边日出\" --seed 42");
        console.log("    node image-gen.js \"大师级油画\" --mode enhanced");
        console.log("    node image-gen.js --setup");
        console.log("");
        return;
    }

    const config = loadConfig();
    const resolvedMode = selectMode(opts, config);
    const modeName = { siliconflow: "fast", sdxl: "enhanced", sd15: "lightweight", flux: "flux" }[resolvedMode] || resolvedMode;
    const modeLabel = { siliconflow: "硅基流动 API", sdxl: "SDXL 本地", sd15: "SD 1.5 本地", flux: "Flux 本地" }[resolvedMode] || resolvedMode;

    console.log(`[image-gen] 模式: ${modeLabel}`);
    console.log(`[image-gen] 提示词: ${opts.prompt}`);
    if (opts.seed !== null) console.log(`[image-gen] 指定种子: ${opts.seed}`);
    if (opts.img2img) console.log(`[image-gen] 参考图: ${opts.img2img}`);
    const batchCount = opts.batch || 1;
    if (batchCount > 1) console.log(`[image-gen] 批量模式: ${batchCount} 张`);

    if (!fs.existsSync(opts.output)) {
        fs.mkdirSync(opts.output, { recursive: true });
    }

    try {
        const batchCount = opts.batch || 1;
        let lastResult = null;
        for (let b = 0; b < batchCount; b++) {
                    const batchOpts = { ...opts };
        if (batchCount > 1) {
                    batchOpts.seed = opts.seed !== null ? opts.seed + b : null;
                    if (opts.filename) {
                                batchOpts.filename = opts.filename.replace(/(\.[^.\/\\]+)$/, '_' + (b + 1) + '$1');
                    }
                    if (b > 0) console.log("");
                    console.log(`[image-gen] 批量生成第 ${b + 1}/${batchCount} 张`);
        }
        let result;
        if (resolvedMode === "siliconflow") {
                    result = await runSiliconFlow(batchOpts, config);
        } else {
                    result = await runLocalModel(batchOpts, config, resolvedMode);
        }
        lastResult = result;

        const elapsed = Date.now() - startTime;
        const sizeLabel = opts.size || (resolvedMode === "sdxl" ? "1024×1024" : resolvedMode === "sd15" ? "512×512" : "");
        console.log("");
        console.log("  ✅ 图片已生成");
        console.log(`  📄 文件: ${result.path}`);
        console.log(`  🎯 Seed: ${result.seed !== null ? result.seed : "未记录"}`);
        console.log(`  ⚙️ 模式: ${modeLabel}`);
        console.log(`  📐 分辨率: ${sizeLabel}`);
        console.log(`  ⏱ 耗时: ${formatTime(elapsed)}`);
        if (result.seed !== null) {
                    console.log(`  💡 提示: 下次用 --seed ${result.seed} + 相同提示词可复现这张图`);
        }
        console.log('OUTPUT_PATH=' + result.path);
        console.log('REMINDER: 生图完成，不要调用 view_image。仅记录 OUTPUT_PATH。');
        console.log("");
        }
        if (opts.open && lastResult) {
                    try {
                                const { execSync } = require("child_process");
                                execSync('start "" "' + lastResult.path + '"', { shell: true });
                                console.log("  🖼️ 已打开最后一张图片到系统查看器");
                    } catch (openErr) {
                                console.error("  ⚠️ 无法打开图片: " + openErr.message);
                    }
        }
    } catch (err) {
        console.error(`[image-gen] 错误: ${err.message}`);
        process.exit(1);
    }
}

main().catch(err => {
    console.error(`[image-gen] 错误: ${err.message}`);
    process.exit(1);
});
