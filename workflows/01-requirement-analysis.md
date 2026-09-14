# 01-requirement-analysis 需求分析

输入：项目配置与课题资料。

输出：docs/01-project-overview.md、docs/02-requirement-analysis.md、evidence/requirements.json。

执行：明确角色、功能、核心业务、业务规则、非功能要求及边界；需求记录为 planned。对应用户 Phase 确认。

规则：[ project-rules ](../rules/project-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
