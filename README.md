# Research Server Kit

快速准备一台 Ubuntu/Debian Linux 服务器，用于短期科研项目。脚本安装常见编译工具和 Python 数据分析环境；API 凭证通过服务器上的 .env 文件配置。

## 服务器要求

- Ubuntu 22.04/24.04 或 Debian 12，具备 sudo 权限
- 能访问 APT 软件源和一个可用的 PyPI 源
- 建议至少 4 核 CPU、16 GB 内存；具体项目和数据集可能需要更多资源
- GPU 任务需先确认 NVIDIA 驱动/CUDA 与 PyTorch 版本兼容；bootstrap 不会改动 GPU 驱动

脚本默认使用清华 PyPI 镜像。若该镜像不可达，可运行时覆盖 PIP_INDEX_URL，使用服务器允许的源。镜像只解决 Python 包下载，不提供模型文件或 API 服务。

## 安装

```bash
git clone https://github.com/Xueyx121/research-server-kit.git
cd research-server-kit
bash bootstrap.sh
source .venv/bin/activate
python scripts/check_env.py
```

## API 配置

首次运行会从 .env.example 创建权限为 600 的 .env。默认 provider 为 Sorux；两套配置独立，真实 key 只填写在服务器本地 .env：

```dotenv
LLM_PROVIDER=sorux
SORUX_API_KEY=在服务器本地填写
SORUX_BASE_URL=https://ai.soruxgpt.com/v1
SORUX_MODEL=gpt-6-sol
TRANSFORMCAT_API_KEY=在服务器本地填写
TRANSFORMCAT_BASE_URL=https://www.transformcat.cn/
TRANSFORMCAT_MODEL=gpt-6-sol
```

快速切换当前 provider，不会覆盖另一套 key：

```bash
python scripts/use_provider.py sorux
python scripts/use_provider.py transformcat
```

项目代码可用 scripts.llm_config 创建兼容 Responses API 的客户端：

```python
from scripts.llm_config import create_client, get_provider_config
config = get_provider_config()
client = create_client(config)
response = client.responses.create(model=config.model, input="Reply with OK")
print(response.output_text)
```

两个 endpoint 根据你提供的 Codex provider 配置预填；模型名称和服务商对 Responses API 的兼容性请以服务商文档为准。请求失败时不会自动切换 provider，以免请求或费用被意外转移。

Codex 的 auth_mode=chatgpt 和 auth.json 中的 OAuth token 属于本机登录态，不是服务器 API key。你刚才贴出的 API key 和登录 token 已暴露，请尽快撤销/轮换。

## 模型与数据

模型权重、数据集和检查点不包含在仓库。提前确认许可证、体积和可访问下载源，并预下载到授权缓存。GPU 版 PyTorch 要按服务器驱动和 CUDA/ROCm 版本选取兼容 wheel；bootstrap 不改 GPU 驱动。

## 两小时部署清单

1. 确认系统、资源、GPU 驱动、网络出口、可用镜像及 sudo 权限。
2. 克隆仓库并运行 bash bootstrap.sh；必要时设置允许使用的 PIP_INDEX_URL。
3. 激活 .venv 并运行 python scripts/check_env.py。
4. 在 .env 填 API key，确认目标 provider 和 model 可用。
5. 下载并校验数据/模型，记录路径、版本、校验和与许可证。
6. 为四个项目分别建目录，固定依赖、保存启动命令与日志，并确认结果备份位置。

## 仓库安全

- .env、数据、模型、日志和实验输出已加入 .gitignore。
- 若 key 曾被提交或公开粘贴，立即撤销并重新生成；只删除文本不能使旧 key 失效。
- 不要上传未经许可的模型、数据集或第三方凭证。
