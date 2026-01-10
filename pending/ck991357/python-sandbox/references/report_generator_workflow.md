# 自动化报告生成指南 (v3.0 - 完整版)

## 🚀 核心输出协议 (强制遵循)

**重要提示**: 要生成一个可供用户下载的文件（Word, Excel, PDF, PPT等），你的Python代码**必须**将文件内容进行Base64编码，并将其包裹在一个特定格式的JSON对象中，然后 `print` 这个JSON对象。

**工作流**:
1. **导入必要库**: `io`, `base64`, `json`。
2. **在内存中创建文件**: 使用 `io.BytesIO()` 创建一个内存缓冲区。
3. **保存到内存**: 调用相应库的 `.save(buffer)` 方法将文件内容写入内存缓冲区。
4. **编码**: 将缓冲区中的二进制数据编码为Base64字符串。
5. **打包并打印**: 构建一个包含 `type` 和 `data_base64` 字段的字典，并使用 `json.dumps()` 打印出来。

**JSON格式规范**:
```json
{
    "type": "文件类型",  // 必须是：word, excel, pdf, ppt 之一
    "title": "文件名.后缀",
    "data_base64": "Base64编码的二进制数据"
}
```

---

## 📊 Word 报告生成 (.docx)

### ✅ 可直接使用的代码模板
```python
import io
import base64
import json
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import datetime

# --- 1. 在内存中构建 Word 文档 ---
doc = Document()
doc.add_heading('业务分析报告', 0)

# 添加报告信息
p = doc.add_paragraph()
p.add_run(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}').bold = True
doc.add_paragraph('这是一个由代码解释器生成的Word文档示例。')

# 添加表格
table = doc.add_table(rows=3, cols=3)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# 设置表头
header_cells = table.rows[0].cells
header_cells[0].text = '项目'
header_cells[1].text = '预算(元)'
header_cells[2].text = '实际支出(元)'

# 添加数据
data_rows = [
    ('营销活动', '50,000', '48,200'),
    ('研发投入', '200,000', '198,500'),
    ('行政费用', '30,000', '31,200')
]

for i, (item, budget, actual) in enumerate(data_rows, 1):
    row_cells = table.rows[i].cells
    row_cells[0].text = item
    row_cells[1].text = budget
    row_cells[2].text = actual

# 添加总结段落
doc.add_heading('总结', level=2)
doc.add_paragraph('总体来看，各部门预算执行情况良好，实际支出基本控制在预算范围内。')

# --- 2. 保存到内存缓冲区 ---
buffer = io.BytesIO()
doc.save(buffer)
buffer.seek(0)  # 重置指针到开头

# --- 3. Base64 编码并打包为 JSON ---
data_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
result = {
    "type": "word",
    "title": f"业务分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
    "data_base64": data_base64
}

# --- 4. 打印最终的 JSON 对象 ---
print(json.dumps(result))
```

---

## 📈 Excel 报告生成 (.xlsx)

### ✅ 可直接使用的代码模板
```python
import io
import base64
import json
import pandas as pd
import numpy as np
from datetime import datetime
from openpyxl.styles import Font, Alignment, PatternFill

# --- 1. 创建 DataFrame 并准备 Excel 内容 ---
data = {
    '部门': ['销售部', '研发部', '市场部', '人力资源部', '财务部'],
    '预算(元)': [500000, 800000, 300000, 200000, 150000],
    '实际支出(元)': [485000, 795000, 310000, 195000, 148000],
    '差异率(%)': [-3.0, -0.6, 3.3, -2.5, -1.3]
}
df = pd.DataFrame(data)

# 计算总计
summary_data = {
    '部门': ['总计'],
    '预算(元)': [df['预算(元)'].sum()],
    '实际支出(元)': [df['实际支出(元)'].sum()],
    '差异率(%)': [round((df['实际支出(元)'].sum() - df['预算(元)'].sum()) / df['预算(元)'].sum() * 100, 2)]
}
summary_df = pd.DataFrame(summary_data)

# --- 2. 使用 ExcelWriter 将 DataFrame 写入内存缓冲区 ---
output_buffer = io.BytesIO()
with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
    # 写入详细数据表
    df.to_excel(writer, sheet_name='部门预算详情', index=False)
    
    # 写入汇总表
    summary_df.to_excel(writer, sheet_name='预算汇总', index=False)
    
    # 获取工作簿和工作表以进行格式设置
    workbook = writer.book
    detail_sheet = writer.sheets['部门预算详情']
    summary_sheet = writer.sheets['预算汇总']
    
    # 设置列宽
    for column in detail_sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        detail_sheet.column_dimensions[column_letter].width = adjusted_width
        
    # 设置标题样式
    for cell in detail_sheet[1]:
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')
    
    for cell in summary_sheet[1]:
        cell.font = Font(bold=True, size=14, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')

output_buffer.seek(0)

# --- 3. Base64 编码并打包为 JSON ---
data_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
result = {
    "type": "excel",
    "title": f"部门预算报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    "data_base64": data_base64
}

# --- 4. 打印最终的 JSON 对象 ---
print(json.dumps(result))
```

---

## 📊 高级Excel操作（v2.5新增）

### 使用多个工作表和数据透视表
```python
import pandas as pd
import io
import base64
import json
from datetime import datetime

def create_advanced_excel_report():
    """创建包含多个工作表和复杂分析的Excel报告"""
    
    # 创建示例数据
    sales_data = {
        '日期': pd.date_range('2024-01-01', periods=30, freq='D'),
        '产品': np.random.choice(['A', 'B', 'C', 'D'], 30),
        '销售额': np.random.randint(1000, 10000, 30),
        '数量': np.random.randint(10, 100, 30)
    }
    
    customer_data = {
        '客户ID': [f'C{1000+i}' for i in range(10)],
        '客户名称': [f'客户_{i}' for i in range(10)],
        '地区': np.random.choice(['华东', '华南', '华北', '西南'], 10),
        '信用评级': np.random.choice(['A', 'B', 'C'], 10)
    }
    
    df_sales = pd.DataFrame(sales_data)
    df_customers = pd.DataFrame(customer_data)
    
    # 创建数据透视表
    pivot_table = pd.pivot_table(df_sales, 
                                 values='销售额', 
                                 index='产品', 
                                 columns=df_sales['日期'].dt.strftime('%Y-%m-%d'), 
                                 aggfunc='sum',
                                 fill_value=0)
    
    # 创建缓冲区
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 写入原始数据
        df_sales.to_excel(writer, sheet_name='销售数据', index=False)
        df_customers.to_excel(writer, sheet_name='客户数据', index=False)
        
        # 写入数据透视表
        pivot_table.to_excel(writer, sheet_name='销售汇总')
        
        # 写入分析结果
        analysis_data = {
            '指标': ['总销售额', '平均销售额', '最高销售额', '最低销售额'],
            '数值': [
                df_sales['销售额'].sum(),
                df_sales['销售额'].mean(),
                df_sales['销售额'].max(),
                df_sales['销售额'].min()
            ]
        }
        df_analysis = pd.DataFrame(analysis_data)
        df_analysis.to_excel(writer, sheet_name='分析结果', index=False)
    
    buffer.seek(0)
    
    # 编码并输出
    data_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    result = {
        "type": "excel",
        "title": f"高级销售分析报告_{datetime.now().strftime('%Y%m%d')}.xlsx",
        "data_base64": data_base64
    }
    
    print(json.dumps(result))
```

---

## 📄 PDF 报告生成 (.pdf)

### ✅ 可直接使用的代码模板
```python
import io
import base64
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# --- 创建图表并保存到内存 ---
def create_chart_image():
    """创建一个示例图表并返回Base64编码"""
    plt.figure(figsize=(8, 4))
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    values = [120, 145, 180, 160]
    plt.bar(categories, values, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
    plt.title('季度销售额趋势')
    plt.xlabel('季度')
    plt.ylabel('销售额(万元)')
    plt.grid(True, alpha=0.3)
    
    # 将图表保存到内存
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    chart_buffer.seek(0)
    return chart_buffer

# --- 1. 在内存中构建 PDF 文档 ---
buffer = io.BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
styles = getSampleStyleSheet()

# 自定义样式
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontSize=24,
    spaceAfter=30,
    alignment=1  # 居中
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    spaceBefore=20,
    spaceAfter=10
)

# 构建内容
story = []
story.append(Paragraph("公司年度财务报告", title_style))
story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", styles['Normal']))
story.append(Spacer(1, 20))

# 添加摘要
story.append(Paragraph("执行摘要", heading_style))
story.append(Paragraph("本报告详细分析了公司2024年度的财务状况和业务表现，包括收入、支出、利润等关键指标。", styles['BodyText']))
story.append(Spacer(1, 15))

# 添加图表
chart_buffer = create_chart_image()
story.append(Paragraph("季度销售趋势", heading_style))
story.append(Image(chart_buffer, width=6*inch, height=3*inch))
story.append(Spacer(1, 15))

# 添加表格
story.append(Paragraph("财务数据汇总", heading_style))
data = [
    ['项目', 'Q1', 'Q2', 'Q3', 'Q4', '年度总计'],
    ['收入(万元)', '450', '520', '610', '580', '2160'],
    ['成本(万元)', '280', '310', '350', '320', '1260'],
    ['利润(万元)', '170', '210', '260', '260', '900'],
    ['利润率(%)', '37.8', '40.4', '42.6', '44.8', '41.7']
]

table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))

story.append(table)
story.append(Spacer(1, 20))

# 添加结论
story.append(Paragraph("结论与建议", heading_style))
story.append(Paragraph("1. 公司全年收入稳步增长，第四季度略有回落但整体表现良好。", styles['BodyText']))
story.append(Paragraph("2. 利润率逐季度提升，显示成本控制措施效果显著。", styles['BodyText']))
story.append(Paragraph("3. 建议明年加大研发投入，优化产品结构，进一步提升盈利能力。", styles['BodyText']))

# 构建文档
doc.build(story)
buffer.seek(0)

# --- 2. Base64 编码并打包为 JSON ---
data_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
result = {
    "type": "pdf",
    "title": f"公司年度财务报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
    "data_base64": data_base64
}

# --- 3. 打印最终的 JSON 对象 ---
print(json.dumps(result))
```

---

## 🎤 PowerPoint 报告生成 (.pptx) - v2.5新增

### ✅ 可直接使用的代码模板
```python
import io
import base64
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# --- 1. 在内存中构建 PowerPoint 文档 ---
prs = Presentation()

# 创建标题页
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "季度业务汇报"
subtitle.text = f"{datetime.now().strftime('%Y年%m月')}\n数据分析团队"

# 创建目录页
bullet_slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(bullet_slide_layout)
shapes = slide.shapes

title_shape = shapes.title
title_shape.text = '汇报目录'

body_shape = shapes.placeholders[1]
tf = body_shape.text_frame
tf.text = '1. 业绩概览'
p = tf.add_paragraph()
p.text = '2. 市场分析'
p = tf.add_paragraph()
p.text = '3. 财务数据'
p = tf.add_paragraph()
p.text = '4. 未来展望'

# 创建图表页 - 业绩概览
slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "业绩概览"

# 在内存中创建图表
plt.figure(figsize=(6, 4))
months = ['1月', '2月', '3月', '4月', '5月', '6月']
sales = [120, 135, 150, 145, 160, 180]
targets = [110, 130, 140, 150, 155, 170]

x = np.arange(len(months))
width = 0.35

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, sales, width, label='实际销售额', color='#2E86AB')
rects2 = ax.bar(x + width/2, targets, width, label='目标销售额', color='#A23B72')

ax.set_xlabel('月份')
ax.set_ylabel('销售额(万元)')
ax.set_title('上半年销售额对比')
ax.set_xticks(x)
ax.set_xticklabels(months)
ax.legend()
ax.grid(True, alpha=0.3)

# 保存图表到内存
chart_buffer = io.BytesIO()
plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
plt.close()
chart_buffer.seek(0)

# 添加图表到幻灯片
left = Inches(1)
top = Inches(1.5)
pic = slide.shapes.add_picture(chart_buffer, left, top, width=Inches(8), height=Inches(4.5))

# 创建数据页 - 财务数据
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "财务数据"

body_shape = slide.shapes.placeholders[1]
tf = body_shape.text_frame
tf.text = '收入情况:'
p = tf.add_paragraph()
p.text = '• 总收入: 850万元'
p = tf.add_paragraph()
p.text = '• 同比增长: 15.2%'
p = tf.add_paragraph()
p.text = '• 毛利率: 42.3%'

p = tf.add_paragraph()
p.text = '成本分析:'
p = tf.add_paragraph()
p.text = '• 总成本: 490万元'
p = tf.add_paragraph()
p.text = '• 人力成本: 45%'
p = tf.add_paragraph()
p.text = '• 营销费用: 28%'

# 创建总结页
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "总结与展望"

body_shape = slide.shapes.placeholders[1]
tf = body_shape.text_frame
tf.text = '核心成果:'
p = tf.add_paragraph()
p.text = '✓ 超额完成上半年销售目标'
p = tf.add_paragraph()
p.text = '✓ 市场占有率提升至18.5%'
p = tf.add_paragraph()
p.text = '✓ 客户满意度达到92%'

p = tf.add_paragraph()
p.text = '下一步计划:'
p = tf.add_paragraph()
p.text = '• 拓展新市场，目标增长20%'
p = tf.add_paragraph()
p.text = '• 优化供应链，降低运营成本'
p = tf.add_paragraph()
p.text = '• 加强人才培养，提升团队能力'

# --- 2. 保存到内存缓冲区 ---
buffer = io.BytesIO()
prs.save(buffer)
buffer.seek(0)

# --- 3. Base64 编码并打包为 JSON ---
data_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
result = {
    "type": "ppt",
    "title": f"季度业务汇报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx",
    "data_base64": data_base64
}

# --- 4. 打印最终的 JSON 对象 ---
print(json.dumps(result))
```

---

## 📝 复合报告生成（Word + Excel + PDF）

### ✅ 完整工作流示例
```python
import io
import base64
import json
import pandas as pd
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_comprehensive_report():
    """生成包含Word摘要、Excel详细数据和PDF报告的完整分析包"""
    
    # 创建示例数据
    data = {
        '指标': ['收入', '成本', '利润', '利润率', '增长率'],
        'Q1': [450, 280, 170, '37.8%', '12.5%'],
        'Q2': [520, 310, 210, '40.4%', '15.6%'],
        'Q3': [610, 350, 260, '42.6%', '23.8%'],
        'Q4': [580, 320, 260, '44.8%', '0%']
    }
    df = pd.DataFrame(data)
    
    # 1. 生成Word摘要报告
    doc = Document()
    doc.add_heading('季度分析摘要', 0)
    doc.add_paragraph(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    doc.add_paragraph('本报告基于2024年四个季度的财务数据，分析了公司的整体经营状况。')
    
    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    word_buffer.seek(0)
    
    # 2. 生成Excel详细数据
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='季度财务数据', index=False)
        
        # 添加计算表
        summary_df = pd.DataFrame({
            '年度指标': ['总收入', '总成本', '总利润', '平均利润率'],
            '数值': [df[['Q1','Q2','Q3','Q4']].sum().sum(), 
                    df[['Q1','Q2','Q3','Q4']].iloc[1].sum(),
                    df[['Q1','Q2','Q3','Q4']].iloc[2].sum(),
                    '41.4%']
        })
        summary_df.to_excel(writer, sheet_name='年度汇总', index=False)
    
    excel_buffer.seek(0)
    
    # 3. 生成PDF报告
    pdf_buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()
    story = [
        Paragraph('2024年度财务分析报告', styles['Title']),
        Spacer(1, 20),
        Paragraph('基于季度数据的深度分析', styles['Heading2']),
        Spacer(1, 15),
        Paragraph('报告总结了公司2024年度的经营表现，并对未来发展趋势进行了展望。', styles['Normal'])
    ]
    doc_pdf.build(story)
    pdf_buffer.seek(0)
    
    # 返回所有文件（实际使用时，一次只能返回一个文件）
    # 这里演示如何构建多个文件，实际使用时需要分别执行
    files_info = [
        {
            "type": "word",
            "title": "分析摘要.docx",
            "data_base64": base64.b64encode(word_buffer.getvalue()).decode('utf-8')
        },
        {
            "type": "excel", 
            "title": "详细数据.xlsx",
            "data_base64": base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
        },
        {
            "type": "pdf",
            "title": "完整报告.pdf",
            "data_base64": base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        }
    ]
    
    print("注意：一次只能返回一个文件，以下是三个文件的JSON示例：")
    for i, file_info in enumerate(files_info):
        print(f"\n文件{i+1} JSON:")
        print(json.dumps(file_info, indent=2))

# 使用示例
if __name__ == "__main__":
    generate_comprehensive_report()
```

---

## ⚠️ 重要注意事项

### ✅ 必须做的:
1. **单一输出**: 每个代码执行只能输出一个JSON对象（一个文件）
2. **Base64编码**: 必须使用`base64.b64encode().decode('utf-8')`进行编码
3. **文件名规范**: 文件名应包含时间戳，避免重复：`f"报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"`
4. **编码一致性**: 中文字符使用`ensure_ascii=False`参数（但在沙盒中会自动处理）

### ❌ 绝对禁止:
1. **禁止保存到磁盘**: 不要使用`doc.save('filename.docx')`或`wb.save('filename.xlsx')`
2. **禁止多次输出**: 不要在一次执行中生成多个文件
3. **禁止混合输出**: 不要在打印JSON后打印其他内容
4. **禁止路径访问**: 不要尝试访问除`/data`目录外的文件系统

### 🔧 最佳实践:
1. **使用内存缓冲区**: 始终使用`io.BytesIO()`在内存中操作文件
2. **及时释放资源**: 使用`buffer.seek(0)`重置指针
3. **包含时间戳**: 在文件名中添加时间戳，避免冲突
4. **测试代码**: 在生成复杂报告前，先测试图表生成和数据处理部分
5. **分步验证**: 对于复杂报告，可以先验证各部分功能再整合

### 📊 常见错误及解决方案:

| 错误类型 | 原因 | 解决方案 |
|---------|------|----------|
| JSON解析失败 | 打印了额外内容 | 确保只打印一个JSON字符串 |
| 文件损坏 | Base64编码错误 | 使用正确的`.decode('utf-8')` |
| 内存不足 | 文件太大 | 压缩图片，减少数据量 |
| 中文乱码 | 编码问题 | 确保使用UTF-8编码 |

---

## 🎯 快速参考表

| 文件类型 | 主要库 | 输出类型 | 备注 |
|---------|--------|----------|------|
| Word (.docx) | `python-docx` | `"type": "word"` | 支持表格、图片、样式 |
| Excel (.xlsx) | `openpyxl` + `pandas` | `"type": "excel"` | 支持多个sheet、格式 |
| PDF (.pdf) | `reportlab` | `"type": "pdf"` | 支持图表、表格、样式 |
| PowerPoint (.pptx) | `python-pptx` | `"type": "ppt"` | 支持幻灯片、图表 |

---

## 🔄 工作流总结

1. **准备数据**: 从`/data`目录读取或生成分析数据
2. **创建文档**: 使用相应库在内存中构建文档
3. **添加内容**: 插入文本、表格、图表、格式等
4. **保存到内存**: 使用`io.BytesIO()`保存文档
5. **Base64编码**: 将二进制数据编码为字符串
6. **构建JSON**: 创建包含类型、文件名和数据的字典
7. **输出结果**: 使用`print(json.dumps())`输出单个JSON对象

**记住**: 系统会自动处理JSON输出并提示用户下载文件！
