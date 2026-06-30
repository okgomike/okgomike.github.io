# 第二分公司 Hugo 网站基础包

第二分公司（五金工具方向）的完整 Hugo + GitHub Pages 静态网站基础包，支持 CSV 批量导入产品、自动分类、多级导航、响应式设计和 SEO/GEO 优化。

## 技术栈

- **Hugo** 静态网站生成器（extended 版本）
- **GitHub Pages** 免费托管
- **GitHub Actions** 自动部署
- **Python 3** CSV 转 Markdown 脚本

## 快速开始

### 1. 安装 Hugo

```bash
# macOS
brew install hugo

# Windows (Scoop)
scoop install hugo-extended

# Linux
sudo apt install hugo
```

### 2. 本地预览

```bash
cd second-branch-hugo
hugo server -D
```

打开 http://localhost:1313 预览。

### 3. 修改公司信息

编辑 `data/company.yaml`：

```yaml
contact:
  phone: "+86-579-8522-8888"
  whatsapp: "+8613800138000"
  email: "sales@yourbrand.com"
```

### 4. 修改导航类目

编辑 `data/categories.yaml`，一级类目和二级子类目都在这里维护：

```yaml
categories:
  - name: "Fasteners & Hardware"
    slug: "fasteners-hardware"
    children:
      - name: "Bolts & Nuts"
        slug: "bolts-nuts"
```

**注意**：修改 `data/categories.yaml` 后，导航菜单会自动更新，无需改动模板。

### 5. 批量上传产品

准备 CSV 文件（参考 `scripts/products_example.csv`），然后执行：

```bash
python scripts/csv_to_hugo.py products.csv content/products/
```

脚本会自动：
- 将每行 CSV 转为 Hugo Markdown 文件
- 提取 frontmatter（MOQ、价格、规格等）
- 按 `category_level1` 和 `category_level2` 自动归类
- **自动创建缺失的类目索引页**（`_index.md`）

#### CSV 必填列

| 列名 | 说明 |
|------|------|
| `title` | 产品标题 |
| `category_level1` | 一级类目（如：Fasteners & Hardware）|
| `category_level2` | 二级子类目（如：Bolts & Nuts）|

#### CSV 可选列

`slug`, `summary`, `description`, `moq`, `price_range`, `material`, `standard`, `grade`, `size_range`, `surface`, `certification`, `packing`, `sample`, `customization`, `mixed_order`, `image`, `gallery`, `specifications`, `faq`, `weight`, `carton_qty`, `carton_size`, `gw_nw`, `tags`, `internal_note`

### 6. 部署到 GitHub Pages

1. 在 GitHub 创建新仓库（如 `second-branch-hardware`）
2. 推送代码到 `main` 分支
3. 打开仓库 **Settings → Pages**
4. Source 选择 **GitHub Actions**
5. `.github/workflows/hugo.yaml` 会自动构建并发布

## 文件结构

```
second-branch-hugo/
├── config.yaml                 # Hugo 主配置
├── data/
│   ├── company.yaml            # 公司联系信息（电话、邮箱、WhatsApp）
│   ├── categories.yaml         # 导航类目结构（一级 + 二级）
│   └── footer.yaml             # 页脚链接配置
├── layouts/
│   ├── _default/
│   │   ├── baseof.html         # 基础模板（头部 + 页脚）
│   │   ├── list.html           # 类目列表页
│   │   └── single.html         # 通用单页
│   ├── partials/
│   │   ├── head.html           # SEO 头部（OG, Twitter, Schema）
│   │   ├── header.html         # 导航菜单（多级下拉 + 移动端）
│   │   └── footer.html         # 页脚（联系信息 + 链接）
│   ├── products/
│   │   └── single.html         # 产品详情页（批发信息 + 询价按钮）
│   └── index.html              # 首页模板
├── assets/css/main.css         # 响应式样式（电脑 + 手机）
├── static/js/main.js           # 移动端菜单交互
├── scripts/
│   └── csv_to_hugo.py          # CSV 批量转 Markdown
├── content/
│   ├── _index.md               # 首页内容
│   └── products/               # 产品 Markdown 文件
└── .github/workflows/hugo.yaml # 自动部署
```

## 公共导航菜单

导航菜单由 `data/categories.yaml` 驱动，模板自动生成：

- **Products** 下拉：6 个一级类目，每个展开显示 6 个二级子类目
- **Services** 下拉：5 个服务页面
- **Buying Guides / About / Contact**：独立链接

顶部固定栏显示 WhatsApp、邮箱、电话，点击直接跳转。

## 响应式适配

- **电脑端（>900px）**：完整导航、 mega menu 下拉、双栏布局
- **平板（600-900px）**：汉堡菜单、单列布局、页脚两列
- **手机（<600px）**：侧边抽屉导航、双列产品网格、精简顶部栏

## SEO & GEO

每个页面自动包含：

- `<title>`、`<meta description>`、canonical URL
- Open Graph（Facebook）和 Twitter Card
- Schema.org 结构化数据（Product / WebPage / WebSite）
- 面包屑导航
- 图片 alt 标签和 lazy loading

在 `static/llms.txt` 放置站点摘要，供 AI 工具读取：

```
# YourBrand Hardware
> A Yiwu-based B2B online wholesale showroom...
## Core Categories
- Fasteners & Hardware
...
```

## 页脚

页脚从 `data/footer.yaml` 自动生成 4 列链接：

1. **Products**：6 个一级类目
2. **Services**：5 个服务
3. **Support**：购买指南、FAQ、物流等
4. **Company**：关于我们、联系、隐私条款

左侧显示公司全称、描述、WhatsApp / 邮箱 / 电话 / 地址。

## 日常维护速查

| 要修改什么 | 修改哪里 |
|---|---|
| 公司名、电话、邮箱、WhatsApp | `data/company.yaml` |
| 导航类目和子类目 | `data/categories.yaml` |
| 页脚链接 | `data/footer.yaml` |
| 首页内容 | `content/_index.md` + `layouts/index.html` |
| 产品内容 | `content/products/*.md`（由 CSV 脚本生成）|
| 产品页样式 | `layouts/products/single.html` |
| 全站样式 | `assets/css/main.css` |
| 网站标题和域名 | `config.yaml` |
| GitHub Pages 自动部署 | `.github/workflows/hugo.yaml` |

## 注意事项

1. **不要直接修改 `content/categories/` 下的 `_index.md`**，它们由 CSV 脚本自动维护
2. **图片路径**：CSV 中的 `image` 和 `gallery` 列使用 `/images/xxx.jpg`，实际图片放在 `static/images/`
3. **baseURL**：部署前务必修改 `config.yaml` 中的 `baseURL` 为你的 GitHub Pages 地址
