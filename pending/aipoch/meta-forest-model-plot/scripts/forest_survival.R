#!/usr/bin/env Rscript
# 生存型数据森林图绘制脚本
# 用法: Rscript forest_survival.R <csv_path> [outcome_name] [output_dir]

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
  library(grid)
  library(stringr)
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("用法: Rscript forest_survival.R <csv_path> [outcome_name] [output_dir]")
}

csv_path <- args[1]
outcome_name <- if (length(args) >= 2 && args[2] != "") args[2] else NULL
output_dir <- if (length(args) >= 3 && args[3] != "") args[3] else dirname(csv_path)

# 读取数据
if (!file.exists(csv_path)) {
  stop(paste0("文件不存在: ", csv_path))
}

data_df <- read.csv(csv_path, stringsAsFactors = FALSE)

# 辅助函数：获取列（支持多种列名）
get_col <- function(df, candidates) {
  for (col in candidates) {
    if (col %in% colnames(df)) return(df[[col]])
  }
  return(NULL)
}

# 检查必要列
if (!"study" %in% colnames(data_df)) {
  stop("缺少必要列: study")
}

hr_col <- get_col(data_df, c("group1_HR"))
lower_col <- get_col(data_df, c("group1_95%Lower CI", "group1_95.Lower.CI"))
upper_col <- get_col(data_df, c("group1_95%Upper CI", "group1_95.Upper.CI"))

if (is.null(hr_col)) stop("缺少必要列: group1_HR")
if (is.null(lower_col)) stop("缺少必要列: group1_95%Lower CI 或 group1_95.Lower.CI")
if (is.null(upper_col)) stop("缺少必要列: group1_95%Upper CI 或 group1_95.Upper.CI")

# 获取结局指标名称
if (is.null(outcome_name)) {
  if ("outcome_new" %in% colnames(data_df)) {
    outcome_name <- unique(data_df$outcome_new)[1]
  } else {
    outcome_name <- "Survival"
  }
}

# 创建输出目录
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 数据准备
study <- data_df$study
hr <- as.numeric(hr_col)
lower_ci <- as.numeric(lower_col)
upper_ci <- as.numeric(upper_col)

# 验证数据有效性
valid_idx <- !is.na(hr) & !is.na(lower_ci) & !is.na(upper_ci) &
  hr > 0 & lower_ci > 0 & upper_ci > 0

if (sum(valid_idx) < 2) {
  stop(paste0(outcome_name, " 结局变量有效数据不足，无法合并！"))
}

# 过滤有效数据
study <- study[valid_idx]
hr <- hr[valid_idx]
lower_ci <- lower_ci[valid_idx]
upper_ci <- upper_ci[valid_idx]

# 对数转换
log_hazard_ratio <- log(hr)

# 计算SE值
se <- (log(upper_ci) - log(lower_ci)) / (2 * 1.96)

# 创建meta分析对象
meta_analysis <- metagen(
  TE = log_hazard_ratio,
  seTE = se,
  studlab = study,
  sm = "HR",
  method.tau = "DL",
  common = TRUE
)

# 获取合并P值
get_pooled_pval <- function(meta_analysis) {
  if (!is.null(meta_analysis$pval.random)) return(meta_analysis$pval.random)
  if (!is.null(meta_analysis$pval.common)) return(meta_analysis$pval.common)
  NA_real_
}

# 绘制森林图
forest_file <- file.path(output_dir, paste0("Survival_forest_", outcome_name, ".png"))

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
                     width = 700)

# 生成森林图数据表
forest_data <- as.data.frame(t(rbind(
  c(test$studlab, 'Model'),
  test$effect.format[c(4:length(test$effect.format), 2)],
  test$ci.format[c(4:length(test$effect.format), 2)],
  c(unlist(lapply(meta_analysis$w.common, function(x) {
    round(x / sum(meta_analysis$w.common) * 100, 1)
  })), 100)
)))

colnames(forest_data) <- c('Study', 'HR', '95% CI', '%W(Random)')

pooled_pval <- get_pooled_pval(meta_analysis)
forest_data$`P value (pooled)` <- c(rep(NA, nrow(forest_data) - 1), pooled_pval)

# 添加log数据列
forest_data <- cbind(forest_data, data.frame(
  'logHR' = c(log_hazard_ratio, NA),
  'SE' = c(se, NA)
))
forest_data <- forest_data[, c(1, 6, 7, 2, 3, 4, 5)]

# 保存数据表
csv_file <- file.path(output_dir, paste0("Survival_forest_", outcome_name, ".csv"))
write.csv(forest_data, csv_file, row.names = FALSE)

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("生存型森林图绘制完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【结局指标】", outcome_name, "\n"))
cat(paste0("【纳入研究】", length(study), " 项\n\n"))
cat("【输出文件】\n")
cat(paste0("• 森林图：", forest_file, "\n"))
cat(paste0("• 数据表：", csv_file, "\n\n"))
cat("【合并效应量】\n")
cat(paste0("• HR = ", round(exp(meta_analysis$TE.random), 2),
           " [", round(exp(meta_analysis$lower.random), 2),
           "; ", round(exp(meta_analysis$upper.random), 2), "]\n"))
cat(paste0("• P值 = ", round(pooled_pval, 4), "\n\n"))
cat("【异质性】\n")
cat(paste0("• I² = ", round(meta_analysis$I2 * 100, 2), "%\n"))
cat(paste0("• Tau² = ", round(meta_analysis$tau2, 4), "\n"))
cat(paste0("• Q检验 P值 = ", round(meta_analysis$pval.Q, 4), "\n"))
cat("═══════════════════════════════════════════\n")
