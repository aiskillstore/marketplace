# 引擎 / 存档格式速查表

用于回答三个问题：**存档在哪、是什么格式、能不能自动化改**。
「可自动化」一列指本技能当前脚本能否直接给出精确的字节偏移。

## RPG Maker 系列

| 引擎 | 安装目录标志文件 | 默认存档位置 | 格式 | 可自动化 |
|---|---|---|---|---|
| MV / MZ | `www/`、`js/`、`package.json`、`Game.exe` | `%LOCALAPPDATA%<游戏名>/` 或游戏目录 `save/` | 明文 JSON（`file1.rpgsave`），或启用插件后加密 | 高（明文时） |
| VX Ace (RGSS3) | `Game.exe` + `Game.rgss3a` + `Game.ini(RGSS300.dll)` | 游戏安装目录下 `Save01.rvdata2` | Ruby Marshal，**两段流拼接** | **完整支持**（见下） |
| VX (RGSS2) | `Game.exe` + `Game.rgss2a` | 同上，`Save01.rvdata` | Ruby Marshal | 同上 |
| XP (RGSS1) | `RGSS100J.dll` + `Game.rxproj` | 同上，`Save01.rxdata` | Ruby Marshal | 同上 |

### RGSS3 存档细节（实战验证过）

```
Save0X.rvdata2
 ├── Marshal 流 1：DataManager.make_save_header
 │     Hash { :characters => [...], :playtime_s => "00:01:41" }
 └── Marshal 流 2：DataManager.make_save_contents
       Hash 11 项：:system :timer :message :switches :variables
                   :self_switches :actors :party :troop :map :player
```

- `:switches`（`Game_Switches`）的 `@data` 是布尔数组，每项 `'T'`/`'F'`/`'0'`(nil) 各 1 字节
- `:variables`（`Game_Variables`）的 `@data` 是整数数组
- `:map`（`Game_Map`）通常占掉整个文件 99% 的体积
- 想读出CG 开关的**语义**（哪个 ID 对应哪张 CG），需要游戏事件数据：
  - 若解压出了 `Data/Scripts.rvdata2`，可用 `ruby_marshal.py` 解析 + zlib 解压得到全部 Ruby 源码
  - 地图/公共事件数据在加密档 `Game.rgss3a`（RGSSAD v3，magic `RGSSAD`+ver3）里，需另行解密
- CG 回想室若用 Ruby 脚本实现，会出现在自定义脚本段；若纯靠事件 + 开关实现，则只能靠**语义无关**的方式处理（全开关置 ON 或差分）

## 常见 Galgame 引擎

| 引擎 | 标志 | 存档位置 | 备注 |
|---|---|---|---|
| Ren'Py | 目录含 `game/`、`.rpa` 归档、`renpy/` | `%APPDATA%RenPy/<游戏名>persistent` 与 `saves/` | 画廊解锁状态多在 `persistent` 上；可用 `unrpyc` 之类工具读脚本拿到 flag 名，或走差分 |
| Kirikiri / KAG | `.xp3` 归档、`krkr.*.exe` | 游戏目录 `save.dat` / `save/*.sav`，或 `%APPDATA%` | 存档可能明文 (YAML/XML)，也可能被 XOR / 压缩；先做字节熵与可打印性检查 |
| TyranoBuilder | `tyrano/`、`data/` | `%LOCALAPPDATA%` 或浏览器 localStorage | Tyrano v4 存档常为 JSON / localStorage 导出 |
| Unity | `<游戏名>_Data/`、`UnityPlayer.dll` | `%LOCALAPPDATA%Low<厂商>/<游戏名>/` | 多为 `JsonUtility` / `BinaryFormatter` / 自定义二进制；先看有无可读字符串 |
| Unreal Engine | `Content/Paks/`、`*.pak` | `%LOCALAPPDATA%<游戏名>/Saved/SaveGames/` | SaveGame 为自定义二进制，通常用差分 |
| Siglus Engine | `*.pak`、`GameData<n>.pak` | 游戏目录或虚拟化重定向目录 | 存档常有自身加密 |
| BGI / Ethornell | `*.arc`、`BD.bgi` | 游戏目录 `Savedata/` | 多为私有二进制 |
| CatSystem2 | `*.int`、`*.cs2` | 游戏目录 `%APPDATA%` 均有 | 同上 |

## 通用判定口诀

1. **文件头 `04 08`** → Ruby Marshal → 走 `rgss_save.py`
2. **文件可以 `json.load`** → 直接改 JSON，例如 RPG Maker MV/MZ
3. **文件头 `78 9c` / `1f 8b`** → zlib / gzip → 先解压再看
4. **大片可读文本与重复结构** → 多半是结构化明文，用差分最快
5. **整份存档在两个状态间几乎每个字节都变** → 说明存档被整体压缩或流式加密，普通差分失效，需先解决加密/压缩
