# Research Server Kit

快速准备一台 Ubuntu/Debian Linux 服务器，用于短期科研项目。脚本安装常见编译工具和 Python 数据分析环境；API 凭证通过服务器上的 `.env` 文件配置。

## 服务器要求

- Ubuntu 22.04/24.04 或 Debian 12，具备 sudo 权限
- 能访问 APT 软件源和一个可用的 PyPI 源
- 建议至少 4 核 CPU、16 GB 内存；具体项目和数据集可能需要更多资源
- GPU 任务需先确认 NVIDIA 驱动/CUDA 与 PyTorch 版本兼容；bootstrap 不会改动 GPU 驱动

脚本默认使用清华 PyPI 镜像。若该镜像不可达，可在运行时覆盖 `PIP_INDEX_URL`，例如使用服务器网络允许的官方源或组织提供的镜像。镜像仅解决 Python 包下载；它不提供模型文件、API 服务或 VPN 能力。

## 安装

```bash
git clone https://github.com/Xueyx121/research-server-kit.git
cd research-server-kit
bash bootstrap.sh
source .venv/bin/activate
python scripts/check_env.py
```

安装脚本会调用 `apt-get`，需要 root 或 sudo。首次安装后如果需要新增系统包或 Python 包，可分别使用 apt 和 `pip install`；记录变更到项目自己的依赖文件。

## API 配置

脚本首次运行时会从 `.env.example` 创建权限为 `600` 的 `.env`。默认 provider 是 Sorux；配置中只保留服务器程序需要的 provider、endpoint、model 和 API key，不包含本机 Codex 的项目路径、MCP、通知或登录态配置。

```dotenv
LLM_PROVIDER=sorux

SORUX_API_KEY=在服务器本地填写
SORUX_BASE_URL=https://ai.soruxgpt.com/v1
SORUX_MODEL=gpt-6-sol

TRANSFORMCAT_API_KEY=在服务器本地填写
TRANSFORMCAT_BASE_URL=https://www.transformcat.cn/
TRANSFORMCAT_MODEL=gpt-6-sol
```

把可用 key 填入服务器的 `.env`。两套配置互相独立，改 provider 不会覆盖另一套 key。快速切换：

```bash
python scripts/use_provider.py sorux
python scripts/use_provider.py transformcat
```

项目代码可通过公共 Responses API client 使用当前选中的 provider：

```python
from scripts.llm_config import create_client, get_provider_config

config = get_provider_config()
client = create_client(config)
response = client.responses.create(
    model=config.model,
    input="Reply with OK",
    store=False,
    reasoning={"effort": "high"},
)
print(response.output_text)
```

这两个地址按当前 Codex provider 配置预填。若服务商文档要求不同的 API base URL 或 model 名，在 `.env` 中改对应 provider 的变量。该 helper 使用 OpenAI Python SDK 的 Responses API；实际调用还要求服务商兼容该接口。脚本不会自动向另一个 provider 重试，以免网络错误时悄悄把请求或费用切到其他服务。

Codex 的 `auth_mode=chatgpt`、`auth.json` 和其中的 OAuth access/refresh token 属于本机登录态，不是服务器可复用的 API 配置；不要上传或复制到 Linux 服务器。不要把 API key 写进仓库、命令行参数、Notebook 输出或 shell history。

## Linux 上使用 Codex CLI

在服务器已有 Node.js/npm 时，可将 CLI 安装在仓库本地目录：

```bash
npm install --prefix "$PWD/.tools" @openai/codex --registry=https://registry.npmjs.org
# 若官方 npm 源不可达，可按活动规则改用组织认可的 npm 镜像。
.tools/bin/codex --version
```

`.tools/` 已忽略。需要服务器兼容的 Node.js 版本及 Linux 运行环境；bootstrap 仅安装 Python 环境，不包含 Node.js。请在部署前确认 npm 的包与原生依赖都可从现场网络下载。

本地 `.env` 填好对应 key 后，使用启动器，不需要浏览器登录或复制 auth.json：

```bash
python scripts/run_codex.py                  # 默认 Sorux
python scripts/use_provider.py transformcat
python scripts/run_codex.py                  # 切换后新会话使用 Transformcat
python scripts/use_provider.py sorux         # 恢复默认
```

启动器在当前工作目录启动 Codex，因此可用于其他项目：

```bash
cd /path/to/project1
/path/to/research-server-kit/.venv/bin/python /path/to/research-server-kit/scripts/run_codex.py
```

切换后要重新启动进程；现有 Python client/已运行会话不会自动切换。进程环境中显式设置的同名变量优先于 `.env`。`codex.config.toml` 是精简后的参考配置；启动器用 CLI 覆盖传入相同设置，不改写用户级配置。若手动复制参考配置，需自行 export 其中 env_key 指定的环境变量，Codex 不会自行读取本仓库的 `.env`。

保留模型 `gpt-6-sol`、`high` 推理、workspace-write 沙箱、never 审批和网络访问。去掉 macOS 通知、项目路径及全盘信任、MCP/桌面插件、marketplace 本机路径、Windows 设置及 OAuth 登录态。provider 用独立 `env_key` 认证，因此不再设置 `requires_openai_auth=true`。`disable_response_storage=true` 保留为客户端设置，Python 示例明确传 `store=False`；第三方服务端是否遵守不由此仓库保证。

配置方式参考 [OpenAI 官方高级配置文档](https://learn.chatgpt.com/docs/config-file/config-advanced#custom-model-providers)。服务商模型可用性、计费和现场网络连通性尚未实测。

## 模型与数据

大模型权重、数据集和检查点不包含在仓库中。提前确认许可证、体积和服务器可访问的下载源，并在有网络时预下载到共享磁盘或经授权的缓存。Hugging Face 下载如需镜像，可在 `.env` 设置组织认可且可访问的 `HF_ENDPOINT`；镜像不保证可用，也不会解决 API endpoint 的连通性。

GPU 版 PyTorch 与驱动、CUDA/ROCm 版本相关，需根据服务器实际环境从 PyTorch 官方安装选择器或组织镜像单独安装，避免安装与驱动不匹配的 wheel。

## 两小时部署清单

1. 确认系统版本、CPU/内存/磁盘、GPU 型号和驱动、网络出口、可用镜像及 sudo 权限。
2. 克隆仓库并运行 `bash bootstrap.sh`；失败时先查看最后一条 apt/pip 错误，按允许的镜像覆盖 `PIP_INDEX_URL` 后重试。
3. 激活 `.venv` 并运行 `python scripts/check_env.py`，确认包、Python、GPU 驱动状态。
4. 配置 `.env`；运行 `python scripts/check_env.py` 确认选中 provider、model 和 key 是否已配置，再对目标 API 做最小调用。
5. 下载/校验数据与模型，记录路径、版本、校验和与许可证。
6. 为四个项目分别建立目录或 Git 分支，固定依赖、保存启动命令与实验日志，并检查可用磁盘和结果备份位置。

## API 网络检查

`check_env.py` 只检查本机依赖和凭证是否存在，不发送密钥或联网调用。正式实验开始前，应从服务器连接目标 provider 的文档 endpoint，用 SDK 做一次最小请求并确认返回模型可用；不要在多人共享终端中打印 Authorization header。

## 仓库安全

- `.env`、数据、模型、日志和实验输出已加入 `.gitignore`。
- 如果密钥曾被提交，即使随后删除也应立即在服务商后台撤销并重新生成。
- 不要将未经许可的模型、数据集或第三方凭证上传到 GitHub.
