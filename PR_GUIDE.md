# Pull Request 创建指南

## 当前状态

✅ 已创建分支：`feature/result-analysis`  
✅ 已推送到GitHub：`origin/feature/result-analysis`  
✅ main分支已重置为与origin/main同步

## 创建PR的步骤

### 方法1：通过GitHub网页界面（推荐）

1. 访问GitHub提供的链接：
   ```
   https://github.com/supergeorge23/vllm_playground/pull/new/feature/result-analysis
   ```

2. 填写PR信息：
   - **Title**: `Add result analysis script for benchmark results`
   - **Description**: 
     ```markdown
     ## 功能描述
     添加了结果分析脚本 `scripts/analyze_results.py`，用于分析基准测试结果。
     
     ## 主要功能
     - 读取JSONL结果文件并按上下文长度分组统计
     - 计算关键指标（平均值、最小值、最大值、中位数、标准差）
     - 生成详细的统计表格（TTFT、吞吐量、延迟、GPU内存）
     - 支持导出为CSV格式
     
     ## 相关文件
     - `scripts/analyze_results.py` - 新增的分析脚本
     - `README.md` - 更新项目结构说明
     - `USAGE.md` - 添加使用说明
     
     ## 测试
     - ✅ 脚本可以正常导入和运行
     - ✅ 帮助信息正常显示
     ```

3. 点击 "Create pull request"

### 方法2：使用GitHub CLI（如果已安装）

```bash
gh pr create --title "Add result analysis script for benchmark results" \
  --body "添加了结果分析脚本，用于分析基准测试结果并生成统计摘要" \
  --base main \
  --head feature/result-analysis
```

## 后续操作

### 查看PR状态
```bash
# 切换回feature分支继续开发
git checkout feature/result-analysis

# 查看PR信息（如果使用gh CLI）
gh pr view
```

### 如果需要更新PR
```bash
# 在feature分支上继续开发
git checkout feature/result-analysis

# 提交新更改
git add .
git commit -m "Update: ..."

# 推送到远程（会自动更新PR）
git push
```

### PR合并后清理本地分支
```bash
# 切换回main
git checkout main

# 拉取最新代码
git pull origin main

# 删除本地feature分支
git branch -d feature/result-analysis
```

## 分支命名规范建议

- `feature/` - 新功能
- `fix/` - Bug修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关

## 注意事项

⚠️ **不要直接push到main分支**  
✅ 始终通过PR流程合并代码  
✅ PR应该包含清晰的描述和测试说明
