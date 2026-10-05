# 工具

本目录自带的程序按下面的写法调用，不需要读源码；加 `--help` 打印同样的说明。

宿主有自己的浏览器工具时，查看页面、走查流程照常用。要交出下面这几样标准证据时，优先用这里的截图工具：它开一个独立的临时浏览器，不碰用户自己浏览器里的数据。本机缺 Node 22，或者没有 Chrome、Chromium、Edge 时，退回宿主工具，交出同样的几样东西。不为截图另写 Playwright 或浏览器协议脚本。

## 截图和录屏

```text
node <skill>/scripts/shoot.mjs <页面地址或 HTML 文件> [选项]
```

本地文件会用一个只监听本机的临时服务器打开。地址里带 `?` 或 `&` 时加引号，例如 `"http://127.0.0.1:3000/?state=done"`；更省事的是用 `--states`。同名文件会直接覆盖，不需要额外参数。

| 要什么 | 加上 |
| --- | --- |
| 每个状态各一张，再拼成并排图 | `--states idle,running,done,error --sheet` |
| 同时要遮掉全部文字的版本 | 再加 `--mask` |
| 200% 截图 | `--zoom 2` |
| 手机和桌面各一套 | `--size 390x844,1280x900`（默认只有 390x844） |
| 整页长图 | `--full` |
| 截图前先操作几步 | `--steps "click .open; wait 300"` |
| 主操作录屏，外加开始、中间、结束三帧 | `--record --steps "drag .handle 0 -80; wait 400; click .start" --hold 1500` |

`--steps` 里的动作用分号隔开：`click 选择器`、`hover 选择器`、`drag 选择器 横向位移 纵向位移`、`type 选择器 文字`、`key 按键`、`scroll 纵向位移`、`wait 毫秒`。

结果写进 `--out` 指定的目录，默认是 `./shots`：每个状态一张 `<状态>.png`，遮字版是 `<状态>-masked.png`，并排图是 `sheet.png` 和 `sheet-masked.png`，录屏是 `record.mp4` 和 `motion-start/mid/end.jpg`。每张图都会检查控制台错误、横向溢出和没加载出来的图片，命令最后一行给出结论，明细在 `report.json`。录屏需要本机装了 ffmpeg，没有时只留三帧。

检查报出接口 401、404 这类和画面无关的错误时（例如访客状态下的登录接口），在交付说明里记一行就行，不为了让检查通过去改登录、接口这类业务代码。

截图前先自己看一眼结果：默认状态是不是已经加载完，遮字版有没有把图形也一起盖掉。证据有错先重截，再交给评审。

## 写可操作的小样

小样要能用地址参数直接打开每个状态，例如 `?state=done`，截图工具和评审都靠它。一个组件或一个页面只写一个文件，不要每个状态复制一份。

颜色、字号、间距、圆角先定成十来个 CSS 变量，后面一律引用变量；同一个组件的样式用原生 CSS 嵌套写在一起。不引入 Tailwind 或 Sass 这类需要构建的工具。

状态和交互用 Alpine.js 写在 HTML 属性上，不手写一长段切换显示的脚本：

1. 复制到任务目录：`cp <skill>/assets/vendor/alpine.min.js <任务目录>/vendor/`
2. 页面里引用：`<script defer src="vendor/alpine.min.js"></script>`
3. 状态集中放在一个 `x-data` 里，初始状态读地址参数：

```html
<main x-data="{ state: new URLSearchParams(location.search).get('state') || 'idle', amount: 40 }">
  <p x-show="state === 'done'">做好了</p>
  <input type="range" min="20" max="80" x-model.number="amount">
  <button @click="state = 'running'">开始</button>
</main>
```

放进对比页时，在 manifest 里给这个候选加 `"interactive": true`。生成器会把任务目录里引用到的 CSS 和 JS 文件内联进对比页，不用手动合并。

存量项目里照用项目自己的技术栈，不引入 Alpine.js。
