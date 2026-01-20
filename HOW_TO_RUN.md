# 🚀 如何运行这个项目

## 第一步: 安装依赖

打开命令行(CMD或PowerShell),进入项目目录:

```bash
cd "E:\AI Staff\AI_Hire_Dashboard"
```

安装所需的Python包:

```bash
pip install -r requirements.txt
```

## 第二步: 启动应用

运行以下命令启动Streamlit应用:

```bash
streamlit run recruitment_dashboard.py
```

## 第三步: 访问应用

浏览器会自动打开,如果没有自动打开,请手动访问:

```
http://localhost:8501
```

## 🎉 完成!

现在你可以:
- 在左侧边栏筛选数据
- 在不同Tab页查看各维度指标
- 导出数据到CSV文件

---

## 📖 更多帮助

- **快速开始指南**: 查看 QUICKSTART.md
- **详细文档**: 查看 README.md
- **项目总结**: 查看 PROJECT_SUMMARY.md

---

## ❓ 遇到问题?

### 问题1: 提示"模块未找到"
**解决**: 重新运行 `pip install -r requirements.txt`

### 问题2: 端口被占用
**解决**: 使用以下命令指定其他端口
```bash
streamlit run recruitment_dashboard.py --server.port 8502
```

### 问题3: 浏览器无法打开
**解决**: 手动在浏览器输入 `http://localhost:8501`

---

祝使用愉快! 🎊
