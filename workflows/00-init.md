# 00-init 项目初始化

输入：project.yaml、现有源码和配置。

输出： .project-state.json。

执行：校验配置；检查源码、前后端、数据库、Docker、测试、设计文档、论文和截图是否存在。文件存在仅记 present，不能记 complete。

规则：[ project-rules ](../rules/project-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
