# ComfyUI Seed Finder

独立、无依赖的前端扩展。仅请求原生 `GET /history`，不提交任务，不修改队列。

## 当前任务运行中：立即使用，无需重启

1. 在当前 ComfyUI 网页打开浏览器开发者工具 → Sources → Snippets，新建片段。
2. 将本目录 `js/seed-finder.js` 的完整内容粘贴进去并运行（也可在 Console 执行）。
3. 展开右下角 **Seed Finder**，输入完整 PNG 文件名，例如 `ComfyUI_00001_.png`，点击查询。

无需部署文件到服务器或刷新页面。脚本只驻留当前页面；刷新后重新执行即可。
查询保留 ComfyUI 页面的 URL 路径前缀；特殊代理路径可显式指定已确认的 history 地址：

```js
ComfySeedFinder.mount(() => fetch('/实际代理前缀/history', {
  method: 'GET', credentials: 'same-origin', cache: 'no-store'
}));
```

## 正式安装（不要在当前生图期间重启）

先确认实际 ComfyUI 安装目录，将整个 `comfyui_seed_finder` 目录复制到其 `custom_nodes/` 下。
这是新增扩展，ComfyUI 需要在之后计划内正常启动时发现 `WEB_DIRECTORY`。
本次不执行服务器重启。扩展加载后，网页右下角显示同一个 Seed Finder，使用 ComfyUI 原生 `api.fetchApi` 处理路径前缀。
没有额外 Python 依赖、数据库、HTTP 路由、Workbench 页面或后端服务。

## 数据含义与限制

- 精确、区分大小写地匹配 `outputs[*].images[*].filename`；不输入文件夹路径。同名文件返回全部 Prompt ID，并显示输出节点、子目录和类型。
- 读取任务 `prompt[2]` 的执行 API 图，从对应输出节点沿输入连线向上遍历；不读取当前画布、`widgets_values` 或 `extra_pnginfo.workflow`。
- JSON 原始文本中的整数字面量在解析前转换为十进制字符串，保留 uint64 Seed 的每一位，显示与复制均使用该字符串。
- 标准 KSampler / KSamplerAdvanced 显示所在节点的 seed/noise_seed、Steps、CFG、Sampler。RandomNoise、BasicScheduler、CFGGuider、KSamplerSelect 等拆分节点分别列出所属参数和节点 ID；不合并不同阶段的采样参数。
- 连线输入不等于已记录的运行输出。任意计算节点、动态展开节点或自定义采样器的实际数值若未存入 history，会显示未解析或缺少参数；不会猜值或使用控件缓存。复制任务参数可保留这些标注。
- 尚未完成、服务历史已清理或服务重启后丢失的任务可能无法查询。history 不证明磁盘上同名文件未被覆盖。
- 剪贴板不可用时提供选中文本手动复制。查询是手动触发，没有后台轮询。

## 定向测试

在仓库根目录运行（UI 测试使用仓库现有 frontend 的 jsdom）：

```sh
node --test tests/seed_finder.test.cjs
```

扩展结构依据 [ComfyUI JavaScript 扩展文档](https://docs.comfy.org/custom-nodes/js/javascript_overview)，history 结构依据 [原生执行队列](https://github.com/comfyanonymous/ComfyUI/blob/master/execution.py)。
