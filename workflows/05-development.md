# 05-development 系统开发

输入：Phase 1、Phase 2 已批准，接口契约与 ui-design.yaml。

输出：backend/、frontend/、docker-compose.yml。

执行：按基础工程、数据库、登录、权限、核心 CRUD、审核、统计、页面联调推进；每个模块与角色完成即测试。服务启动后用实际 API 验证，不以源码扫描替代。

规则：[ project-rules ](../rules/project-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
