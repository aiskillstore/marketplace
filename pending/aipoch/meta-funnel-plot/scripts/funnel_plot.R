#!/usr/bin/env Rscript
# 漏斗图绘制与发表偏倚检验脚本
# 用法: Rscript funnel_plot.R <csv_path> <type> [outcome_name] [output_dir]

suppressPackageStartupMessages({
  library(meta)
  library(metafor)
  library(stringr)
})

# 解析命令行参数
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("用法: Rscript funnel_plot.R <csv_path> <type> [outcome_name] [output_dir]")
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
if (nrow(data_df) < 2) {
  stop("至少需要2项研究才能绘制漏斗图")
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

  if (sum(valid_idx) < 2) {
    stop("有效数据不足2项，无法绘制漏斗图")
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

# 绘制漏斗图
funnel_file <- file.path(output_dir, paste0(type, "_funnel_", outcome_name, ".png"))

png(funnel_file, width = 800, height = 800, units = 'px', pointsize = 20)
test <- funnel(meta_analysis, lty.random = 0)
dev.off()

# 保存漏斗图数据
funnel_data <- as.data.frame(t(rbind(test$xvals, test$yvals)))
colnames(funnel_data) <- c('x', 'y')
funnel_csv <- file.path(output_dir, paste0(type, "_funnel_", outcome_name, ".csv"))
write.csv(funnel_data, funnel_csv, row.names = FALSE)

# 发表偏倚检验（需要至少3项研究）
n_studies <- length(meta_analysis$studlab)
Egger_result <- NULL
Begg_result <- NULL
Effect_size_tf <- NULL

if (n_studies >= 3) {
  # Egger线性回归检验
  Egger_res <- tryCatch({
    metabias(meta_analysis, k.min = 2, method.bias = "Egger")
  }, error = function(e) NULL)

  if (!is.null(Egger_res)) {
    Egger_result <- data.frame(
      beta = Egger_res$estimate[1],
      se.beta = Egger_res$estimate[2],
      intercept = Egger_res$intercept,
      se.intercept = Egger_res$se.intercept,
      statistic = Egger_res$statistic,
      p_val = Egger_res$pval,
      df = Egger_res$df
    )
    egger_csv <- file.path(output_dir, paste0(type, "_Egger_", outcome_name, ".csv"))
    write.csv(Egger_result, egger_csv, row.names = FALSE)
  }

  # Begg秩相关检验
  Begg_res <- tryCatch({
    metabias(meta_analysis, k.min = 2, method.bias = "Begg")
  }, error = function(e) NULL)

  if (!is.null(Begg_res)) {
    Begg_result <- data.frame(
      ks = Begg_res$estimate[1],
      se.ks = Begg_res$estimate[2],
      statistic = Begg_res$statistic,
      p.val = Begg_res$pval
    )
    begg_csv <- file.path(output_dir, paste0(type, "_Begg_", outcome_name, ".csv"))
    write.csv(Begg_result, begg_csv, row.names = FALSE)
  }

  # 剪补法（Trim and Fill）
  tf1 <- tryCatch({
    meta::trimfill(meta_analysis, ma.common = FALSE, common = FALSE, random = TRUE)
  }, error = function(e) NULL)

  if (!is.null(tf1)) {
    n_filled <- sum(tf1$trimfill)
    if (n_filled > 0) {
      Effect_size_tf <- data.frame(
        method = c("Trim Fill before", "Trim Fill after"),
        effect = c(round(exp(meta_analysis$TE.random), 2), round(exp(tf1$TE.random), 2)),
        lower = c(round(exp(meta_analysis$lower.random), 2), round(exp(tf1$lower.random), 2)),
        upper = c(round(exp(meta_analysis$upper.random), 2), round(exp(tf1$upper.random), 2)),
        n_filled = c(0, n_filled)
      )
      tf_csv <- file.path(output_dir, paste0(type, "_Trimfill_", outcome_name, ".csv"))
      write.csv(Effect_size_tf, tf_csv, row.names = FALSE)
    }
  }
}

# 输出结果摘要
cat("\n")
cat("═══════════════════════════════════════════\n")
cat("漏斗图绘制与发表偏倚检验完成\n")
cat("═══════════════════════════════════════════\n\n")
cat(paste0("【结局指标】", outcome_name, "\n"))
cat(paste0("【数据类型】", type, "\n"))
cat(paste0("【纳入研究】", n_studies, " 项\n\n"))
cat("【输出文件】\n")
cat(paste0("• 漏斗图：", funnel_file, "\n"))
cat(paste0("• 漏斗数据：", funnel_csv, "\n"))

if (!is.null(Egger_result)) {
  cat(paste0("• Egger检验：", file.path(output_dir, paste0(type, "_Egger_", outcome_name, ".csv")), "\n"))
}
if (!is.null(Begg_result)) {
  cat(paste0("• Begg检验：", file.path(output_dir, paste0(type, "_Begg_", outcome_name, ".csv")), "\n"))
}

cat("\n【发表偏倚检验结果】\n\n")

if (!is.null(Egger_result)) {
  egger_conclusion <- if (Egger_result$p_val < 0.05) "存在显著发表偏倚" else "无显著发表偏倚"
  cat("Egger线性回归检验：\n")
  cat(paste0("• 截距 = ", round(Egger_result$intercept, 4),
             " (SE = ", round(Egger_result$se.intercept, 4), ")\n"))
  cat(paste0("• t值 = ", round(Egger_result$statistic, 4), "\n"))
  cat(paste0("• P值 = ", round(Egger_result$p_val, 4), "\n"))
  cat(paste0("• 结论：", egger_conclusion, "\n\n"))
} else {
  cat("Egger检验：研究数量不足，无法进行检验\n\n")
}

if (!is.null(Begg_result)) {
  begg_conclusion <- if (Begg_result$p.val < 0.05) "存在显著发表偏倚" else "无显著发表偏倚"
  cat("Begg秩相关检验：\n")
  cat(paste0("• Kendall's tau = ", round(Begg_result$ks, 4), "\n"))
  cat(paste0("• z值 = ", round(Begg_result$statistic, 4), "\n"))
  cat(paste0("• P值 = ", round(Begg_result$p.val, 4), "\n"))
  cat(paste0("• 结论：", begg_conclusion, "\n\n"))
} else {
  cat("Begg检验：研究数量不足，无法进行检验\n\n")
}

if (!is.null(Effect_size_tf)) {
  cat("【剪补法分析】\n")
  cat(paste0("• 剪补前：", Effect_size_tf$effect[1],
             " [", Effect_size_tf$lower[1], "; ", Effect_size_tf$upper[1], "]\n"))
  cat(paste0("• 剪补后：", Effect_size_tf$effect[2],
             " [", Effect_size_tf$lower[2], "; ", Effect_size_tf$upper[2], "]\n"))
  cat(paste0("• 填补研究数：", Effect_size_tf$n_filled[2], "\n"))
}

cat("═══════════════════════════════════════════\n")
