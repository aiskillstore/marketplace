#!/usr/bin/env Rscript
# 连续性数据森林图绘制脚本
# 用法: Rscript forest_continuous.R <csv_path> [outcome_name] [output_dir]

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
  library(grid)
  library(stringr)
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("用法: Rscript forest_continuous.R <csv_path> [outcome_name] [output_dir]")
}

csv_path <- args[1]
outcome_name <- if (length(args) >= 2 && args[2] != "") args[2] else NULL
output_dir <- if (length(args) >= 3 && args[3] != "") args[3] else dirname(csv_path)

# 读取数据
if (!file.exists(csv_path)) {
  stop(paste0("文件不存在: ", csv_path))
}

data_df <- read.csv(csv_path, stringsAsFactors = FALSE)

# 检查必要列
required_cols <- c("study", "group1_sample_size", "group1_Mean", "group1_SD",
                   "group2_sample_size", "group2_Mean", "group2_SD")
missing_cols <- setdiff(required_cols, colnames(data_df))
if (length(missing_cols) > 0) {
  stop(paste0("缺少必要列: ", paste(missing_cols, collapse = ", ")))
}

# 获取结局指标名称
if (is.null(outcome_name)) {
  if ("outcome_new" %in% colnames(data_df)) {
    outcome_name <- unique(data_df$outcome_new)[1]
  } else {
    outcome_name <- "Outcome"
  }
}

# 验证数据
if (nrow(data_df) < 2) {
  stop("至少需要2项研究才能进行Meta分析")
}

# 创建输出目录
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 数据准备
study <- data_df$study
n_experimental <- as.numeric(data_df$group1_sample_size)
mean_experimental <- as.numeric(data_df$group1_Mean)
sd_experimental <- as.numeric(data_df$group1_SD)
n_control <- as.numeric(data_df$group2_sample_size)
mean_control <- as.numeric(data_df$group2_Mean)
sd_control <- as.numeric(data_df$group2_SD)

# 创建meta分析对象
meta_analysis <- metacont(
  studlab = study,
  n.e = n_experimental,
  mean.e = mean_experimental,
  sd.e = sd_experimental,
  n.c = n_control,
  mean.c = mean_control,
  sd.c = sd_control,
  sm = "SMD",
  method.tau = "DL",
  method.random.ci = "HK"
)

# 获取合并P值
get_pooled_pval <- function(meta_analysis) {
  if (!is.null(meta_analysis$pval.random)) return(meta_analysis$pval.random)
  if (!is.null(meta_analysis$pval.common)) return(meta_analysis$pval.common)
  NA_real_
}

# 绘制森林图
forest_file <- file.path(output_dir, paste0("Continuity_forest_", outcome_name, ".png"))

test <- meta::forest(meta_analysis,
                     xlab = "",
                     col.diamond = "black",
                     col.diamond.lines = "black",
                     col.square = "red",
                     col.square.lines = "red",
                     col.label = "black",
                     common = FALSE,
                     text.random = 'Total(95% CI)',
                     lty.random = 0,
                     print.stat = TRUE,
                     colgap = grid::unit(6, "mm"),
                     layout = "RevMan5",
                     file = forest_file,
                     width = 800)

# 生成森林图数据表
forest_data <- as.data.frame(t(rbind(
  c(test$studlab, 'Model'),
  test$effect.format[c(4:length(test$effect.format), 2)],
  test$ci.format[c(4:length(test$effect.format), 2)],
  c(unlist(lapply(meta_analysis$w.random, function(x) {
    round(x / sum(meta_analysis$w.random) * 100, 1)
  })), 100)
)))

colnames(forest_data) <- c('Study', 'SMD', '95% CI', '%W(Random)')

pooled_pval <- get_pooled_pval(meta_analysis)
forest_data$`P value (pooled)` <- c(rep(NA, nrow(forest_data) - 1), pooled_pval)

# 添加原始数据列
forest_data <- cbind(forest_data, data.frame(
  'Mean.e' = c(mean_experimental, NA),
  'SD.e' = c(sd_experimental, NA),
  'Total.e' = c(n_experimental, sum(n_experimental)),
  'Mean.c' = c(mean_control, NA),
  'SD.c' = c(sd_control, NA),
  'Total.c' = c(n_control, sum(n_control))
))

forest_data <- forest_data[, c(1, 6, 7, 8, 9, 10, 11, 2, 3, 4, 5)]

# 保存数据表
csv_file <- file.path(output_dir, paste0("Continuity_forest_", outcome_name, ".csv"))
write.csv(forest_data, csv_file, row.names = FALSE)

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("连续性森林图绘制完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【结局指标】", outcome_name, "\n"))
cat(paste0("【纳入研究】", length(study), " 项\n\n"))
cat("【输出文件】\n")
cat(paste0("• 森林图：", forest_file, "\n"))
cat(paste0("• 数据表：", csv_file, "\n\n"))
cat("【合并效应量】\n")
cat(paste0("• SMD = ", round(meta_analysis$TE.random, 2),
           " [", round(meta_analysis$lower.random, 2),
           "; ", round(meta_analysis$upper.random, 2), "]\n"))
cat(paste0("• P值 = ", round(pooled_pval, 4), "\n\n"))
cat("【异质性】\n")
cat(paste0("• I² = ", round(meta_analysis$I2 * 100, 2), "%\n"))
cat(paste0("• Tau² = ", round(meta_analysis$tau2, 4), "\n"))
cat(paste0("• Q检验 P值 = ", round(meta_analysis$pval.Q, 4), "\n"))
cat("═══════════════════════════════════════════\n")
