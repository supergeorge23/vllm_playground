# 修复 Hugging Face 访问权限问题

## 问题诊断

错误信息：
```
GatedRepoError: 403 Client Error
Cannot access gated repo for url https://huggingface.co/meta-llama/Meta-Llama-3-8B
Access to model meta-llama/Meta-Llama-3-8B is restricted and you are not in the authorized list.
```

## 解决步骤

### 步骤 1: 申请 LLaMA-3 访问权限

1. 访问：https://huggingface.co/meta-llama/Meta-Llama-3-8B
2. 点击 "Request access" 或 "Agree and access repository"
3. 填写申请表单（通常需要几分钟到几小时审批）

### 步骤 2: 获取 Hugging Face Token

1. 访问：https://huggingface.co/settings/tokens
2. 创建一个新的 token（如果有的话）
3. 选择 "Read" 权限即可
4. 复制 token（只显示一次，请保存好）

### 步骤 3: 在实例上登录 Hugging Face

```bash
# SSH到实例
ssh -i ~/.ssh/MacBookPro.pem ubuntu@150.136.52.154

# 进入项目目录
cd ~/projects/vllm_playground
source .venv/bin/activate

# 登录Hugging Face
huggingface-cli login

# 粘贴你的token，按Enter
```

### 步骤 4: 验证访问权限

```bash
# 测试是否可以访问模型
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='meta-llama/Meta-Llama-3-8B', filename='config.json')"
```

如果成功，说明权限已配置好。

### 步骤 5: 重新运行基准测试

```bash
python scripts/workflow.py --phase 1
```

## 替代方案：使用其他模型（如果无法获得LLaMA-3权限）

如果暂时无法获得LLaMA-3访问权限，可以修改配置使用其他模型：

### 选项1: 使用公开的模型

编辑 `configs/baseline.yaml`：
```yaml
model:
  name: "mistralai/Mistral-7B-v0.1"  # 或其他公开模型
  dtype: "bfloat16"
  max_model_len: 16384
```

### 选项2: 使用本地模型（如果已下载）

```yaml
model:
  name: "/path/to/local/model"  # 本地路径
  dtype: "bfloat16"
  max_model_len: 16384
```

## 检查清单

- [ ] 已在HF网站申请LLaMA-3访问权限
- [ ] 已获得访问批准
- [ ] 已创建HF token
- [ ] 已在实例上运行 `huggingface-cli login`
- [ ] 已验证可以访问模型
- [ ] 可以成功运行基准测试

## 常见问题

### Q: 申请后多久能获得访问权限？
A: 通常几分钟到几小时，取决于Meta的审批速度。

### Q: Token在哪里找到？
A: https://huggingface.co/settings/tokens

### Q: 登录后还是403错误？
A: 确保：
1. 申请已获得批准
2. 使用正确的账号登录
3. Token有read权限

### Q: 可以使用其他模型吗？
A: 可以，修改 `configs/baseline.yaml` 中的 `model.name` 即可。
