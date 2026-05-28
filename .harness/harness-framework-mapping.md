# Harness Framework Mapping
# 本框架 × mattpocock/skills × GSD Redux 与 Anthropic 文章要点的对应关系

> 临时分析文档。参考来源：
> - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
> - https://github.com/multica-ai/andrej-karpathy-skills
> - https://github.com/mattpocock/skills (via Superpowers)
> - https://github.com/open-gsd/get-shit-done-redux

---

## Anthropic 文章核心问题

两个根本失败模式：

| # | 失败模式 | 文章描述 |
|---|---|---|
| 1 | **一次性实现（one-shot）** | Agent 试图一口气完成全部功能，跑出 context 导致半成品 |
| 2 | **提前宣布完成** | 看到部分进展就声称任务完成（= Fuzzy Done） |

文章解法：**Initializer Agent**（环境设定）+ **Coding Agent**（增量推进 + 结构化交接）

---

## 1. 环境初始化 / Initializer Agent

**文章要点：** `init.sh`、初始 git commit、`claude-progress.txt`（进度日志）

| 本框架 | 作用 |
|---|---|
| `/harness-audit` 检查 #7 | 检测 `init.sh` 是否存在且可执行 |
| `/setup-harness-skills` | 生成 `init.sh`、`.harness/STATE.md`、`.harness/config.json` |
| `/session-start` | 每次 session 开始读取 STATE.md（等同于 `claude-progress.txt`）并输出 briefing |

**GSD 对应：** `/gsd-new-project` → 生成 init 脚本和项目骨架

**何时用：** 新项目第一次启动，或跨会话恢复时。

---

## 2. 增量推进 / Coding Agent — 每个 session 交接

**文章要点：** 每个 session 结束留下结构化更新，保持"干净状态"（clean state = 可 merge 的代码）

| 本框架 | 作用 |
|---|---|
| `/context-handover` | 写 `.continue-here.md`（XML 结构）、更新 STATE.md、发 GitHub 进度评论 |
| `/session-start` | 读取 `.continue-here.md` 的 `<next_action>`，检测中断 session |

**GSD 对应：**

| GSD Skill | 对应 |
|---|---|
| `/gsd-execute-phase` | 原子提交 + 偏差处理 + checkpoint 协议（= coding agent 执行层） |
| `/gsd-verify-work` | 目标逆向验证（goal-backward，= clean state 检查） |

**何时用：** 接近 context 80% 时触发 `/context-handover`；下次 session 开头触发 `/session-start`。

---

## 3. Stop Hook / 防止提前宣布完成

**文章要点：** 必须有外部门控阻止 agent 凭感觉声称完成。

| 本框架 | 作用 |
|---|---|
| `/harness-audit` 检查 #1 | **永远是 Gap #1**：缺少 Stop hook → 输出完整 JSON 片段 |
| `/harness-guide` Phase 3 | 同样强制 Stop hook 为最高优先级推荐 |
| `universal-snippets.md` | Stop hook 内容：强制在宣布完成前 run lint+build、确认 observable 行为 |

**何时用：** 任何新项目初始化时。无 Stop hook 的项目，所有其他 gap 都不重要。

---

## 4. PostToolUse Hook / 增量验证

**文章要点：** 每次写文件后立即验证，不等到 session 末尾。

| 本框架 | 作用 |
|---|---|
| `/harness-audit` 检查 #2 | 检测 PostToolUse hook（独立于 Stop hook）|
| `universal-snippets.md` | PostToolUse → `npx eslint --fix "$CLAUDE_FILE_PATH"` |

**GSD 对应：** `/gsd-executor` 通过 hook 在每次文件写入后自动验证

---

## 5. Planner → Generator → QA 三层架构

**文章要点：** 单 agent 能力有限；Planner（规格）+ Builder（实现）+ QA（验证）效果显著。

| 本框架 | 对应层 |
|---|---|
| `/to-prd` | **Planner**：将对话转化为带技术约束和验收标准的 PRD |
| `/to-issues` | **Planner**：将 PRD 分解为 vertical-slice issues，带 AFK/HITL 置信标签 |
| `/triage` | **Planner 前置**：状态机过滤无效任务 |
| `/grill-with-docs` | **Planner 深化**：用 domain docs 和 ADR 压测计划，更新 CONTEXT.md |

**GSD 对应：**

| GSD Skill | 对应层 | 何时用 |
|---|---|---|
| `/gsd-discuss-phase` | Planner — 需求讨论，生成 CONTEXT.md | 功能设计阶段 |
| `/gsd-plan-phase` | Planner — 生成 PLAN.md，任务分解 | CONTEXT.md 确认后 |
| `/gsd-execute-phase` | Builder — 原子执行，偏差上报 | PLAN.md 批准后 |
| `/gsd-verify-work` | QA — 目标逆向验证 | 执行完成前 |
| `/gsd-code-review` | QA — 代码审查，分严重等级 | merge 前 |
| `/gsd-debug` | QA 修复 — 科学方法 debug | 测试失败时 |

---

## 6. CLAUDE.md / Instruction File 质量

**文章要点：** 简洁、可信、不超过工作 context 上限。

| 本框架 | 作用 |
|---|---|
| `/harness-audit` 检查 #3 | 检测存在性、200 行上限、AGENTS.md 等价性 |
| `universal-snippets.md` 的 CLAUDE.md 模板 | = **Karpathy 4 原则 + 第 5 节 Harness Discipline** |

### CLAUDE.md 是否真的被修改？

**修改条件：** 必须运行 `/setup-harness-skills`（非 `/harness-audit`，audit 只读不写）

**流程：** 输出草稿 → **等待用户确认** → 写入文件

**写入内容结构：**
```
Karpathy 4 原则
  1. Think Before Coding
  2. Simplicity First
  3. Surgical Changes
  4. Goal-Driven Execution
+
本框架新增 第 5 节: Harness Discipline
  - session 状态文档化
  - one active task at a time
  - observable 退出条件（非感觉）
  - 外部状态真相来源（issue tracker / handoff doc）
  - 不凭置信声称完成
```

`/harness-audit` **不会**修改任何文件——只输出 paste-ready 片段供用户手动应用。

---

## 7. mattpocock/skills (Superpowers) 对应关系

| Skill | 文章对应要点 | 何时用 |
|---|---|---|
| `brainstorming` | 实现前探索意图（= Think Before Coding）| 开始任何新功能前，**必须先用** |
| `systematic-debugging` | 科学方法 debug，避免 Confidence Exit | 遇到任何 bug 或测试失败时 |
| `writing-plans` | 代码前写计划（Planning ≠ Done）| 多步骤任务开始前 |
| `subagent-driven-development` | 独立任务并行执行，隔离 context | 有多个不相互依赖的实现任务时 |

---

## 8. 反模式检测（本框架命名，文章隐含）

| 反模式 | 文章对应 | 本框架检测方法 |
|---|---|---|
| **Fuzzy Done** | 看到进度就宣布完成 | `/harness-guide` Phase 2：STATE.md idle 后无验证提交 |
| **Proxy Signal** | CI 通过 ≠ 功能正确 | `/harness-audit` 检查 #5：CI 只有 build 无 lint |
| **Confidence Exit** | 凭自信跳过验证 | Stop hook 强制要求验证步骤 |
| **Planning=Done** | 写了计划就认为完成 | `/harness-guide`：git log 检查 plan commit 后是否有 implement commit |
| **Context Drift** | 任务范围在 session 中漂移 | `/triage` + `/to-issues` 预先锁定 scope |
| **Batch Questioning** | 一次问多个问题 | 所有 skill 强制 one-question-at-a-time |

---

## 使用时序

```
新项目启动
  → /harness-audit          ← 检测 gaps，输出优先清单
  → /setup-harness-skills   ← 一次性配置：labels、STATE.md、CLAUDE.md
  → /session-start          ← 每次 session 开头

需求阶段
  → brainstorming           ← 探索意图（Superpowers）
  → /grill-with-docs        ← 压测计划 vs domain docs
  → /to-prd → /to-issues    ← PRD + issue 分解

执行阶段
  → writing-plans           ← 代码前写计划（Superpowers）
  → /gsd-execute-phase      ← 原子执行
  → systematic-debugging    ← bug 时（Superpowers）
  → /gsd-code-review        ← merge 前

Session 结束
  → /context-handover       ← 保存状态（≥70% context 时）
  → /compact               ← 用户手动执行

持续治理
  → /harness-guide          ← 定期检查 harness 健康度
  → /harness-audit          ← 新成员加入或发现问题时
```
