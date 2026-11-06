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

脚本首次运行时会从 `.env.example` 创建权限为 `600` 的 `.env`。编辑服务器上的 `.env`，填入服务商提供的密钥和（如适用）兼容 API 地址：

```dotenv
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://服务商文档中的兼容接口地址/v1
LLM_MODEL=服务商支持的模型名
```

接入 OpenAI 兼容服务时，使用该服务商文档给出的 endpoint、模型名和认证格式。未填写 `OPENAI_BASE_URL` 时，OpenAI Python SDK 使用默认官方 endpoint；网络无法访问该 endpoint 时，请使用活动组织提供的合规服务地址或在本地/联网环境完成任务。脚本不会绕过网络限制。

不要把真实密钥写进仓库、命令行参数、Notebook 输出或 shell history。可由项目代码使用 `python-dotenv` 读取 `.env`；部署到共享机器时按组织要求管理和轮换密钥。

## 模型与数据

大模型权重、数据集和检查点不包含在仓库中。提前确认许可证、体积和服务器可访问的下载源，并在有网络时预下载到共享磁盘或经授权的缓存。Hugging Face 下载如需镜像，可在 `.env` 设置组织认可且可访问的 `HF_ENDPOINT`；镜像不保证可用，也不会解决 API endpoint 的连通性。

GPU 版 PyTorch 与驱动、CUDA/ROCm 版本相关，需根据服务器实际环境从 PyTorch 官方安装选择器或组织镜像单独安装，避免安装与驱动不匹配的 wheel。

## 两小时部署清单

1. 确认系统版本、CPU/内存/磁盘、GPU 型号和驱动、网络出口、可用镜像及 sudo 权限。
2. 克隆仓库并运行 `bash bootstrap.sh`；失败时先查看最后一条 apt/pip 错误，按允许的镜像覆盖 `PIP_INDEX_URL` 后重试。
3. 激活 `.venv` 并运行 `python scripts/check_env.py`，确认包、Python、GPU 驱动状态。
4. 配置 `.env`；只对组织批准的 API 地址运行最小调用，确认认证和模型名。
5. 下载/校验数据与模型，记录路径、版本、校验和与许可证。
6. 为四个项目分别建立目录或 Git 分支，固定依赖、保存启动命令与实验日志，并检查可用磁盘和结果备份位置。

## API 网络检查

`check_env.py` 只检查本机依赖和凭证是否存在，不发送密钥或联网调用。正式实验开始前，应从服务器连接目标 provider 的文档 endpoint，用 SDK 做一次最小请求并确认返回模型可用；不要在多人共享终端中打印 Authorization header。

## 仓库安全

- `.env`、数据、模型、日志和实验输出已加入 `.gitignore`。
- 如果密钥曾被提交，即使随后删除也应立即在服务商后台撤销并重新生成。
- 不要将未经许可的模型、数据集或第三方凭证上传到 GitHub.
