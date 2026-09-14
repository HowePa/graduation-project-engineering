package example;
public class DomainChecks {
    interface Action { void run(); }
    static void rejects(Class<? extends Throwable> type, Action action) {
        try { action.run(); } catch (Throwable e) {
            if (type.isInstance(e)) return;
            throw new AssertionError("wrong exception", e);
        }
        throw new AssertionError("expected " + type.getName());
    }
    public static void main(String[] args) {
        Achievement a = new Achievement(1, "成果");
        switch (args[0]) {
            case "normal_review": a.submit(1); a.review("科研秘书", true); if (a.getStatus() != Achievement.Status.APPROVED) throw new AssertionError(); break;
            case "reject_review": a.submit(1); a.review("科研秘书", false); if (a.getStatus() != Achievement.Status.REJECTED) throw new AssertionError(); break;
            case "blank_title": rejects(IllegalArgumentException.class, () -> new Achievement(1, "  ")); break;
            case "title_boundary": new Achievement(1, "字".repeat(200)); rejects(IllegalArgumentException.class, () -> new Achievement(1, "字".repeat(201))); break;
            case "foreign_update": rejects(SecurityException.class, () -> a.update(2, "修改")); break;
            case "foreign_submit": rejects(SecurityException.class, () -> a.submit(2)); break;
            case "teacher_review": a.submit(1); rejects(SecurityException.class, () -> a.review("教师", true)); break;
            case "draft_review": rejects(IllegalStateException.class, () -> a.review("科研秘书", true)); break;
            case "repeat_submit": a.submit(1); rejects(IllegalStateException.class, () -> a.submit(1)); break;
            case "submitted_update": a.submit(1); rejects(IllegalStateException.class, () -> a.update(1, "修改")); break;
            default: throw new AssertionError("unknown case");
        }
    }
}
