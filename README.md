# Research Server Kit

Linux 科研环境和 Codex：默认 Sorux，模型 gpt-6-sol，推理强度 high。

## 使用

服务器使用 Ubuntu 22.04+ / Debian 11+，有 root 或 sudo 权限，能访问软件源。下载仓库后只需运行一个脚本：

```bash
git clone https://github.com/Xueyx121/research-server-kit.git
cd research-server-kit
bash start.sh
```

脚本自动安装系统工具、Python 科研包、Node.js/npm 和 Codex CLI，然后默认启动 Sorux。**无需手动安装 Node.js 或逐个输入 pip/npm 命令。** 第一次会提示补上 Sorux key 的最后一个字符，以后直接运行 `bash start.sh`。

前一晚只安装环境、不启动 AI：

```bash
bash setup.sh
```

第二天运行 `bash start.sh`。重复运行会检查并复用已完成的安装；中途断网或安装失败后，重新运行同一个脚本即可。首次下载耗时由现场网络决定。

没有 Git 时，也可以在 GitHub 页面通过 **Code → Download ZIP** 下载并解压，然后在该文件夹中运行 `bash start.sh`。

切到另一个 API：

```bash
bash start.sh transformcat
```

第一次切换同样需要补上该 key 的末位。切回 Sorux：

```bash
bash start.sh
```

`api.partial.env` 中预填了两套删掉最后一个字符的 key。补全后只保存到被 Git 忽略的本地 `.env`，不打印完整 key。**只删一位不能保密，缺失位可被枚举；更稳妥的方式是改用新 key 并仅本地保存。**

## 配置与其他项目

两个 API 的地址和模型在 `.env.example`，安装后可编辑本地 `.env`。现有客户端或会话需要重启才能切换。不会自动向另一家 API 重试。

在其他项目中启动：

```bash
cd /path/to/project1
bash /path/to/research-server-kit/start.sh
# 或 bash /path/to/research-server-kit/start.sh transformcat
```

精简 Codex 配置见 `codex.config.toml`。启动器使用同样的设置，不会覆盖现有用户配置。已去掉本机项目路径、MCP、macOS 通知、桌面插件与登录令牌。

Python 包默认走清华镜像，Node.js 和 Codex 包优先走 npmmirror；后两者失败时尝试官方源。使用镜像下载不需要 VPN，但仍取决于现场网络。Node.js 安装在仓库的 `.tools/` 中，Python 包安装在 `.venv/` 中。

需要更换软件源时可指定：

```bash
PIP_INDEX_URL=https://pypi.org/simple CODEX_NPM_REGISTRY=https://registry.npmjs.org bash start.sh
```

模型权重、数据集、GPU 驱动和 GPU 版 PyTorch 需按实际项目准备。第三方 API 的模型支持和现场可达性尚未实测。

参考：[Codex 官方 provider 配置](https://learn.chatgpt.com/docs/config-file/config-advanced#custom-model-providers)。
