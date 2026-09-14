# 03-database-design 数据库设计

输入：系统设计。

输出：database/schema.sql、init.sql、seed.sql、docs/04-database-design.md。

执行：设计 DDL 后用 inspect_database.py 提取字段、长度、主键、空值、默认值、外键、注释及索引。当前仅支持 Golden DDL 子集，拒绝不认识的结构；真实库比对另行执行。

规则：[ database-table-rules ](../rules/database-table-rules.md)。

验收：输出可读、与输入一致且来源可追溯；执行失败记录 failed，停止依赖本阶段的后续步骤。输入变化后重跑本阶段及受影响下游，保留历史日志。

用户交互与推进以 [Phase 层](phases/README.md) 为准；内部步骤完成不自动代表用户批准。
