#!/usr/bin/env Rscript
# 星状图（Radial Plot / Galbraith Plot）绘制脚本
# 用法: Rscript radial_plot.R <csv_path> <type> [outcome_name] [output_dir]

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
  library(ggplot2)
  if (requireNamespace("ggrepel", quietly = TRUE)) {
    library(ggrepel)
    has_ggrepel <- TRUE
  } else {
    has_ggrepel <- FALSE
  }
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("用法: Rscript radial_plot.R <csv_path> <type> [outcome_name] [output_dir]")
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
  stop("至少需要3项研究才能进行有效的异质性分析")
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
  effect_name <- "log(OR)"
  display_effect_name <- "OR"

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
  display_effect_name <- "SMD"

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
    stop("有效数据不足3项，无法进行异质性分析")
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
  effect_name <- "log(HR)"
  display_effect_name <- "HR"
}

# 计算星状图数据
n_studies <- length(meta_analysis$studlab)
precision <- 1 / meta_analysis$seTE  # 精度 = 1/SE
z_value <- meta_analysis$TE / meta_analysis$seTE  # 标准化效应量

# 合并效应量（作为回归线斜率）
pooled_effect <- meta_analysis$TE.random

# 计算95%置信带边界
# 在星状图中，置信带是 pooled_effect ± 1.96（因为是标准化的z值）
z_upper <- pooled_effect * precision + 1.96
z_lower <- pooled_effect * precision - 1.96

# 判断是否在置信带内
radial_data <- data.frame(
  study = meta_analysis$studlab,
  precision = precision,
  z_value = z_value,
  effect = meta_analysis$TE,
  se = meta_analysis$seTE
)

radial_data$expected_z <- pooled_effect * radial_data$precision
radial_data$in_ci <- abs(radial_data$z_value - radial_data$expected_z) <= 1.96
radial_data$deviation <- ifelse(radial_data$z_value > radial_data$expected_z, "偏高", "偏低")

# 绘制星状图
max_precision <- max(precision) * 1.1
x_range <- c(0, max_precision)

# 创建置信带的多边形数据
ci_data <- data.frame(
  x = c(0, max_precision, max_precision, 0),
  y = c(1.96, pooled_effect * max_precision + 1.96,
        pooled_effect * max_precision - 1.96, -1.96)
)

p <- ggplot() +
  # 95%置信带
  geom_polygon(data = ci_data, aes(x = x, y = y),
               fill = "lightblue", alpha = 0.3) +
  # 回归线（通过原点，斜率为合并效应量）
  geom_abline(intercept = 0, slope = pooled_effect,
              color = "darkblue", size = 1) +
  # 置信带边界
  geom_abline(intercept = 1.96, slope = pooled_effect,
              color = "darkblue", linetype = "dashed", size = 0.5) +
  geom_abline(intercept = -1.96, slope = pooled_effect,
              color = "darkblue", linetype = "dashed", size = 0.5) +
  # 水平参考线 y=0
  geom_hline(yintercept = 0, color = "gray50", linetype = "dotted") +
  # 散点
  geom_point(data = radial_data, aes(x = precision, y = z_value, color = in_ci),
             size = 4) +
  scale_color_manual(values = c("TRUE" = "#2166ac", "FALSE" = "#b2182b"),
                     labels = c("置信带外", "置信带内"),
                     name = "") +
  labs(
    title = paste0("Radial Plot (Galbraith Plot) - ", outcome_name),
    x = "Precision (1/SE)",
    y = "Standardized effect (z = Effect/SE)"
  ) +
  xlim(x_range) +
  theme_bw(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    legend.position = "bottom"
  )

# 添加标签
if (has_ggrepel) {
  p <- p + geom_text_repel(data = radial_data, aes(x = precision, y = z_value, label = study),
                           size = 3, max.overlaps = 15)
} else {
  p <- p + geom_text(data = radial_data, aes(x = precision, y = z_value, label = study),
                     size = 3, vjust = -0.5, hjust = 0.5)
}

# 保存图片
plot_file <- file.path(output_dir, paste0(type, "_radial_", outcome_name, ".png"))
ggsave(plot_file, p, width = 10, height = 8, dpi = 150)

# 保存数据
csv_file <- file.path(output_dir, paste0(type, "_radial_", outcome_name, ".csv"))
write.csv(radial_data, csv_file, row.names = FALSE)

# 统计
n_in <- sum(radial_data$in_ci)
n_out <- sum(!radial_data$in_ci)
pct_in <- round(n_in / n_studies * 100, 1)
pct_out <- round(n_out / n_studies * 100, 1)

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("星状图（Radial Plot）绘制完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【结局指标】", outcome_name, "\n"))
cat(paste0("【数据类型】", type, "\n"))
cat(paste0("【纳入研究】", n_studies, " 项\n\n"))

cat("【异质性统计】\n")
cat(paste0("• I² = ", round(meta_analysis$I2 * 100, 2), "%\n"))
cat(paste0("• Tau² = ", round(meta_analysis$tau2, 4), "\n"))
cat(paste0("• Q = ", round(meta_analysis$Q, 2),
           ", df = ", meta_analysis$df.Q,
           ", P = ", round(meta_analysis$pval.Q, 4), "\n\n"))

cat("【合并效应量】\n")
if (display_effect_name %in% c("OR", "HR")) {
  cat(paste0("• ", display_effect_name, " = ", round(exp(meta_analysis$TE.random), 2),
             " [", round(exp(meta_analysis$lower.random), 2),
             "; ", round(exp(meta_analysis$upper.random), 2), "]\n\n"))
} else {
  cat(paste0("• ", display_effect_name, " = ", round(meta_analysis$TE.random, 2),
             " [", round(meta_analysis$lower.random, 2),
             "; ", round(meta_analysis$upper.random, 2), "]\n\n"))
}

cat("【输出文件】\n")
cat(paste0("• 星状图：", plot_file, "\n"))
cat(paste0("• 数据表：", csv_file, "\n\n"))

cat("【异质性分析】\n")
cat(paste0("• 落在95%置信带内的研究：", n_in, " 项 (", pct_in, "%)\n"))
cat(paste0("• 落在95%置信带外的研究：", n_out, " 项 (", pct_out, "%)\n\n"))

if (n_out > 0) {
  cat("【置信带外研究列表】\n")
  cat(sprintf("%-20s %-12s %-12s %-10s\n", "研究", "精度", "z值", "偏离方向"))
  cat("─────────────────────────────────────────────────────\n")

  outliers <- radial_data[!radial_data$in_ci, ]
  outliers <- outliers[order(-abs(outliers$z_value - outliers$expected_z)), ]

  for (i in 1:nrow(outliers)) {
    study_name <- if (nchar(outliers$study[i]) > 18) {
      paste0(substr(outliers$study[i], 1, 15), "...")
    } else {
      outliers$study[i]
    }
    cat(sprintf("%-20s %-12.2f %-12.2f %-10s\n",
                study_name, outliers$precision[i], outliers$z_value[i], outliers$deviation[i]))
  }
  cat("\n")
}

cat("【结论】\n")
if (pct_out <= 5) {
  cat("• 几乎所有研究都落在95%置信带内，异质性较低，研究结果一致性好。\n")
} else if (pct_out <= 20) {
  cat("• 大部分研究落在95%置信带内，存在轻度异质性。\n")
  cat("• 置信带外的研究可能需要进一步分析。\n")
} else if (pct_out <= 40) {
  cat("• 有相当比例的研究落在95%置信带外，存在中度异质性。\n")
  cat("• 建议进行亚组分析或敏感性分析以探索异质性来源。\n")
} else {
  cat("• 大量研究落在95%置信带外，存在显著异质性。\n")
  cat("• 建议谨慎解释合并结果，并深入分析异质性来源。\n")
}

if (meta_analysis$I2 > 0.75) {
  cat("• I² > 75%，表明存在高度异质性，需要特别关注。\n")
} else if (meta_analysis$I2 > 0.5) {
  cat("• I² 在50%-75%之间，表明存在中等异质性。\n")
}

cat("═══════════════════════════════════════════\n")
