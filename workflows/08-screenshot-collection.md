# 08-screenshot-collection 截图采集

输入：对应用户 Phase 确认、真实运行的 Web 页面。

输出：artifacts/screenshots/、evidence/screenshots.json。

执行：Playwright 使用 1440×900；按角色真实登录，操作核心页面，等待业务标识与网络完成；保存路由、角色、功能、时间、图片散列，检查页面错误及数据。禁止绘制截图替代真实浏览器截图。

规则：[ screenshot-rules ](../rules/screenshot-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
