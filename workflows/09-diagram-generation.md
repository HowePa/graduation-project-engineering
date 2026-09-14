# 09-diagram-generation 设计图

输入：有效 evidence。

输出：artifacts/diagrams/source/、artifacts/diagrams/、evidence/diagrams.json。

执行：根据实际组件和关系生成图源，再渲染；至少用例、模块、架构、业务流程、核心时序、ER、实体图。人工检查布局和业务真实性。对应用户 Phase 确认。

规则：[ diagram-rules ](../rules/diagram-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
