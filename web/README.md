# 连连看 - 网页版部署说明

## 方式一：GitHub Pages（推荐，免费获得网址）

### 1. 创建 GitHub 仓库

1. 在 [GitHub](https://github.com) 登录，点击 **New repository**
2. 仓库名例如：`lianliankan`
3. 选择 **Public**，创建仓库

### 2. 上传文件

将 `web` 文件夹下的 **全部内容** 上传到仓库根目录，结构如下：

```
你的仓库根目录/
├── index.html      ← web/index.html
└── images/         ← web/images/ 整个文件夹（含 8 张 PNG）
    ├── 008CDAAD-6C3C-4EAE-8046-62A322C3D3C3.png
    └── ... (其他 7 张 PNG 图片)
```

### 3. 开启 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. 在 **Source** 中选择 **Deploy from a branch**
3. **Branch** 选 `main`，文件夹选 `/ (root)`
4. 点击 **Save**

### 4. 获取网址

几分钟后访问：

```
https://你的用户名.github.io/lianliankan/
```

例如：`https://junia.github.io/lianliankan/`

---

## 方式二：本地预览

在项目目录下运行一个本地服务器：

```bash
cd /Users/junia/lianliankan/web
python3 -m http.server 8080
```

浏览器打开：`http://localhost:8080`

---

## 方式三：Vercel / Netlify

1. 将 `web` 文件夹内容推送到 GitHub
2. 在 [Vercel](https://vercel.com) 或 [Netlify](https://netlify.com) 导入该仓库
3. 构建完成后会得到一个线上网址
