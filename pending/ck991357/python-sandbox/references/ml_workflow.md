# 机器学习工作流指南 (v2.3)

## 🎯 工具概述
**功能**：机器学习模型训练、评估、统计分析和可视化  
**输出原则**：直接打印结果，系统自动处理输出格式  

**新增功能**：
- ✅ **XGBoost 1.7.6**：高性能梯度提升树模型
- ✅ **pmdarima 2.0.4**：自动化ARIMA时间序列建模
- ✅ 增强的时间序列分析能力
- ✅ 非线性模型与线性模型的对比分析

## 📊 基础机器学习模板

### 数据准备与预处理
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_ml_data():
    """机器学习数据准备示例"""
    
    # 创建示例数据集
    np.random.seed(42)
    n_samples = 1000
    
    # 回归问题数据
    X_reg = np.random.normal(0, 1, (n_samples, 5))
    y_reg = 2 * X_reg[:, 0] + 1.5 * X_reg[:, 1] - X_reg[:, 2] + np.random.normal(0, 0.5, n_samples)
    
    # 分类问题数据
    X_clf = np.random.normal(0, 1, (n_samples, 4))
    y_clf = (X_clf[:, 0] + X_clf[:, 1] > 0).astype(int)
    
    print("=== 数据准备完成 ===")
    print(f"样本数量: {n_samples}")
    print(f"回归特征维度: {X_reg.shape[1]}")
    print(f"分类特征维度: {X_clf.shape[1]}")
    print(f"分类标签分布: {np.unique(y_clf, return_counts=True)}")
    
    return X_reg, y_reg, X_clf, y_clf

# 使用示例
# X_reg, y_reg, X_clf, y_clf = prepare_ml_data()
```

### 标准机器学习工作流
```python
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.model_selection import cross_val_score

def standard_ml_pipeline(X, y, problem_type='regression'):
    """标准机器学习流程"""
    
    print(f"=== 开始 {problem_type} 模型训练 ===")
    
    # 数据分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y if problem_type == 'classification' else None
    )
    
    print(f"训练集大小: {X_train.shape}")
    print(f"测试集大小: {X_test.shape}")
    
    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 选择模型
    if problem_type == 'regression':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # 训练模型
    model.fit(X_train_scaled, y_train)
    
    # 预测
    y_pred = model.predict(X_test_scaled)
    
    # 模型评估
    if problem_type == 'regression':
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        print(f"回归模型性能:")
        print(f"  MSE: {mse:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R²: {r2:.4f}")
        
        metrics = {'mse': mse, 'rmse': rmse, 'r2': r2}
    else:
        accuracy = accuracy_score(y_test, y_pred)
        print(f"分类模型性能:")
        print(f"  准确率: {accuracy:.4f}")
        print("\n详细分类报告:")
        print(classification_report(y_test, y_pred))
        
        metrics = {'accuracy': accuracy}
    
    # 交叉验证
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, 
                               scoring='r2' if problem_type == 'regression' else 'accuracy')
    print(f"交叉验证平均得分: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    return {
        'model': model,
        'metrics': metrics,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'cv_scores': cv_scores
    }

# 使用示例
# X_reg, y_reg, X_clf, y_clf = prepare_ml_data()
# regression_results = standard_ml_pipeline(X_reg, y_reg, 'regression')
# classification_results = standard_ml_pipeline(X_clf, y_clf, 'classification')
```

## 📈 回归分析完整工作流

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def complete_regression_analysis():
    """完整的回归分析工作流"""
    
    print("=== 开始回归分析 ===")
    
    # 1. 数据生成
    np.random.seed(42)
    n_samples = 500
    
    # 创建有意义的特征
    feature1 = np.random.normal(50, 15, n_samples)  # 年龄
    feature2 = np.random.normal(100, 25, n_samples) # 收入
    feature3 = np.random.normal(10, 3, n_samples)   # 教育年限
    feature4 = np.random.normal(0, 1, n_samples)    # 噪声特征
    
    # 创建目标变量（模拟房价）
    target = (50 * feature1 + 80 * feature2 + 5000 * feature3 + 
              10 * feature1 * feature3 + np.random.normal(0, 10000, n_samples))
    
    df = pd.DataFrame({
        '年龄': feature1,
        '收入': feature2,
        '教育年限': feature3,
        '噪声特征': feature4,
        '房价': target
    })
    
    print("数据基本信息:")
    print(f"数据集形状: {df.shape}")
    print(f"特征列表: {list(df.columns[:-1])}")
    print(f"目标变量: {df.columns[-1]}")
    
    # 2. 数据探索
    print("\n=== 数据探索 ===")
    print("数值特征统计:")
    print(df.describe())
    
    # 相关性分析
    correlation = df.corr()['房价'].sort_values(ascending=False)
    print("\n特征与目标变量相关性:")
    for feature, corr in correlation.items():
        if feature != '房价':
            print(f"  {feature}: {corr:.3f}")
    
    # 3. 模型训练
    X = df.drop('房价', axis=1)
    y = df['房价']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    # 4. 模型评估
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n=== 模型性能 ===")
    print(f"均方误差 (MSE): {mse:,.2f}")
    print(f"均方根误差 (RMSE): {rmse:,.2f}")
    print(f"决定系数 (R²): {r2:.4f}")
    
    # 5. 特征重要性
    feature_importance = pd.DataFrame({
        '特征': X.columns,
        '重要性': model.feature_importances_
    }).sort_values('重要性', ascending=False)
    
    print(f"\n=== 特征重要性 ===")
    for _, row in feature_importance.iterrows():
        print(f"  {row['特征']}: {row['重要性']:.4f}")
    
    # 6. 可视化分析
    plt.figure(figsize=(15, 10))
    
    # 实际值 vs 预测值
    plt.subplot(2, 3, 1)
    plt.scatter(y_test, y_pred, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('实际值')
    plt.ylabel('预测值')
    plt.title(f'预测效果 (R² = {r2:.3f})')
    plt.grid(True, alpha=0.3)
    
    # 残差分析
    plt.subplot(2, 3, 2)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('预测值')
    plt.ylabel('残差')
    plt.title('残差分析')
    plt.grid(True, alpha=0.3)
    
    # 特征重要性可视化
    plt.subplot(2, 3, 3)
    top_features = feature_importance.head(5)
    plt.barh(top_features['特征'], top_features['重要性'])
    plt.xlabel('重要性')
    plt.title('Top 5 特征重要性')
    plt.gca().invert_yaxis()
    
    # 误差分布
    plt.subplot(2, 3, 4)
    plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('残差')
    plt.ylabel('频数')
    plt.title('误差分布')
    plt.grid(True, alpha=0.3)
    
    # 相对误差
    plt.subplot(2, 3, 5)
    relative_error = np.abs(residuals / y_test) * 100
    plt.hist(relative_error, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('相对误差 (%)')
    plt.ylabel('频数')
    plt.title('相对误差分布')
    plt.grid(True, alpha=0.3)
    
    # 预测误差箱线图
    plt.subplot(2, 3, 6)
    plt.boxplot(relative_error)
    plt.ylabel('相对误差 (%)')
    plt.title('预测误差分布')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 7. 模型解释
    print(f"\n=== 模型解释 ===")
    print(f"模型性能: {'优秀' if r2 > 0.8 else '良好' if r2 > 0.6 else '一般'}")
    print(f"最重要的特征: {feature_importance.iloc[0]['特征']}")
    print(f"建议: 关注{feature_importance.iloc[0]['特征']}和{feature_importance.iloc[1]['特征']}的优化")
    
    return {
        'model': model,
        'metrics': {'mse': mse, 'rmse': rmse, 'r2': r2},
        'feature_importance': feature_importance,
        'predictions': y_pred
    }

# 使用示例
# regression_results = complete_regression_analysis()
```

## 🔍 分类分析完整工作流

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.datasets import make_classification

def complete_classification_analysis():
    """完整的分类分析工作流"""
    
    print("=== 开始分类分析 ===")
    
    # 1. 数据生成
    X, y = make_classification(
        n_samples=1000,
        n_features=8,
        n_informative=5,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    feature_names = [f'特征_{i+1}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['类别'] = y
    
    print("数据基本信息:")
    print(f"数据集形状: {df.shape}")
    print(f"特征数量: {X.shape[1]}")
    print(f"类别数量: {len(np.unique(y))}")
    print(f"类别分布: {np.unique(y, return_counts=True)}")
    
    # 2. 数据探索
    print("\n=== 数据探索 ===")
    print("数值特征统计:")
    print(df.describe())
    
    # 3. 模型训练
    X_data = df.drop('类别', axis=1)
    y_data = df['类别']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_data, y_data, test_size=0.2, random_state=42, stratify=y_data
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    # 4. 模型评估
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n=== 模型性能 ===")
    print(f"准确率: {accuracy:.4f}")
    print("\n详细分类报告:")
    print(classification_report(y_test, y_pred))
    
    # 5. 特征重要性
    feature_importance = pd.DataFrame({
        '特征': X_data.columns,
        '重要性': model.feature_importances_
    }).sort_values('重要性', ascending=False)
    
    print(f"\n=== 特征重要性 ===")
    for _, row in feature_importance.iterrows():
        print(f"  {row['特征']}: {row['重要性']:.4f}")
    
    # 6. 可视化分析
    plt.figure(figsize=(15, 10))
    
    # 混淆矩阵
    plt.subplot(2, 3, 1)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.title('混淆矩阵')
    
    # 特征重要性
    plt.subplot(2, 3, 2)
    top_features = feature_importance.head(8)
    plt.barh(top_features['特征'], top_features['重要性'])
    plt.xlabel('重要性')
    plt.title('特征重要性排名')
    plt.gca().invert_yaxis()
    
    # 类别分布
    plt.subplot(2, 3, 3)
    unique, counts = np.unique(y, return_counts=True)
    plt.pie(counts, labels=[f'类别 {cls}' for cls in unique], autopct='%1.1f%%')
    plt.title('类别分布')
    
    # 分类报告热力图
    plt.subplot(2, 3, 4)
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose().iloc[:-3, :-1]
    sns.heatmap(report_df, annot=True, cmap='YlOrRd', fmt='.3f')
    plt.title('分类指标热力图')
    
    # 学习曲线（简化版）
    plt.subplot(2, 3, 5)
    train_sizes = np.linspace(0.1, 1.0, 10)
    train_scores = []
    test_scores = []
    
    for size in train_sizes:
        n_train = int(size * len(X_train))
        X_train_sub = X_train.iloc[:n_train]
        y_train_sub = y_train.iloc[:n_train]
        
        model_temp = RandomForestClassifier(n_estimators=50, random_state=42)
        model_temp.fit(X_train_sub, y_train_sub)
        
        train_score = model_temp.score(X_train_sub, y_train_sub)
        test_score = model_temp.score(X_test, y_test)
        
        train_scores.append(train_score)
        test_scores.append(test_score)
    
    plt.plot(train_sizes, train_scores, 'o-', label='训练得分')
    plt.plot(train_sizes, test_scores, 'o-', label='测试得分')
    plt.xlabel('训练样本比例')
    plt.ylabel('准确率')
    plt.title('学习曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 类别预测分布
    plt.subplot(2, 3, 6)
    pred_counts = pd.Series(y_pred).value_counts().sort_index()
    true_counts = pd.Series(y_test).value_counts().sort_index()
    
    x = np.arange(len(true_counts))
    width = 0.35
    
    plt.bar(x - width/2, true_counts, width, label='真实分布', alpha=0.7)
    plt.bar(x + width/2, pred_counts, width, label='预测分布', alpha=0.7)
    plt.xlabel('类别')
    plt.ylabel('样本数')
    plt.title('类别分布对比')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 7. 模型解释
    print(f"\n=== 模型解释 ===")
    print(f"模型性能: {'优秀' if accuracy > 0.9 else '良好' if accuracy > 0.8 else '一般'}")
    print(f"最重要的特征: {feature_importance.iloc[0]['特征']}")
    print(f"最容易混淆的类别: 查看混淆矩阵对角线外的最大值")
    
    return {
        'model': model,
        'metrics': {'accuracy': accuracy},
        'feature_importance': feature_importance,
        'predictions': y_pred
    }

# 使用示例
# classification_results = complete_classification_analysis()
```

## 📊 统计建模分析

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

def statistical_modeling_analysis():
    """统计建模分析"""
    
    print("=== 开始统计建模分析 ===")
    
    # 创建示例数据
    np.random.seed(42)
    n_samples = 200
    
    data = pd.DataFrame({
        '广告投入': np.random.normal(1000, 300, n_samples),
        '价格': np.random.normal(50, 15, n_samples),
        '促销活动': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        '季节性': np.random.choice([0, 1], n_samples, p=[0.5, 0.5])
    })
    
    # 生成销售额（与特征有真实关系）
    data['销售额'] = (
        500 + 0.8 * data['广告投入'] - 5 * data['价格'] + 
        200 * data['促销活动'] + 150 * data['季节性'] + 
        np.random.normal(0, 100, n_samples)
    )
    
    print("数据基本信息:")
    print(f"样本数量: {len(data)}")
    print(f"特征: {list(data.columns[:-1])}")
    print("\n数据描述:")
    print(data.describe())
    
    # 1. OLS 回归分析
    print("\n=== OLS 回归分析 ===")
    model = smf.ols('销售额 ~ 广告投入 + 价格 + 促销活动 + 季节性', data=data).fit()
    
    print("回归结果摘要:")
    print(model.summary())
    
    # 2. 关键统计指标
    print(f"\n=== 关键统计指标 ===")
    print(f"R²: {model.rsquared:.4f}")
    print(f"调整R²: {model.rsquared_adj:.4f}")
    print(f"F统计量: {model.fvalue:.2f}")
    print(f"F统计量p值: {model.f_pvalue:.4f}")
    
    # 3. 系数解释
    print(f"\n=== 系数解释 ===")
    for feature, coef in model.params.items():
        p_value = model.pvalues[feature]
        significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
        print(f"{feature}: {coef:.2f} {significance} (p值: {p_value:.4f})")
    
    # 4. 残差分析
    print(f"\n=== 残差分析 ===")
    residuals = model.resid
    print(f"残差均值: {residuals.mean():.4f}")
    print(f"残差标准差: {residuals.std():.4f}")
    
    # 5. 可视化分析
    plt.figure(figsize=(15, 10))
    
    # 实际值 vs 预测值
    plt.subplot(2, 3, 1)
    y_pred_ols = model.predict(data[['广告投入', '价格', '促销活动', '季节性']])
    plt.scatter(data['销售额'], y_pred_ols, alpha=0.6)
    plt.plot([data['销售额'].min(), data['销售额'].max()], 
             [data['销售额'].min(), data['销售额'].max()], 'r--', lw=2)
    plt.xlabel('实际销售额')
    plt.ylabel('预测销售额')
    plt.title(f'OLS预测效果 (R² = {model.rsquared:.3f})')
    plt.grid(True, alpha=0.3)
    
    # 残差图
    plt.subplot(2, 3, 2)
    plt.scatter(y_pred_ols, residuals, alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('预测值')
    plt.ylabel('残差')
    plt.title('残差分析')
    plt.grid(True, alpha=0.3)
    
    # Q-Q图
    plt.subplot(2, 3, 3)
    sm.qqplot(residuals, line='45', ax=plt.gca())
    plt.title('Q-Q图（残差正态性检验）')
    
    # 特征与目标变量关系
    plt.subplot(2, 3, 4)
    plt.scatter(data['广告投入'], data['销售额'], alpha=0.6)
    plt.xlabel('广告投入')
    plt.ylabel('销售额')
    plt.title('广告投入 vs 销售额')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 5)
    plt.scatter(data['价格'], data['销售额'], alpha=0.6)
    plt.xlabel('价格')
    plt.ylabel('销售额')
    plt.title('价格 vs 销售额')
    plt.grid(True, alpha=0.3)
    
    # 系数可视化
    plt.subplot(2, 3, 6)
    coefficients = model.params.iloc[1:]  # 排除截距项
    colors = ['green' if p < 0.05 else 'red' for p in model.pvalues.iloc[1:]]
    plt.barh(coefficients.index, coefficients.values, color=colors)
    plt.axvline(x=0, color='black', linestyle='-')
    plt.xlabel('系数值')
    plt.title('特征系数（绿色表示显著）')
    
    plt.tight_layout()
    plt.show()
    
    # 6. 业务解释
    print(f"\n=== 业务解释 ===")
    print(f"模型解释力: {'强' if model.rsquared > 0.7 else '中等' if model.rsquared > 0.5 else '弱'}")
    
    significant_features = []
    for feature in model.params.index[1:]:  # 排除截距
        if model.pvalues[feature] < 0.05:
            significant_features.append(feature)
    
    if significant_features:
        print(f"显著影响特征: {', '.join(significant_features)}")
    else:
        print("没有发现统计显著的特征")
    
    return {
        'model': model,
        'rsquared': model.rsquared,
        'significant_features': significant_features,
        'residuals': residuals
    }

# 使用示例
# stats_results = statistical_modeling_analysis()
```

## ⏰ 时间序列分析（v2.3新增）

### 使用pmdarima进行自动化ARIMA建模

```python
from pmdarima import auto_arima
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

def time_series_arima_analysis(series, seasonal_period=7, forecast_steps=30):
    """自动化ARIMA时间序列分析"""
    
    print("=== 开始时间序列ARIMA分析 ===")
    
    # 1. 数据检查
    print(f"时间序列长度: {len(series)}")
    print(f"数据类型: {type(series)}")
    
    # 2. 自动ARIMA建模
    print("\n=== 自动ARIMA参数选择 ===")
    try:
        model = auto_arima(
            series,
            seasonal=True,
            m=seasonal_period,  # 季节性周期（7天为周季节性）
            stepwise=True,      # 使用逐步搜索，节省内存
            suppress_warnings=True,
            error_action='ignore',
            trace=True,         # 显示搜索过程
            random_state=42
        )
        
        print(f"最佳ARIMA参数: {model.order}")
        print(f"最佳季节性参数: {model.seasonal_order}")
        print(f"模型AIC: {model.aic():.2f}")
        
    except Exception as e:
        print(f"自动ARIMA失败: {e}")
        return None
    
    # 3. 模型摘要
    print("\n=== 模型摘要 ===")
    print(model.summary())
    
    # 4. 预测
    print(f"\n=== 未来{forecast_steps}期预测 ===")
    forecast, conf_int = model.predict(
        n_periods=forecast_steps,
        return_conf_int=True,
        alpha=0.05  # 95%置信区间
    )
    
    # 5. 模型评估（使用训练集最后部分作为验证）
    train_size = int(len(series) * 0.8)
    train = series[:train_size]
    test = series[train_size:]
    
    # 在训练集上重新拟合模型
    model.fit(train)
    predictions = model.predict(n_periods=len(test))
    
    # 计算指标
    mae = mean_absolute_error(test, predictions)
    rmse = np.sqrt(mean_squared_error(test, predictions))
    mape = np.mean(np.abs((test - predictions) / test)) * 100
    
    print(f"\n=== 模型性能评估 ===")
    print(f"MAE (平均绝对误差): {mae:.2f}")
    print(f"RMSE (均方根误差): {rmse:.2f}")
    print(f"MAPE (平均绝对百分比误差): {mape:.2f}%")
    
    # 6. 可视化
    plt.figure(figsize=(15, 10))
    
    # 原始序列与拟合值
    plt.subplot(2, 2, 1)
    plt.plot(series.index, series, label='原始序列', alpha=0.7)
    plt.plot(series.index, model.predict_in_sample(), label='拟合值', alpha=0.7)
    plt.xlabel('时间')
    plt.ylabel('值')
    plt.title('原始序列与模型拟合')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 残差分析
    plt.subplot(2, 2, 2)
    residuals = series - model.predict_in_sample()
    plt.plot(residuals.index, residuals, alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('时间')
    plt.ylabel('残差')
    plt.title('模型残差')
    plt.grid(True, alpha=0.3)
    
    # 预测结果
    plt.subplot(2, 2, 3)
    last_n = min(100, len(series))
    plt.plot(series.index[-last_n:], series.values[-last_n:], label='历史数据')
    
    # 创建未来时间索引
    if hasattr(series.index, 'freq'):
        future_index = pd.date_range(start=series.index[-1], periods=forecast_steps+1, freq=series.index.freq)[1:]
    else:
        future_index = range(len(series), len(series) + forecast_steps)
    
    plt.plot(future_index, forecast, label='预测值', color='red')
    plt.fill_between(future_index, conf_int[:, 0], conf_int[:, 1], color='pink', alpha=0.3, label='95%置信区间')
    plt.xlabel('时间')
    plt.ylabel('值')
    plt.title(f'未来{forecast_steps}期预测')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 残差分布
    plt.subplot(2, 2, 4)
    plt.hist(residuals.dropna(), bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('残差值')
    plt.ylabel('频数')
    plt.title('残差分布')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return {
        'model': model,
        'order': model.order,
        'seasonal_order': model.seasonal_order,
        'forecast': forecast,
        'confidence_interval': conf_int,
        'metrics': {'mae': mae, 'rmse': rmse, 'mape': mape},
        'residuals': residuals
    }

# 使用示例
# 假设df是一个时间序列DataFrame，index为日期，有一列'销售额'
# results = time_series_arima_analysis(df['销售额'], seasonal_period=7, forecast_steps=30)
```

### 使用XGBoost进行时间序列预测

```python
def time_series_xgboost_analysis(df, target_col, lag_features=7, forecast_steps=30):
    """使用XGBoost进行时间序列预测"""
    
    print("=== 开始时间序列XGBoost分析 ===")
    
    # 1. 准备特征
    print("准备时间序列特征...")
    features_df = pd.DataFrame(index=df.index)
    
    # 滞后特征
    for lag in range(1, lag_features + 1):
        features_df[f'lag_{lag}'] = df[target_col].shift(lag)
    
    # 滚动统计特征
    for window in [3, 7, 14, 30]:
        features_df[f'ma_{window}'] = df[target_col].rolling(window).mean().shift(1)
        features_df[f'std_{window}'] = df[target_col].rolling(window).std().shift(1)
    
    # 日期特征
    if hasattr(df.index, 'month'):
        features_df['month'] = df.index.month
        features_df['dayofweek'] = df.index.dayofweek
        features_df['dayofmonth'] = df.index.day
        features_df['quarter'] = df.index.quarter
    
    # 外部特征（如果存在）
    external_features = ['Temperature', 'Promotion', 'Competitor_Price', 'Holiday']
    for feat in external_features:
        if feat in df.columns:
            features_df[feat] = df[feat]
    
    # 目标变量
    features_df['target'] = df[target_col]
    
    # 移除缺失值
    features_df = features_df.dropna()
    
    print(f"特征矩阵形状: {features_df.shape}")
    
    # 2. 划分训练集和测试集
    X = features_df.drop('target', axis=1)
    y = features_df['target']
    
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"训练集大小: {X_train.shape}")
    print(f"测试集大小: {X_test.shape}")
    
    # 3. 训练XGBoost模型
    print("\n训练XGBoost模型...")
    
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method='hist',  # 内存友好
        n_jobs=2,           # 6GB内存下使用2个线程
        random_state=42,
        verbosity=0
    )
    
    xgb_model.fit(X_train, y_train)
    
    # 4. 模型评估
    y_pred = xgb_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    print(f"\n=== XGBoost模型性能 ===")
    print(f"MAE (平均绝对误差): {mae:.2f}")
    print(f"RMSE (均方根误差): {rmse:.2f}")
    print(f"MAPE (平均绝对百分比误差): {mape:.2f}%")
    
    # 5. 特征重要性
    feature_importance = pd.DataFrame({
        '特征': X.columns,
        '重要性': xgb_model.feature_importances_
    }).sort_values('重要性', ascending=False)
    
    print(f"\n=== 特征重要性（Top 10）===")
    for _, row in feature_importance.head(10).iterrows():
        print(f"  {row['特征']}: {row['重要性']:.4f}")
    
    # 6. 可视化
    plt.figure(figsize=(15, 10))
    
    # 预测 vs 实际
    plt.subplot(2, 3, 1)
    plt.scatter(y_test, y_pred, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('实际值')
    plt.ylabel('预测值')
    plt.title(f'XGBoost预测效果 (MAE = {mae:.2f})')
    plt.grid(True, alpha=0.3)
    
    # 特征重要性
    plt.subplot(2, 3, 2)
    top_features = feature_importance.head(10)
    plt.barh(top_features['特征'], top_features['重要性'])
    plt.xlabel('重要性')
    plt.title('Top 10 特征重要性')
    plt.gca().invert_yaxis()
    
    # 时间序列预测对比
    plt.subplot(2, 3, 3)
    plt.plot(y_test.index, y_test.values, label='实际值', alpha=0.7)
    plt.plot(y_test.index, y_pred, label='预测值', alpha=0.7)
    plt.xlabel('时间')
    plt.ylabel('值')
    plt.title('时间序列预测对比')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 残差分析
    plt.subplot(2, 3, 4)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('预测值')
    plt.ylabel('残差')
    plt.title('残差分析')
    plt.grid(True, alpha=0.3)
    
    # 误差分布
    plt.subplot(2, 3, 5)
    plt.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('残差')
    plt.ylabel('频数')
    plt.title('误差分布')
    plt.grid(True, alpha=0.3)
    
    # 滚动预测
    plt.subplot(2, 3, 6)
    # 取最后100个点展示
    last_n = min(100, len(y_test))
    plt.plot(y_test.index[-last_n:], y_test.values[-last_n:], label='实际值')
    plt.plot(y_test.index[-last_n:], y_pred[-last_n:], label='预测值')
    plt.xlabel('时间')
    plt.ylabel('值')
    plt.title('滚动预测对比（最后100点）')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 7. 未来预测（如果需要）
    if forecast_steps > 0:
        print(f"\n=== 未来{forecast_steps}期预测 ===")
        # 注意：这里需要根据具体业务逻辑实现滚动预测
        # 简化版：使用最后lag_features个点作为初始特征
        
        last_features = X.iloc[-1:].copy()
        future_predictions = []
        
        for i in range(forecast_steps):
            # 预测下一步
            pred = xgb_model.predict(last_features)[0]
            future_predictions.append(pred)
            
            # 更新特征（如果是时间序列预测，需要更新滞后特征）
            # 这里简化为只使用最新预测值
            # 实际应用中需要根据特征工程逻辑更新
            
        print(f"未来预测值: {future_predictions}")
    
    return {
        'model': xgb_model,
        'metrics': {'mae': mae, 'rmse': rmse, 'mape': mape},
        'feature_importance': feature_importance,
        'predictions': y_pred,
        'future_predictions': future_predictions if forecast_steps > 0 else None
    }

# 使用示例
# 假设df是一个DataFrame，包含时间序列和外部特征
# results = time_series_xgboost_analysis(df, target_col='Sales', lag_features=14, forecast_steps=30)
```

### 时间序列模型对比

```python
def compare_time_series_models(df, target_col, seasonal_period=7, lag_features=14):
    """对比不同时间序列模型性能"""
    
    print("=== 时间序列模型对比分析 ===")
    
    # 准备数据
    series = df[target_col]
    
    # 1. ARIMA模型
    print("\n1. 训练ARIMA模型...")
    arima_results = time_series_arima_analysis(series, seasonal_period, forecast_steps=0)
    
    # 2. XGBoost模型
    print("\n2. 训练XGBoost模型...")
    xgb_results = time_series_xgboost_analysis(df, target_col, lag_features, forecast_steps=0)
    
    # 3. LightGBM模型（如果可用）
    try:
        import lightgbm as lgb
        print("\n3. 训练LightGBM模型...")
        
        # 准备特征（复用XGBoost的特征）
        features_df = pd.DataFrame(index=df.index)
        for lag in range(1, lag_features + 1):
            features_df[f'lag_{lag}'] = df[target_col].shift(lag)
        
        for window in [3, 7, 14, 30]:
            features_df[f'ma_{window}'] = df[target_col].rolling(window).mean().shift(1)
        
        if hasattr(df.index, 'month'):
            features_df['month'] = df.index.month
            features_df['dayofweek'] = df.index.dayofweek
        
        external_features = ['Temperature', 'Promotion', 'Competitor_Price', 'Holiday']
        for feat in external_features:
            if feat in df.columns:
                features_df[feat] = df[feat]
        
        features_df['target'] = df[target_col]
        features_df = features_df.dropna()
        
        X = features_df.drop('target', axis=1)
        y = features_df['target']
        
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # 训练LightGBM
        lgb_model = lgb.LGBMRegressor(
            num_leaves=31,
            learning_rate=0.05,
            n_estimators=100,
            n_jobs=2,
            random_state=42,
            verbose=-1
        )
        
        lgb_model.fit(X_train, y_train)
        y_pred_lgb = lgb_model.predict(X_test)
        
        mae_lgb = mean_absolute_error(y_test, y_pred_lgb)
        rmse_lgb = np.sqrt(mean_squared_error(y_test, y_pred_lgb))
        
        print(f"LightGBM性能: MAE={mae_lgb:.2f}, RMSE={rmse_lgb:.2f}")
        
        lgb_results = {
            'model': lgb_model,
            'metrics': {'mae': mae_lgb, 'rmse': rmse_lgb}
        }
        
    except ImportError:
        print("LightGBM不可用，跳过")
        lgb_results = None
    
    # 4. 模型对比
    print("\n=== 模型性能对比 ===")
    
    comparison_data = []
    
    if arima_results:
        comparison_data.append({
            '模型': 'ARIMA',
            'MAE': arima_results['metrics']['mae'],
            'RMSE': arima_results['metrics']['rmse'],
            'MAPE': arima_results['metrics']['mape']
        })
    
    if xgb_results:
        comparison_data.append({
            '模型': 'XGBoost',
            'MAE': xgb_results['metrics']['mae'],
            'RMSE': xgb_results['metrics']['rmse'],
            'MAPE': xgb_results['metrics']['mape']
        })
    
    if lgb_results:
        comparison_data.append({
            '模型': 'LightGBM',
            'MAE': lgb_results['metrics']['mae'],
            'RMSE': lgb_results['metrics']['rmse'],
            'MAPE': None
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))
    
    # 5. 可视化对比
    if len(comparison_data) > 1:
        plt.figure(figsize=(12, 5))
        
        # MAE对比
        plt.subplot(1, 2, 1)
        models = [d['模型'] for d in comparison_data]
        maes = [d['MAE'] for d in comparison_data]
        
        bars = plt.bar(models, maes, alpha=0.7)
        plt.xlabel('模型')
        plt.ylabel('MAE')
        plt.title('模型MAE对比')
        plt.grid(True, alpha=0.3)
        
        # 在柱子上添加数值
        for bar, mae in zip(bars, maes):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                    f'{mae:.2f}', ha='center', va='bottom')
        
        # RMSE对比
        plt.subplot(1, 2, 2)
        rmses = [d['RMSE'] for d in comparison_data]
        
        bars = plt.bar(models, rmses, alpha=0.7, color='orange')
        plt.xlabel('模型')
        plt.ylabel('RMSE')
        plt.title('模型RMSE对比')
        plt.grid(True, alpha=0.3)
        
        for bar, rmse in zip(bars, rmses):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                    f'{rmse:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        # 推荐模型
        best_model_idx = np.argmin(maes)
        best_model = models[best_model_idx]
        print(f"\n=== 推荐模型 ===")
        print(f"根据MAE指标，推荐使用: {best_model}模型")
        print(f"理由: 在测试集上表现最佳 (MAE = {maes[best_model_idx]:.2f})")
    
    return {
        'arima': arima_results,
        'xgboost': xgb_results,
        'lightgbm': lgb_results,
        'comparison': comparison_df
    }

# 使用示例
# 假设有完整的时间序列数据集df
# model_comparison = compare_time_series_models(df, target_col='Sales', seasonal_period=7, lag_features=14)
```

## 🔧 模型优化与调参

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

def model_optimization_pipeline(X, y, problem_type='regression'):
    """模型超参数优化流程"""
    
    print(f"=== 开始 {problem_type} 模型优化 ===")
    
    # 数据分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 选择模型和参数网格
    if problem_type == 'regression':
        model = RandomForestRegressor(random_state=42)
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        scoring = 'r2'
    else:
        model = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        scoring = 'accuracy'
    
    # 网格搜索
    print("正在进行网格搜索...")
    grid_search = GridSearchCV(
        model, param_grid, cv=5, scoring=scoring, 
        n_jobs=-1, verbose=1
    )
    grid_search.fit(X_train, y_train)
    
    # 输出最优参数
    print(f"\n=== 最优参数 ===")
    for param, value in grid_search.best_params_.items():
        print(f"  {param}: {value}")
    
    print(f"最优模型得分: {grid_search.best_score_:.4f}")
    
    # 测试集性能
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    if problem_type == 'regression':
        test_score = r2_score(y_test, y_pred)
        print(f"测试集 R²: {test_score:.4f}")
    else:
        test_score = accuracy_score(y_test, y_pred)
        print(f"测试集准确率: {test_score:.4f}")
    
    return {
        'best_model': best_model,
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'test_score': test_score
    }

# 使用示例
# X_reg, y_reg, X_clf, y_clf = prepare_ml_data()
# optimized_regression = model_optimization_pipeline(X_reg, y_reg, 'regression')
# optimized_classification = model_optimization_pipeline(X_clf, y_clf, 'classification')
```

## 机器学习增强(v2.5新增)

### LightGBM - 高效梯度提升

**用途**: 高性能梯度提升树算法  
**优势**: 比XGBoost训练更快，内存占用更少  

```python
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import pandas as pd

# 准备数据
data = pd.read_csv('/data/train.csv')
X = data.drop('target', axis=1)
y = data['target']

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建数据集
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

# 参数设置（优化内存使用）
params = {
    'boosting_type': 'gbdt',
    'objective': 'binary',
    'metric': 'binary_logloss',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'num_threads': 2  # 限制线程数
}

# 训练模型
gbm = lgb.train(params, train_data, num_boost_round=100)
```

### Category Encoders - 分类特征编码

**用途**: 各种分类编码方法  
**优势**: 提升分类模型性能，支持多种编码策略  

```python
import pandas as pd
import category_encoders as ce

# 创建示例数据
df = pd.DataFrame({
    'category': ['A', 'B', 'A', 'C', 'B', 'A'],
    'value': [1, 2, 3, 4, 5, 6]
})

# 使用Target Encoding
encoder = ce.TargetEncoder(cols=['category'])
df_encoded = encoder.fit_transform(df['category'], df['value'])

print(df_encoded)
```

### XGBoost - 高性能梯度提升树 (v2.3新增)

**用途**: 高级梯度提升树算法，支持回归、分类、排序任务  
**优势**: 精度高，支持自定义目标函数，可解释性好  

```python
import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

# 准备数据
data = pd.read_csv('/data/train.csv')
X = data.drop('target', axis=1)
y = data['target']

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建DMatrix（XGBoost高效数据结构）
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# 参数设置（回归问题示例）
params = {
    'objective': 'reg:squarederror',  # 回归任务
    'max_depth': 5,
    'eta': 0.1,  # 学习率
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'hist',  # 内存友好的直方图算法
    'n_jobs': 2,  # 6GB内存下使用2个线程
    'random_state': 42
}

# 训练模型
num_rounds = 100
model = xgb.train(params, dtrain, num_rounds)

# 预测
y_pred = model.predict(dtest)

# 评估
if data['target'].dtype == 'object':  # 分类任务
    accuracy = accuracy_score(y_test, y_pred.round())
    print(f"准确率: {accuracy:.4f}")
else:  # 回归任务
    mse = mean_squared_error(y_test, y_pred)
    print(f"MSE: {mse:.4f}")

# 特征重要性
importance = model.get_score(importance_type='weight')
print("特征重要性:", importance)

# 保存模型
model.save_model('/data/xgboost_model.json')
```

### scikit-optimize - 贝叶斯超参数优化

**用途**: 自动化超参数优化  
**优势**: 比网格搜索更高效，找到更好参数组合  

```python
from skopt import BayesSearchCV
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# 准备数据
data = pd.read_csv('/data/train.csv')
X = data.drop('target', axis=1)
y = data['target']

# 定义参数搜索空间
param_space = {
    'n_estimators': (50, 200),
    'max_depth': (3, 10),
    'min_samples_split': (2, 10),
    'min_samples_leaf': (1, 4)
}

# 贝叶斯优化搜索
opt = BayesSearchCV(
    RandomForestClassifier(),
    param_space,
    n_iter=50,
    cv=5,
    n_jobs=2  # 限制并行线程
)

opt.fit(X, y)
print(f"最佳参数: {opt.best_params_}")
print(f"最佳分数: {opt.best_score_:.4f}")
```

## ⚠️ 使用注意事项

### ✅ 推荐做法：
- 使用标准的 scikit-learn 和 statsmodels 接口
- 直接使用 `print()` 输出结果和指标
- 使用 `plt.show()` 显示图表
- 对数据进行适当的预处理和标准化
- 时间序列分析优先使用pmdarima自动选择ARIMA参数
- 非线性建模优先使用XGBoost或LightGBM

### ❌ 避免的操作：
- 不要手动构建 JSON 输出
- 不要使用 `base64` 编码
- 不要创建复杂的自定义输出格式
- 不要对明显季节性数据使用非季节性ARIMA

### 🔧 错误处理：
```python
try:
    from sklearn.ensemble import RandomForestRegressor
    # 模型训练代码
except ImportError:
    print("scikit-learn 不可用")

try:
    import statsmodels.api as sm
    # 统计建模代码
except ImportError:
    print("statsmodels 不可用")

try:
    import xgboost as xgb
    # XGBoost代码
except ImportError:
    print("XGBoost 不可用，请检查环境配置")

try:
    import pmdarima as pm
    # ARIMA代码
except ImportError:
    print("pmdarima 不可用，请检查环境配置")
```

### 💡 实用技巧：
```python
# 快速模型评估函数
def quick_model_evaluation(model, X_test, y_test, problem_type='regression'):
    """快速模型评估"""
    y_pred = model.predict(X_test)
    
    if problem_type == 'regression':
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f"R²: {r2:.4f}, RMSE: {rmse:.4f}")
    else:
        accuracy = accuracy_score(y_test, y_pred)
        print(f"准确率: {accuracy:.4f}")
    
    return y_pred

# 时间序列分析快速模板
def quick_time_series_analysis(series, model_type='auto_arima'):
    """快速时间序列分析模板"""
    if model_type == 'auto_arima':
        from pmdarima import auto_arima
        model = auto_arima(series, seasonal=True, m=7, suppress_warnings=True)
        forecast = model.predict(n_periods=30)
    elif model_type == 'xgboost':
        # 使用time_series_xgboost_analysis函数
        pass
    
    return model, forecast
```

**记住**：系统会自动处理所有输出格式，您只需要专注于机器学习建模和分析逻辑！

## 📁 沙盒环境文件操作指南

### 文件上传（必须步骤）
在沙盒中运行代码前，**必须先上传数据文件**：

```python
# 示例：如何引用已上传的文件
# 假设您已经通过前端界面上传了以下文件：
# - /data/train.csv      （通过文件上传API上传）
# - /data/dataset.xlsx   （通过文件上传API上传）
# - /data/sales.parquet  （通过文件上传API上传）

import pandas as pd
import os

def list_uploaded_files():
    """列出所有已上传的文件"""
    data_dir = '/data'
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        print(f"已上传的文件: {files}")
        return files
    else:
        print("没有找到/data目录")
        return []

# 列出文件
available_files = list_uploaded_files()

# 读取特定文件
if 'train.csv' in available_files:
    df = pd.read_csv('/data/train.csv')
    print(f"成功读取 train.csv，形状: {df.shape}")
    
if 'dataset.xlsx' in available_files:
    df = pd.read_excel('/data/dataset.xlsx')
    print(f"成功读取 dataset.xlsx，形状: {df.shape}")
```

### 支持的文件格式
根据code_interpreter.py，系统支持以下文件格式：
- 📊 数据文件：`.csv`, `.xlsx`, `.xls`, `.parquet`, `.json`

### 文件读取最佳实践
```python
def safe_read_data(filename):
    """安全读取数据文件，带错误处理"""
    try:
        filepath = f'/data/{filename}'
        
        # 根据扩展名选择读取方法
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(filepath)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        elif filename.endswith('.json'):
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"不支持的文件格式: {filename}")
        
        print(f"✅ 成功读取 {filename}")
        print(f"   行数: {len(df)}, 列数: {len(df.columns)}")
        print(f"   列名: {list(df.columns)}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filename}")
        print("请先通过文件上传功能上传文件")
        return None
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 检查可用的文件
    files = list_uploaded_files()
    if files:
        for file in files:
            print(f"发现文件: {file}")
        
        # 读取第一个CSV文件
        csv_files = [f for f in files if f.endswith('.csv')]
        if csv_files:
            df = safe_read_data(csv_files[0])
            if df is not None:
                # 进行机器学习分析
                pass
```

### 工作流整合示例
```python
# 完整的ML工作流，包含文件检查
def complete_ml_workflow_with_file_check():
    """包含文件检查的完整ML工作流"""
    
    print("=== 机器学习工作流开始 ===")
    
    # 1. 检查数据文件
    files = list_uploaded_files()
    if not files:
        print("警告：没有找到上传的文件，将使用示例数据")
        # 使用generate_sample_data()函数创建示例数据
        from sklearn.datasets import make_regression
        X, y = make_regression(n_samples=1000, n_features=10, random_state=42)
    else:
        print(f"找到 {len(files)} 个文件: {files}")
        
        # 读取第一个数据文件
        data_file = files[0]
        df = safe_read_data(data_file)
        
        if df is None:
            print("无法读取文件，使用示例数据")
            from sklearn.datasets import make_regression
            X, y = make_regression(n_samples=1000, n_features=10, random_state=42)
        else:
            # 假设最后一列是目标变量
            X = df.iloc[:, :-1].values
            y = df.iloc[:, -1].values
    
    # 2. 执行ML分析（使用文档中的函数）
    results = standard_ml_pipeline(X, y, problem_type='regression')
    
    return results
```

### ⚡ 快速使用模板
```python
# 在沙盒中运行机器学习分析的完整示例
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 步骤1：读取数据（替换为您的文件名）
try:
    # 如果您上传了train.csv
    df = pd.read_csv('/data/train.csv')
    print(f"数据形状: {df.shape}")
    
    # 步骤2：准备特征和目标
    X = df.drop('target_column', axis=1)  # 替换为您的目标列名
    y = df['target_column']
    
    # 步骤3：训练模型
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 步骤4：评估
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"模型性能: R²={r2:.4f}, RMSE={rmse:.4f}")
    
    # 步骤5：可视化
    plt.figure(figsize=(10, 5))
    plt.scatter(y_test, y_pred, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('实际值')
    plt.ylabel('预测值')
    plt.title(f'预测效果 (R² = {r2:.3f})')
    plt.grid(True, alpha=0.3)
    plt.show()
    
except FileNotFoundError:
    print("❌ 未找到文件。请确保：")
    print("   1. 已通过文件上传功能上传train.csv")
    print("   2. 文件位于/data目录下")
    print("   3. 文件名拼写正确")
    
    # 提供示例数据作为备选
    print("\n🔧 正在生成示例数据进行分析...")
    from sklearn.datasets import make_regression
    X, y = make_regression(n_samples=1000, n_features=5, random_state=42)
    
    # 继续执行分析...
```
