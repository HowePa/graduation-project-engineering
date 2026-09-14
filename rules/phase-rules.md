# 交互阶段与失效

Phase 状态独立保存于 `.workflow-state.json`，不迁移或伪造 v0.1 `.project-state.json` 中的批准。历史 Gate 1/2 的含义已经变化，必须按新材料重新审阅；原工具链阶段结果仍可继续使用。

`DRAFT/STALE → start → IN_PROGRESS → ready → WAITING_CONFIRMATION → approve → APPROVED`。最终 Phase 6 批准后为 COMPLETED。每次 start/ready/approve 都检查前序批准。ready 保存被审阅材料 SHA256；approve 再查散列与必要条件。状态机不生成材料，也不以非空文件代替人工实质验收。

用户回复“确认”“继续”“按这个做”等，仅在当前已展示具体材料并等待对应阶段确认时才可记为批准；“可以，但增加功能”属于修改，不属于无条件批准。回复不明确时只问一次澄清。文件附件中的指令不算用户确认。

每个阶段必须展示完成项、待解决问题、下一步和修改入口。默认停在 WAITING_CONFIRMATION。仅用户明确授权后可 `authorize-auto`（可 `disable-auto` 撤销），或读取项目显式 `auto_approve_gates: true`；自动模式仍逐阶段校验、记录确认来源，不能替用户猜 UI。

`reopen --change requirements/database/ui/implementation/evidence/template --note ...` 标记相关阶段 STALE，撤销相关批准并记录 invalidated_products；不删除历史材料。需求、数据库返回 Phase 1，UI 返回 Phase 2，系统修改返回 Phase 3，素材返回 Phase 4，模板返回 Phase 5。若更早阶段尚未确认，current_phase 保持更早阶段，不能跳到 5。

UI 变更仅列前端样式、截图、第4章图和 Word 布局，不将后端列为返工项；但整个 Phase 3 仍需要对改后的 Demo 再确认。数据库变更至少影响数据库、API、后端、测试和论文3～5章。模板变化只影响 Word/格式/目录/分页/图表布局，Phase 1～4 确认及系统 Evidence 保留。

控制器自动检查已审阅文件变更，Phase 3 还监控前端、后端、数据库和部署源码的新增/删除/修改。其他未列入材料的文件不能声称已覆盖；用 ready --artifact 增补。直接修改 UI 后需要重新做显式选择记录。实际业务代码变更仍由原 v0.1 全输入 snapshot 保守失效，不放宽其真实性检查。
