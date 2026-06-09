# 创建 Skill 的 Skill

## 问题

Skill 如此好用，正是我所需要的，但是我自己不会写啊！一个 Skill 里面包含：

- `SKILL.md` — 核心说明文件
- `scripts/` — 脚本
- `references/` — 指令/参考文档
- 等等……

这可如何是好~

---

## 解决方案：让 Skill 自己生成 Skill

在资料包里找到 `iwen-skill-creator.zip`，之后解压到当前的 skills 目录下，即可使用了！

### 温馨提示

`iwen-skill-creator.zip` 的来源是官方认证的 skill `skill-creator`，它可以把跑通的工作流转化为独一无二的 skill。我们进行了简单的修改，让他更适合大部分人使用！

> 官方 skill-creator 的核心思路：你先在 Claude Code 中完整跑通一个工作流（比如"生成图片"），然后让 skill-creator 观察你的操作过程，自动提炼成可复用的 SKILL.md + 脚本 + 资源文件。