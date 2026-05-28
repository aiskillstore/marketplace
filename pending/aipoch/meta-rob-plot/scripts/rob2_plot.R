#!/usr/bin/env Rscript
# ROB2偏倚风险评估图绘制脚本
# 用法: Rscript rob2_plot.R <csv_path> [save_name] [output_dir]

suppressPackageStartupMessages({
  library(ggplot2)
  library(reshape2)
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("用法: Rscript rob2_plot.R <csv_path> [save_name] [output_dir]")
}

csv_path <- args[1]
save_name <- if (length(args) >= 2 && args[2] != "") args[2] else "rob2"
output_dir <- if (length(args) >= 3 && args[3] != "") args[3] else dirname(csv_path)

# 读取数据
if (!file.exists(csv_path)) {
  stop(paste0("文件不存在: ", csv_path))
}

rob2_data <- read.csv(csv_path, stringsAsFactors = FALSE)

# 将主要绘图流程封装在 main() 中，若 R 报错可在 error handler 中尝试 Python 回退
main <- function() {

# 检查必要列
required_cols <- c("study", "d1", "d2", "d3", "d4", "d5", "overall")
missing_cols <- setdiff(required_cols, colnames(rob2_data))
if (length(missing_cols) > 0) {
  stop(paste0("缺少必要列: ", paste(missing_cols, collapse = ", ")))
}

# 验证评估值
valid_values <- c("Low", "Some concerns", "High", "No information")
  for (col in c("d1", "d2", "d3", "d4", "d5", "overall")) {
    invalid <- setdiff(unique(rob2_data[[col]]), valid_values)
    if (length(invalid) > 0) {
      warning(paste0("列 ", col, " 包含无效值: ", paste(invalid, collapse = ", "),
                     "\n有效值为: Low, Some concerns, High, No information"))
    }
  }

# 创建输出目录
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 数据转换为长格式
traffic_m <- melt(rob2_data, id.vars = c('study'))
traffic_m$variable <- factor(traffic_m$variable,
                             levels = c('d1', 'd2', 'd3', 'd4', 'd5', 'overall'))
traffic_m$value <- factor(traffic_m$value,
                          levels = c("Low", "Some concerns", "High", "No information"))

# 绘制红绿灯图
p1 <- ggplot(traffic_m, aes(variable, study)) +
  geom_tile(color = "black", fill = 'white', size = 0.6) +
  geom_point(aes(fill = value), shape = 21, color = "black", size = 15) +
  geom_point(aes(shape = value, fill = value), color = "black", size = 15) +
  scale_shape_manual(
    values = c("Low" = 43, "Some concerns" = 45, "High" = 120, "No information" = 63),
    name = ''
  ) +
  scale_fill_manual(
    values = c(
      "Low" = "#4daf4a",
      "Some concerns" = "#ff7f00",
      "High" = "#e41a1c",
      "No information" = "#999999"
    ),
    name = ''
  ) +
  labs(title = "", x = "", y = "", fill = '', shape = '') +
  theme_minimal(base_size = 12) +
  theme(
    legend.position = 'right',
    panel.grid = element_blank(),
    axis.text.x = element_text(size = 14),
    axis.text.y = element_text(size = 14),
    legend.text = element_text(size = 14)
  )

# 计算风险比例用于条带图
traffic_m_bar <- traffic_m

for (i in unique(traffic_m_bar$variable)) {
  for (j in unique(traffic_m_bar$value)) {
    count_i <- nrow(traffic_m_bar[traffic_m_bar$variable == i, ])
    traffic_m_bar[(traffic_m_bar$variable == i) & (traffic_m_bar$value == j), 'risk'] <- 1 / count_i
  }
}

traffic_m_bar$variable <- factor(traffic_m_bar$variable, levels = rev(levels(traffic_m$variable)))
traffic_m_bar$value <- factor(traffic_m_bar$value, levels = rev(levels(traffic_m$value)))

# 绘制汇总条带图
p2 <- ggplot(data = traffic_m_bar, aes(x = variable, y = risk)) +
  geom_bar(aes(fill = value), stat = 'identity') +
  coord_flip() +
  scale_fill_manual(
    values = c(
      "Low" = "#4daf4a",
      "Some concerns" = "#ff7f00",
      "High" = "#e41a1c",
      "No information" = "#999999"
    ),
    name = ''
  ) +
  labs(title = "", x = "", y = "", fill = '', shape = '') +
  theme_bw(base_size = 12) +
  theme(
    legend.position = 'right',
    panel.grid = element_blank(),
    axis.text.x = element_text(size = 14),
    axis.text.y = element_text(size = 14),
    legend.text = element_text(size = 14)
  )

# 保存图片
light_file <- file.path(output_dir, paste0(save_name, '_rob2_light_plot.png'))
bar_file <- file.path(output_dir, paste0(save_name, '_rob2_bar_plot.png'))

# 根据研究数量调整图片高度
  n_studies <- nrow(rob2_data)
  height_light <- max(400, 100 + n_studies * 40)

png(light_file, width = 800, height = height_light, units = 'px', pointsize = 20)
print(p1)
dev.off()

png(bar_file, width = 800, height = 400, units = 'px', pointsize = 20)
print(p2)
dev.off()

# 统计各域风险分布
count_risk <- function(data, col) {
  c(
    Low = sum(data[[col]] == "Low", na.rm = TRUE),
    `Some concerns` = sum(data[[col]] == "Some concerns", na.rm = TRUE),
    High = sum(data[[col]] == "High", na.rm = TRUE),
    `No info` = sum(data[[col]] == "No information", na.rm = TRUE)
  )
}

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("ROB2偏倚风险评估图绘制完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【纳入研究】", n_studies, " 项\n\n"))
cat("【输出文件】\n")
cat(paste0("• 红绿灯图：", light_file, "\n"))
cat(paste0("• 汇总条带图：", bar_file, "\n\n"))

cat("【偏倚风险汇总】\n\n")
cat(sprintf("%-20s %-6s %-16s %-6s %-8s\n", "Domain", "Low", "Some concerns", "High", "No info"))
cat("─────────────────────────────────────────────────────────────\n")

domain_labels <- c(
  d1 = "D1 (随机化)",
  d2 = "D2 (干预偏离)",
  d3 = "D3 (数据缺失)",
  d4 = "D4 (结局测量)",
  d5 = "D5 (选择性报告)",
  overall = "Overall"
)

  for (col in c("d1", "d2", "d3", "d4", "d5", "overall")) {
    counts <- count_risk(rob2_data, col)
    cat(sprintf("%-20s %-6d %-16d %-6d %-8d\n",
                domain_labels[col], counts["Low"], counts["Some concerns"],
                counts["High"], counts["No info"]))
  }

# 总体评估统计
overall_counts <- count_risk(rob2_data, "overall")
n_low <- overall_counts["Low"]
n_some <- overall_counts["Some concerns"]
n_high <- overall_counts["High"]

pct_low <- round(n_low / n_studies * 100, 1)
pct_some <- round(n_some / n_studies * 100, 1)
pct_high <- round(n_high / n_studies * 100, 1)

cat("\n【总体评估】\n")
cat(paste0("• 低风险研究：", n_low, " 项 (", pct_low, "%)\n"))
cat(paste0("• 存在顾虑：", n_some, " 项 (", pct_some, "%)\n"))
cat(paste0("• 高风险研究：", n_high, " 项 (", pct_high, "%)\n"))
cat("═══════════════════════════════════════════\n")

} # end main

# 尝试运行 main()，如发生错误则尝试调用 Python 回退脚本
tryCatch({
  main()
}, error = function(e) {
  message("R 绘图过程遇到错误: ", e$message)
  message("尝试使用 Python 回退脚本生成图像...")
  py_script <- file.path("scripts", "rob2_plot.py")
  if (!file.exists(py_script)) {
    stop("找不到 Python 回退脚本: ", py_script)
  }
  # 尝试常见的 Python 可执行名
  py_execs <- c("python", "py")
  success <- FALSE
  for (py in py_execs) {
    status <- tryCatch(system2(py, args = c(py_script, csv_path, save_name, output_dir), wait = TRUE),
                       error = function(err) NA)
    if (!is.na(status) && status == 0) {
      message("已使用 ", py, " 成功执行 Python 回退脚本")
      success <- TRUE
      break
    }
  }
  if (!success) {
    stop("Python 回退也未能成功执行（请检查是否安装 Python 及 pandas/matplotlib）")
  }
})
