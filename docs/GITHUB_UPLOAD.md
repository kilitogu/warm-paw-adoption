# 上传到 GitHub

本项目已经在本地完成提交：分支 `main`，共 4 个提交，尚未配置远端仓库。
下面按“网页建仓 + 命令行推送”的顺序操作，全程在 PowerShell 中执行。

> 本机已经安装 **Git Credential Manager**（`git credential-manager 2.7.3`），
> 首次推送会自动弹出浏览器登录授权，不需要手动创建 Token。
> 也已确认 `github.com:443` 可以正常访问。

---

## 第 1 步：在 GitHub 创建一个空仓库

1. 打开 <https://github.com/new> 并登录。
2. 填写：
   - **Repository name**：例如 `warm-paw`（只能用英文、数字、`-`、`_`）
   - **Description**：`暖爪 · 智能宠物领养平台（FastAPI + Vue3 + LangGraph）`
   - **Public / Private**：按需选择
3. **不要勾选** 以下三项：
   - Add a README file
   - Add .gitignore
   - Choose a license
   
   因为本地已经有这些文件，勾选会造成推送冲突。
4. 点击 **Create repository**，复制页面上的仓库地址，例如：
   `https://github.com/kilitogu/warm-paw.git`

---

## 第 2 步：把本地仓库和 GitHub 关联

```powershell
cd "D:\Python project\python-vue-agent"

$user = "你的GitHub用户名"
$repo = "warm-paw"

git remote add origin "https://github.com/$user/$repo.git"
git remote -v
```

`git remote -v` 应输出两行 `origin`（fetch / push）。

如果提示 `remote origin already exists`，说明之前配置过，改为：

```powershell
git remote set-url origin "https://github.com/$user/$repo.git"
```

---

## 第 3 步：推送

```powershell
git push -u origin main
```

- 第一次推送会弹出 **Git Credential Manager** 窗口。
- 点击 **Sign in with your browser**，在浏览器里登录 GitHub 并授权。
- 授权完成后回到终端，看到类似输出即成功：

```text
branch 'main' set up to track 'origin/main'.
```

---

## 第 4 步：确认上传成功

```powershell
git status
```

应显示：

```text
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

然后打开 `https://github.com/你的用户名/仓库名`：

- 能看到 4 个提交记录；
- README 能正常显示 6 张项目截图；
- 顶部 **Actions** 会自动运行 CI（后端单元测试 + 前端构建），第一次大约 1–3 分钟。

---

## 方法二：用 GitHub Desktop（不想敲命令）

1. 安装并登录 [GitHub Desktop](https://desktop.github.com/)。
2. 菜单 **File → Add local repository**，选择 `D:\Python project\python-vue-agent`。
3. 右上角点击 **Publish repository**。
4. 取消勾选 “Keep this code private”（如果要公开），点击 **Publish repository**。

它会自动创建远程仓库并推送，不需要再做第 1–3 步。

---

## 推送时要求输入密码怎么办

GitHub 已经不支持账号密码，只能用 **Personal Access Token（PAT）**：

1. 打开 <https://github.com/settings/tokens>；
2. **Generate new token (classic)**；
3. Note 填 `warm-paw`，Expiration 选 30 days；
4. 勾选 **repo** 权限；
5. 生成后复制 Token（只显示一次）；
6. 回到推送窗口：
   - Username：填 GitHub 用户名；
   - Password：粘贴 Token（不是账号密码）。

> 本机有 Git Credential Manager，正常情况下会直接走浏览器授权，不会要求密码。
> 如果之前保存过错误凭据：控制面板 → 凭据管理器 → Windows 凭据 →
> 删除所有 `git:https://github.com` 条目，再重新推送。

---

## 常见报错对照表

| 报错 | 原因 | 解决 |
|---|---|---|
| `remote origin already exists` | 已配置过远端 | `git remote set-url origin 新地址` |
| `Updates were rejected because the remote contains work` | 建仓时勾选了 README / license | `git pull --rebase origin main` 后重新 push；或删除远程仓库，重建空仓库 |
| `Authentication failed` | 凭据错误或过期 | 清理 Windows 凭据管理器中的 github 条目，重新 push |
| `Support for password authentication was removed` | 用了账号密码 | 改用 PAT，见上一节 |
| `error: src refspec main does not match any` | 本地没有提交或分支名不对 | `git log --oneline`、`git branch` 检查 |
| `ssh: connect to host github.com port 22: timed out` | SSH 22 端口被网络拦截 | 使用本指南的 HTTPS 方式 |
| 推送一直卡住 | 网络/代理问题 | 配置代理：`git config --global http.proxy http://127.0.0.1:7890` |
| `GH001: Large files detected` | 单个文件超过 100MB | 本项目最大文件是截图（几百 KB），不会触发 |

---

## 上传前的安全检查（本仓库已满足）

```powershell
# 确认 .env 没有被提交
git ls-files | Select-String -Pattern '\.env$'

# 确认没有依赖目录 / 日志 / 上传文件
git ls-files | Select-String -Pattern 'node_modules|\.venv|^.*logs/|uploads/'

# 确认仓库里没有真实密钥
git grep -n -E 'sk-[A-Za-z0-9]{16,}'
```

三条命令都应没有输出（`python-agent/.env.example` 只是占位示例）。

---

## 以后更新代码

```powershell
cd "D:\Python project\python-vue-agent"
git add -A
git commit -m "feat: 本次改了什么"
git push
```

---

## 如果仓库地址已经准备好

把仓库地址发给我，或在本机完成第 1 步后告诉我仓库名，
我可以直接帮你执行第 2、3 步并检查 CI 结果。
