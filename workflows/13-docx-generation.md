# 13-docx-generation Word 生成

输入：通过内容检查的 Markdown、学校模板和格式配置。

输出：thesis/毕业论文.docx、渲染预览。

执行：按模板与格式规则生成分节、目录域、图表、页码。必须渲染并逐页检查，目录更新与跨页续表不能仅靠 XML 检测声称通过。当前学校模板未提供时，禁止宣称符合学校模板。

规则：[ thesis-format-rules ](../rules/thesis-format-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
