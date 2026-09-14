package example;

public final class Achievement {
    public enum Status { DRAFT, SUBMITTED, APPROVED, REJECTED }
    private final long ownerId;
    private String title;
    private Status status = Status.DRAFT;
    public Achievement(long ownerId, String title) {
        if (ownerId <= 0) throw new IllegalArgumentException("owner must be positive");
        this.ownerId = ownerId;
        setTitle(title);
    }
    private void setTitle(String value) {
        if (value == null || value.trim().isEmpty() || value.length() > 200)
            throw new IllegalArgumentException("title must contain 1 to 200 characters");
        this.title = value.trim();
    }
    private void requireOwner(long actor) {
        if (actor != ownerId) throw new SecurityException("owner only");
    }
    public void update(long actor, String value) {
        requireOwner(actor);
        if (status != Status.DRAFT) throw new IllegalStateException("draft only");
        setTitle(value);
    }
    public void submit(long actor) {
        requireOwner(actor);
        if (status != Status.DRAFT) throw new IllegalStateException("draft only");
        status = Status.SUBMITTED;
    }
    public void review(String role, boolean approved) {
        if (!"科研秘书".equals(role)) throw new SecurityException("secretary only");
        if (status != Status.SUBMITTED) throw new IllegalStateException("submitted only");
        status = approved ? Status.APPROVED : Status.REJECTED;
    }
    public Status getStatus() { return status; }
    public String getTitle() { return title; }
}
