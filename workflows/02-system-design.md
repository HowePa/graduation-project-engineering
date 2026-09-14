# 02-system-design 系统设计

输入：已确认需求。

输出：docs/03-system-design.md、图源。

执行：描述组件、权限、业务流程、页面与部署结构，设计与真实实现分开记录。

规则：[ diagram-rules ](../rules/diagram-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
