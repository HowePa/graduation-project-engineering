# 11-thesis-writing 按章撰写

输入：对应用户 Phase 确认 和当前 evidence。

输出：thesis/chapters/*.md、thesis/thesis.md、thesis/claims.json。

执行：按第1至5章、结论、摘要、Abstract 顺序逐章写与检查。第3章数据库表直接读 database.json，第4章引用真实截图，第5章仅使用真实结果。

规则：[ thesis-content-rules ](../rules/thesis-content-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
