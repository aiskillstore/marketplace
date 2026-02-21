# 典型翻译样本

> 展示用户偏好的翻译风格，供子 Agent 作为"基调锚点"。
> 每条样本包含原文片段、译文片段和说明（可选）。
>
> **此文件不会被清理**——随使用逐步积累，翻译时自动加载。

---

## 样本 1：技术文档

**原文**：
> When you deploy a model to production, it is important to note that latency can vary significantly depending on the batch size and the hardware configuration. Users should carefully monitor the inference throughput and adjust parameters accordingly.

**译文**：
> 模型上线后，延迟会因批量大小和硬件配置而明显波动。需要持续监控推理吞吐量，及时调整参数。

**说明**：删除了 "it is important to note that" 等不承载信息的填充结构，"Users should" 不译为"用户应该"而是直接用无主语祈使句。整体简洁干脆，一句一个落点。

---

## 样本 2：博客文章

**原文**：
> I've been playing around with this new framework for about two weeks now, and honestly? It's kind of blown my mind. The developer experience is just *chef's kiss*. But — and this is a big but — the documentation is, well, let's just say it leaves something to be desired.

**译文**：
> 这个新框架我折腾了差不多两周，说实话？有点上头。开发体验堪称绝了。但是——这个"但是"很关键——文档嘛，怎么说呢，只能说还有很大的进步空间。

**说明**：保留了作者口语化的节奏感和破折号的戏剧效果。"chef's kiss" 不直译而是用"绝了"传递同样的赞叹情绪。"leaves something to be desired" 用委婉的中文口语化表达。

---

## 样本 3：学术/研究

**原文**：
> Our experiments demonstrate that the proposed method achieves state-of-the-art performance on three benchmark datasets, outperforming the previous best results by 2.3% on average. Notably, the improvement is most pronounced in low-resource scenarios, suggesting that the model's inductive biases are well-suited for data-scarce domains.

**译文**：
> 实验表明，本文方法在三个基准数据集上均达到了最优性能，平均超出此前最佳结果 2.3%。值得关注的是，低资源场景下提升最为显著，这说明该模型的归纳偏置特别适合数据稀缺的领域。

**说明**：学术文体保持严谨书面风格。"state-of-the-art" 译为"最优"而非"最先进的"（后者口语化）。"Notably" 译为"值得关注的是"而非"值得注意的是"（后者已被用滥）。被动句适度保留，符合学术规范。

---

## 样本 4：产品/README

**原文**：
> Get started in under 5 minutes. No configuration required. Just install, import, and start building amazing things.

**译文**：
> 5 分钟上手，零配置。安装、引入、开始构建。

**说明**：产品文案追求极致简洁。三个短句形成节奏感，不添加多余的修饰词。"amazing things" 不译——中文产品文案中这类空泛修饰反而显得不专业。
