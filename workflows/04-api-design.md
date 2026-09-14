# 04-api-design API 设计

输入：设计和 DDL。

输出：docs/05-api-design.md、evidence/api.json。

执行：接口说明包括参数、响应、角色。开发后扫描实际 Spring 注解，未识别表达式应报错，不能推测动态路径。对应用户 Phase 确认。

规则：[ project-rules ](../rules/project-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
