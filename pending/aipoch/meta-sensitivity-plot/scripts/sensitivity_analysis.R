#!/usr/bin/env Rscript
# 敏感性分析脚本（逐一剔除法）- 含图片输出
# 用法: Rscript sensitivity_analysis.R <csv_path> <type> [outcome_name] [output_dir]

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
  library(stringr)
  library(grid)
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("用法: Rscript sensitivity_analysis.R <csv_path> <type> [outcome_name] [output_dir]")
}

csv_path <- args[1]
type <- args[2]
outcome_name <- if (length(args) >= 3 && args[3] != "") args[3] else NULL
output_dir <- if (length(args) >= 4 && args[4] != "") args[4] else dirname(csv_path)

# 验证类型
if (!type %in% c("Binary", "Continuity", "Survival")) {
  stop("type 必须是 Binary, Continuity 或 Survival")
}

# 读取数据
if (!file.exists(csv_path)) {
  stop(paste0("文件不存在: ", csv_path))
}

data_df <- read.csv(csv_path, stringsAsFactors = FALSE)

# 获取结局指标名称
if (is.null(outcome_name)) {
  if ("outcome_new" %in% colnames(data_df)) {
    outcome_name <- unique(data_df$outcome_new)[1]
  } else {
    outcome_name <- "Outcome"
  }
}

# 验证数据量
if (nrow(data_df) < 3) {
  stop("至少需要3项研究才能进行敏感性分析")
}

# 创建输出目录
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 辅助函数：获取列
get_col <- function(df, candidates) {
  for (col in candidates) {
    if (col %in% colnames(df)) return(df[[col]])
  }
  return(NULL)
}

# 根据类型创建meta分析对象
if (type == "Binary") {
  required_cols <- c("study", "group1_Events", "group1_sample_size",
                     "group2_Events", "group2_sample_size")
  missing_cols <- setdiff(required_cols, colnames(data_df))
  if (length(missing_cols) > 0) {
    stop(paste0("缺少必要列: ", paste(missing_cols, collapse = ", ")))
  }

  meta_analysis <- metabin(
    event.e = as.numeric(data_df$group1_Events),
    n.e = as.numeric(data_df$group1_sample_size),
    event.c = as.numeric(data_df$group2_Events),
    n.c = as.numeric(data_df$group2_sample_size),
    studlab = data_df$study,
    sm = "OR",
    method = "MH",
    random = TRUE
  )
  effect_name <- "OR"
  effect_label <- "Odds Ratio"

} else if (type == "Continuity") {
  required_cols <- c("study", "group1_sample_size", "group1_Mean", "group1_SD",
                     "group2_sample_size", "group2_Mean", "group2_SD")
  missing_cols <- setdiff(required_cols, colnames(data_df))
  if (length(missing_cols) > 0) {
    stop(paste0("缺少必要列: ", paste(missing_cols, collapse = ", ")))
  }

  meta_analysis <- metacont(
    studlab = data_df$study,
    n.e = as.numeric(data_df$group1_sample_size),
    mean.e = as.numeric(data_df$group1_Mean),
    sd.e = as.numeric(data_df$group1_SD),
    n.c = as.numeric(data_df$group2_sample_size),
    mean.c = as.numeric(data_df$group2_Mean),
    sd.c = as.numeric(data_df$group2_SD),
    sm = "SMD",
    method.tau = "DL",
    method.random.ci = "HK"
  )
  effect_name <- "SMD"
  effect_label <- "Standardized Mean Difference"

} else if (type == "Survival") {
  hr_col <- get_col(data_df, c("group1_HR"))
  lower_col <- get_col(data_df, c("group1_95%Lower CI", "group1_95.Lower.CI"))
  upper_col <- get_col(data_df, c("group1_95%Upper CI", "group1_95.Upper.CI"))

  if (is.null(hr_col) || is.null(lower_col) || is.null(upper_col)) {
    stop("缺少必要列: group1_HR, group1_95%Lower CI, group1_95%Upper CI")
  }

  hr <- as.numeric(hr_col)
  lower_ci <- as.numeric(lower_col)
  upper_ci <- as.numeric(upper_col)

  valid_idx <- !is.na(hr) & !is.na(lower_ci) & !is.na(upper_ci) &
    hr > 0 & lower_ci > 0 & upper_ci > 0

  if (sum(valid_idx) < 3) {
    stop("有效数据不足3项，无法进行敏感性分析")
  }

  log_hr <- log(hr[valid_idx])
  se <- (log(upper_ci[valid_idx]) - log(lower_ci[valid_idx])) / (2 * 1.96)

  meta_analysis <- metagen(
    TE = log_hr,
    seTE = se,
    studlab = data_df$study[valid_idx],
    sm = "HR",
    method.tau = "DL",
    common = TRUE
  )
  effect_name <- "HR"
  effect_label <- "Hazard Ratio"
}

# 敏感性分析 - 逐一排除法
Leave_one_fun <- tryCatch({
  metainf(meta_analysis, pooled = "random")
}, error = function(e) {
  stop(paste0("敏感性分析失败: ", e$message))
})

# ========== 绘制敏感性分析森林图 ==========
plot_file <- file.path(output_dir, paste0(type, "_sensitive_forest_", outcome_name, ".png"))

# 计算图片高度（根据研究数量动态调整）
n_studies <- length(Leave_one_fun$studlab)
plot_height <- max(600, 150 + n_studies * 35)

png(plot_file, width = 900, height = plot_height, units = 'px', pointsize = 14)
tryCatch({
  forest(Leave_one_fun)
}, error = function(e) {
  # 如果forest失败，使用简单的散点图替代
  n <- length(Leave_one_fun$studlab)
  te <- if(effect_name %in% c("OR", "HR")) exp(Leave_one_fun$TE) else Leave_one_fun$TE
  ci_lower <- if(effect_name %in% c("OR", "HR")) exp(Leave_one_fun$lower) else Leave_one_fun$lower
  ci_upper <- if(effect_name %in% c("OR", "HR")) exp(Leave_one_fun$upper) else Leave_one_fun$upper

  par(mar = c(5, 10, 4, 2))
  plot(te, 1:n, xlim = range(c(ci_lower, ci_upper), na.rm = TRUE),
       ylim = c(0.5, n + 0.5), pch = 15, col = "darkblue",
       xlab = effect_label, ylab = "", yaxt = "n",
       main = paste0("Leave-one-out ", effect_label))
  axis(2, at = 1:n, labels = Leave_one_fun$studlab, las = 1)
  segments(ci_lower, 1:n, ci_upper, 1:n, col = "darkblue")
  abline(v = if(effect_name %in% c("OR", "HR")) 1 else 0, lty = 2, col = "gray")
})
dev.off()

# ========== 绘制漏斗图（Funnel plot） ==========
funnel_file <- file.path(output_dir, paste0(type, "_funnel_", outcome_name, ".png"))

png(funnel_file, width = 700, height = 700, units = 'px', pointsize = 14)
tryCatch({
  # 使用原始meta_analysis对象绘制漏斗图
  if (exists("meta_analysis") && !is.null(meta_analysis)) {
    # 对于二分类和生存数据，使用meta对象直接绘图
    funnel(meta_analysis, studlab = TRUE, xlab = effect_label, contour = c(0.90, 0.95), col.contour = c("gray80","gray60"), legend = TRUE)
  } else {
    # 作为降级选项，绘制基于效应量和标准误的散点图
    te <- Leave_one_fun$TE
    se <- Leave_one_fun$se
    plot(te, se, pch = 16, xlab = effect_label, ylab = "Standard Error", main = paste0("Funnel plot - ", outcome_name))
  }
}, error = function(e) {
  # 若funnel绘制失败，输出简单提示图
  plot.new()
  text(0.5, 0.5, paste0("Funnel plot failed:\n", e$message), cex = 0.9)
})
dev.off()

# ========== 提取结果数据 ==========
# 提取效应量用于显示
if (effect_name %in% c("OR", "HR")) {
  te_display <- exp(Leave_one_fun$TE)
  lower_display <- exp(Leave_one_fun$lower)
  upper_display <- exp(Leave_one_fun$upper)
  pooled_display <- exp(meta_analysis$TE.random)
  pooled_lower <- exp(meta_analysis$lower.random)
  pooled_upper <- exp(meta_analysis$upper.random)
} else {
  te_display <- Leave_one_fun$TE
  lower_display <- Leave_one_fun$lower
  upper_display <- Leave_one_fun$upper
  pooled_display <- meta_analysis$TE.random
  pooled_lower <- meta_analysis$lower.random
  pooled_upper <- meta_analysis$upper.random
}

# 格式化数值
format_val <- function(x, digits = 2) {
  ifelse(is.na(x) | is.nan(x) | is.null(x), "NA", format(round(x, digits), nsmall = digits))
}

sensitivity_data <- data.frame(
  study = Leave_one_fun$studlab,
  value = format_val(te_display, 2),
  lower_95 = format_val(lower_display, 2),
  upper_95 = format_val(upper_display, 2),
  statistic = Leave_one_fun$statistic,
  p_val = Leave_one_fun$pval,
  tau2 = Leave_one_fun$tau2,
  I2 = Leave_one_fun$I2,
  stringsAsFactors = FALSE
)

# 保存结果
csv_file <- file.path(output_dir, paste0(type, "_sensitive_", outcome_name, ".csv"))
write.csv(sensitivity_data, csv_file, row.names = FALSE)

# 判断稳健性
effect_values <- as.numeric(sensitivity_data$value)
pooled_effect_val <- effect_values[length(effect_values)]

# 检查所有剔除后的效应量方向是否一致
if (effect_name %in% c("OR", "HR")) {
  all_greater <- all(effect_values > 1, na.rm = TRUE)
  all_smaller <- all(effect_values < 1, na.rm = TRUE)
  all_same_direction <- all_greater | all_smaller
} else {
  all_greater <- all(effect_values > 0, na.rm = TRUE)
  all_smaller <- all(effect_values < 0, na.rm = TRUE)
  all_same_direction <- all_greater | all_smaller
}

robustness <- if (all_same_direction) "稳健" else "不稳健（剔除部分研究后效应量方向改变）"

# 计算效应量变化范围
effect_range <- range(effect_values, na.rm = TRUE)
effect_variation <- round((effect_range[2] - effect_range[1]) / abs(pooled_effect_val) * 100, 1)

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("敏感性分析完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【结局指标】", outcome_name, "\n"))
cat(paste0("【数据类型】", type, "\n"))
cat(paste0("【纳入研究】", nrow(data_df), " 项\n\n"))

cat("【输出文件】\n")
cat(paste0("• 敏感性分析森林图：", plot_file, "\n"))
cat(paste0("• 敏感性分析数据表：", csv_file, "\n\n"))

cat("【合并效应量（全部研究）】\n")
cat(paste0("• ", effect_name, " = ", round(pooled_display, 2),
           " [", round(pooled_lower, 2), "; ", round(pooled_upper, 2), "]\n\n"))

cat("【敏感性分析结果摘要】\n")
cat(sprintf("%-20s %-10s %-18s %-8s\n", "剔除研究", effect_name, "95% CI", "I²"))
cat("───────────────────────────────────────────\n")

for (i in 1:nrow(sensitivity_data)) {
  study_name <- if (nchar(sensitivity_data$study[i]) > 18) {
    paste0(substr(sensitivity_data$study[i], 1, 15), "...")
  } else {
    sensitivity_data$study[i]
  }
  ci_str <- paste0("[", sensitivity_data$lower_95[i], "; ", sensitivity_data$upper_95[i], "]")
  i2_val <- sensitivity_data$I2[i]
  if (is.na(i2_val) || is.nan(i2_val) || is.null(i2_val)) {
    i2_str <- "NA"
  } else {
    i2_str <- paste0(round(as.numeric(i2_val) * 100, 1), "%")
  }
  cat(sprintf("%-20s %-10s %-18s %-8s\n",
              study_name, sensitivity_data$value[i], ci_str, i2_str))
}

cat("\n【效应量变化分析】\n")
cat(paste0("• 效应量范围：", round(effect_range[1], 2), " ~ ", round(effect_range[2], 2), "\n"))
cat(paste0("• 相对变化幅度：", effect_variation, "%\n\n"))

cat("【结论】\n")
cat(paste0("• 效应量稳健性：", robustness, "\n"))

if (effect_variation < 10) {
  cat("• 剔除任意单项研究后效应量变化小（<10%），结果稳健。\n")
} else if (effect_variation < 20) {
  cat("• 剔除部分研究后效应量有一定变化（10-20%），需关注影响较大的研究。\n")
} else {
  cat("• 效应量变化较大（>20%），部分研究对结果影响显著，建议进一步分析。\n")
}

cat("═══════════════════════════════════════════\n")
