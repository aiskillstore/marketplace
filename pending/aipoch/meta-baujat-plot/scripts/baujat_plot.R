#!/usr/bin/env Rscript
# Baujat图绘制脚本（异质性分析）
# 用法: Rscript baujat_plot.R <csv_path> <type> [outcome_name] [output_dir]

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
  stop("用法: Rscript baujat_plot.R <csv_path> <type> [outcome_name] [output_dir]")
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
  effect_name <- "OR"

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
  effect_name <- "HR"
}

# 计算Baujat数据
baujat_data <- tryCatch({
  # 使用meta包的baujat函数获取数据
  bj <- baujat(meta_analysis, plot = FALSE)
  data.frame(
    study = meta_analysis$studlab,
    x = bj$x,  # 对结果的贡献
    y = bj$y   # 对异质性Q的贡献
  )
}, error = function(e) {
  # 手动计算Baujat数据
  n_studies <- length(meta_analysis$studlab)
  x_vals <- numeric(n_studies)
  y_vals <- numeric(n_studies)

  for (i in 1:n_studies) {
    # 计算剔除第i项研究后的合并效应量
    idx <- setdiff(1:n_studies, i)

    if (type == "Binary") {
      meta_loo <- metabin(
        event.e = meta_analysis$event.e[idx],
        n.e = meta_analysis$n.e[idx],
        event.c = meta_analysis$event.c[idx],
        n.c = meta_analysis$n.c[idx],
        studlab = meta_analysis$studlab[idx],
        sm = "OR", method = "MH", random = TRUE
      )
    } else if (type == "Continuity") {
      meta_loo <- metacont(
        n.e = meta_analysis$n.e[idx],
        mean.e = meta_analysis$mean.e[idx],
        sd.e = meta_analysis$sd.e[idx],
        n.c = meta_analysis$n.c[idx],
        mean.c = meta_analysis$mean.c[idx],
        sd.c = meta_analysis$sd.c[idx],
        studlab = meta_analysis$studlab[idx],
        sm = "SMD", method.tau = "DL"
      )
    } else {
      meta_loo <- metagen(
        TE = meta_analysis$TE[idx],
        seTE = meta_analysis$seTE[idx],
        studlab = meta_analysis$studlab[idx],
        sm = "HR", method.tau = "DL"
      )
    }

    # 对结果的贡献：效应量变化的平方
    x_vals[i] <- (meta_analysis$TE.random - meta_loo$TE.random)^2

    # 对Q的贡献
    y_vals[i] <- meta_analysis$Q - meta_loo$Q
  }

  data.frame(
    study = meta_analysis$studlab,
    x = x_vals,
    y = y_vals
  )
})

# 标记离群研究（Q贡献超过平均值2倍）
mean_y <- mean(baujat_data$y)
baujat_data$outlier <- baujat_data$y > mean_y * 2

# 绘制Baujat图
p <- ggplot(baujat_data, aes(x = x, y = y)) +
  geom_point(aes(color = outlier), size = 4) +
  scale_color_manual(values = c("FALSE" = "#2166ac", "TRUE" = "#b2182b"),
                     labels = c("正常", "潜在离群"),
                     name = "") +
  geom_hline(yintercept = mean_y, linetype = "dashed", color = "gray50") +
  geom_vline(xintercept = mean(baujat_data$x), linetype = "dashed", color = "gray50") +
  labs(
    title = paste0("Baujat Plot - ", outcome_name),
    x = "Contribution to overall result",
    y = "Contribution to overall heterogeneity (Q)"
  ) +
  theme_bw(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    legend.position = "bottom"
  )

# 添加标签
if (has_ggrepel) {
  p <- p + geom_text_repel(aes(label = study), size = 3, max.overlaps = 15)
} else {
  p <- p + geom_text(aes(label = study), size = 3, vjust = -0.5, hjust = 0.5)
}

# 保存图片
plot_file <- file.path(output_dir, paste0(type, "_baujat_", outcome_name, ".png"))
ggsave(plot_file, p, width = 10, height = 8, dpi = 150)

# 保存数据
baujat_data$rank <- rank(-baujat_data$y)
baujat_data <- baujat_data[order(baujat_data$rank), ]
csv_file <- file.path(output_dir, paste0(type, "_baujat_", outcome_name, ".csv"))
write.csv(baujat_data, csv_file, row.names = FALSE)

# 输出结果摘要
n_studies <- length(meta_analysis$studlab)
n_outliers <- sum(baujat_data$outlier)

cat("\n")
cat("═══════════════════════════════════════════\n")
cat("Baujat图绘制完成\n")
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

cat("【输出文件】\n")
cat(paste0("• Baujat图：", plot_file, "\n"))
cat(paste0("• 贡献度数据：", csv_file, "\n\n"))

cat("【异质性贡献排名】（按对Q的贡献降序）\n")
cat(sprintf("%-5s %-20s %-12s %-10s %-8s\n", "排名", "研究", "结果贡献", "Q贡献", "判断"))
cat("─────────────────────────────────────────────────────\n")

for (i in 1:min(10, nrow(baujat_data))) {
  study_name <- if (nchar(baujat_data$study[i]) > 18) {
    paste0(substr(baujat_data$study[i], 1, 15), "...")
  } else {
    baujat_data$study[i]
  }
  status <- if (baujat_data$outlier[i]) "⚠️ 离群" else "正常"
  cat(sprintf("%-5d %-20s %-12.4f %-10.4f %-8s\n",
              i, study_name, baujat_data$x[i], baujat_data$y[i], status))
}

if (nrow(baujat_data) > 10) {
  cat("...\n")
}

cat("\n【建议】\n")
if (n_outliers == 0) {
  cat("• 未发现明显的离群研究，各研究对异质性的贡献较为均衡。\n")
} else if (n_outliers == 1) {
  outlier_study <- baujat_data$study[baujat_data$outlier][1]
  cat(paste0("• 发现1项潜在离群研究：", outlier_study, "\n"))
  cat("• 建议进行敏感性分析，评估剔除该研究后结果是否稳健。\n")
} else {
  cat(paste0("• 发现", n_outliers, "项潜在离群研究，可能是异质性的主要来源。\n"))
  cat("• 建议检查这些研究的特征，考虑进行亚组分析或敏感性分析。\n")
}

if (meta_analysis$I2 > 0.5) {
  cat("• 异质性较高（I² > 50%），建议探索异质性来源。\n")
}

cat("═══════════════════════════════════════════\n")
