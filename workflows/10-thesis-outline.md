# 10-thesis-outline 论文大纲

输入：对应用户 Phase 确认 和有效证据。

输出：thesis/outline.md。

执行：默认五章：概述、分析、设计、实现、测试；明确每节证据映射，性能未测删除性能节。摘要最后撰写。对应用户 Phase 确认。

规则：[ thesis-content-rules ](../rules/thesis-content-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
