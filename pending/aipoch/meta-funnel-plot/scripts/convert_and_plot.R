#!/usr/bin/env Rscript
# 转换数据格式并绘制漏斗图

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
})

# 读取原始数据
data <- read.csv("漏斗图_测试文件_1.txt", sep = "\t", stringsAsFactors = FALSE)

# 重命名列以符合R脚本要求
colnames(data) <- c("study", "group1_Events", "group1_sample_size", 
                     "group2_Events", "group2_sample_size", "country")

# 保存为CSV格式
write.csv(data, "funnel_plot_input.csv", row.names = FALSE)

cat("数据已转换并保存为 funnel_plot_input.csv\n")
cat("数据摘要：\n")
print(head(data))
