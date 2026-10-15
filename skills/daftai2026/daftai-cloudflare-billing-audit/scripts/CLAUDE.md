# scripts/
> L2 | 父级: ../CLAUDE.md

职责：离线有界扫描、受控证据读取与外置报告；不执行目标项目代码。依赖方向从入口到编排，再到领域逻辑与文件访问，最后到共享类型和身份原语；禁止底层反向导入入口。

- `audit.ts`：CLI 与兼容公共导出门面。
- `audit-engine.ts`：扫描编排、配额、报告、证据清单及指纹复核。
- `audit-types.ts`：报告/API 类型、默认上限和静态集合。
- `audit-fs.ts`：真实宿主平台选择、共享接口、Windows 原始路径验证；Linux 不自动降级。
- `linux-fs.ts`：Linux 描述符锚定遍历、读取和独占输出。
- `portable-fs.ts`：macOS/Windows 稳定目录树访问，前后身份/真实路径校验；不承诺原子快照或恶意并发隔离。
- `fs-common.ts`：路径包含关系、对象守卫和身份指纹原语。
- `discovery.ts`：发现边界、敏感路径排除、候选与有界读取。
- `config.ts`：JSONC/TOML 解析、环境/绑定/入口与辅助证据范围。
- `source-scan.ts`：词法遮罩与候选风险规则，不构建调用图。
- `audit.test.ts`：核心配置、扫描、有界读取回归。
- `audit.security.test.ts`：Linux 描述符与确定性竞态回归，仅真实 Linux 执行。
- `audit.portable.test.ts`：真实宿主与显式稳定树适配器测试；不伪造平台。
- `audit.regression.test.ts`：大小写别名与大库存受控读回回归。
- `installed-smoke.ts`：校验指定安装目录的文件哈希，使用虚构夹具运行 CLI、受控读取及契约测试。

测试均使用虚构夹具；实际 macOS/Windows 运行结果须由对应宿主验证，Linux 适配器测试不能替代。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
