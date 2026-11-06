# Research Server Kit

Linux 科研环境和 Codex：默认 Sorux，模型 gpt-6-sol，推理强度 high。

## 使用

服务器需要 Ubuntu/Debian、sudo、Node.js 22+ 和 npm，并能访问 APT/PyPI/npm 软件源。

```bash
git clone https://github.com/Xueyx121/research-server-kit.git
cd research-server-kit
bash start.sh
```

第一次会安装 Python 科研依赖，提示补上 Sorux key 的最后一个字符，并安装 Codex CLI。之后直接运行 `bash start.sh`。首次安装耗时由服务器网络决定。

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

Python 包默认走清华镜像，Codex 包默认走 npm 镜像。可在启动时指定：

```bash
PIP_INDEX_URL=https://pypi.org/simple CODEX_NPM_REGISTRY=https://registry.npmjs.org bash start.sh
```

模型权重、数据集、GPU 驱动和 GPU 版 PyTorch 需按实际项目准备。第三方 API 的模型支持和现场可达性尚未实测。

参考：[Codex 官方 provider 配置](https://learn.chatgpt.com/docs/config-file/config-advanced#custom-model-providers)。
