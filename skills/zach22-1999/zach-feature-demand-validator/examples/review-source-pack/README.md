# 示例：review_source_pack

这是一个最小化的 Review fallback 示例包，用于演示：

- `source_manifest.json`
- `raw/reviews.csv`
- `raw/reviews.txt`

运行示例：

```bash
python3 skills/zach-feature-demand-validator/scripts/parse_review_source_pack.py \
  --pack skills/zach-feature-demand-validator/examples/review-source-pack \
  --keywords "steam,steamer,steaming" \
  --output /tmp/01_review_信号_原始数据.csv
```

Windows:

```powershell
py -3 skills/zach-feature-demand-validator/scripts/parse_review_source_pack.py `
  --pack skills\zach-feature-demand-validator\examples\review-source-pack `
  --keywords "steam,steamer,steaming" `
  --output C:\Temp\01_review_信号_原始数据.csv
```
