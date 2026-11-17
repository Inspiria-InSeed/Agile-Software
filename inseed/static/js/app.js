(() => {
  "use strict";

  const API = "/api/v1";
  const statuses = [
    { key: "BACKLOG", label: "Backlog", style: "backlog" },
    { key: "TO_DO", label: "To do", style: "todo" },
    { key: "IN_PROGRESS", label: "In progress", style: "progress" },
    { key: "DONE", label: "Done", style: "done" },
  ];
  const priorities = {
    CRITICAL: "Critical",
    HIGH: "High",
    MEDIUM: "Medium",
    LOW: "Low",
  };
  const state = {
    user: null,
    users: [],
    projects: [],
    activeProject: null,
    issues: [],
    view: "board",
    filterView: "board",
    query: "",
    assignee: "",
    priority: "",
    activeIssue: null,
    toastTimer: null,
  };

  const byId = (id) => document.getElementById(id);
  const esc = (value) =>
    String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[char]);
  const initials = (name) =>
    String(name || "?").trim().split(/\s+/).slice(0, 2).map((part) => part[0] || "").join("").toUpperCase();
  const displayName = (user) => user?.full_name || user?.email || "Teammate";
  const userById = (id) => state.users.find((user) => user.id === id);

  async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers,
      credentials: "same-origin",
    });
    if (response.status === 204) return null;
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401 && state.user) {
        state.user = null;
        showAuth();
      }
      const message = typeof body?.detail === "string" ? body.detail : "Something went wrong. Please try again.";
      throw new Error(message);
    }
    return body;
  }

  function showToast(message, isError = false) {
    const toast = byId("toast");
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");
    window.clearTimeout(state.toastTimer);
    state.toastTimer = window.setTimeout(() => toast.classList.remove("show"), 3200);
  }

  function showAuth(register = false) {
    byId("workspace").hidden = true;
    byId("auth-screen").hidden = false;
    byId("auth-name").hidden = !register;
    byId("auth-name-label").hidden = !register;
    byId("auth-name").required = register;
    byId("auth-password").autocomplete = register ? "new-password" : "current-password";
    byId("auth-eyebrow").textContent = register ? "LET'S GET STARTED" : "WELCOME BACK";
    byId("auth-title").textContent = register ? "Create your account" : "Sign in to Inseed";
    byId("auth-copy").textContent = register
      ? "Set up your workspace and start moving work forward."
      : "Your team’s work is right where you left it.";
    byId("auth-submit").innerHTML = `${register ? "Create account" : "Sign in"} <span aria-hidden="true">→</span>`;
    byId("auth-switch-copy").textContent = register ? "Already have an account?" : "New to Inseed?";
    byId("auth-switch").textContent = register ? "Sign in" : "Create an account";
    byId("auth-error").textContent = "";
    byId("auth-screen").dataset.mode = register ? "register" : "login";
    byId("auth-email").value = "";
    byId("auth-password").value = "";
    byId("auth-name").value = "";
  }

  async function showWorkspace(user) {
    state.user = user;
    byId("auth-screen").hidden = true;
    byId("workspace").hidden = false;
    const name = displayName(user);
    byId("profile-name").textContent = name;
    byId("profile-email").textContent = user.email || "";
    byId("user-avatar").textContent = initials(name);
    byId("top-avatar").textContent = initials(name);
    try {
      const [users, projects] = await Promise.all([api("/users/"), api("/projects/")]);
      state.users = users;
      state.projects = projects;
      state.activeProject = projects[0] || null;
      populateAssignees();
      renderProjects();
      await loadProjectIssues();
      render();
    } catch (error) {
      showToast(error.message, true);
    }
  }

  async function loadProjectIssues() {
    if (!state.activeProject) {
      state.issues = [];
      render();
      return;
    }
    state.issues = await api(`/projects/${state.activeProject.id}/issues`);
    render();
  }

  function renderProjects() {
    const list = byId("project-list");
    list.innerHTML = state.projects.map((project) => `
      <button class="project-item ${project.id === state.activeProject?.id ? "selected" : ""}" type="button" data-project-id="${project.id}">
        <span class="project-dot"></span><span class="project-name">${esc(project.key)}</span></button>`).join("");
    const project = state.activeProject;
    if (!project) return;
    byId("breadcrumbs").innerHTML = `<span>Projects</span><span class="crumb-slash">/</span><strong>${esc(project.key)}</strong>`;
    byId("project-overline").innerHTML = `<span class="project-dot"></span> ${esc(project.key)} <span class="dot-separator">·</span> ${esc(project.name).toUpperCase()}`;
    document.title = `${project.name} · Inseed`;
  }

  async function selectProject(projectId) {
    const selected = state.projects.find((project) => project.id === Number(projectId));
    if (!selected) return;
    state.activeProject = selected;
    state.filterView = "board";
    document.querySelectorAll(".side-nav .nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === "board"));
    renderProjects();
    try {
      await loadProjectIssues();
    } catch (error) {
      showToast(error.message, true);
    }
  }

  function populateAssignees() {
    const filter = byId("assignee-filter");
    const assignee = byId("issue-assignee");
    filter.innerHTML = '<option value="">All assignees</option>';
    assignee.innerHTML = '<option value="">Unassigned</option>';
    for (const user of state.users) {
      const label = displayName(user);
      filter.insertAdjacentHTML("beforeend", `<option value="${user.id}">${esc(label)}</option>`);
      assignee.insertAdjacentHTML("beforeend", `<option value="${user.id}">${esc(label)}</option>`);
    }
    byId("team-avatars").innerHTML = state.users.slice(0, 4)
      .map((user) => `<span class="user-avatar" title="${esc(displayName(user))}">${esc(initials(displayName(user)))}</span>`)
      .join("");
  }

  function filteredIssues() {
    const query = state.query.trim().toLowerCase();
    return state.issues.filter((issue) => {
      const assigned = !state.assignee || String(issue.assignee_id || "") === state.assignee;
      const priority = !state.priority || issue.priority === state.priority;
      const mine = state.filterView !== "my-work" || issue.assignee_id === state.user?.id || issue.reporter_id === state.user?.id;
      const search = !query || `${issue.title} ${issue.description || ""} ${state.activeProject?.key || "INSEED"}-${issue.id}`.toLowerCase().includes(query);
      return assigned && priority && mine && search;
    });
  }

  function render() {
    renderStats();
    renderBoard();
    renderList();
    byId("my-work-count").textContent = state.issues.filter(
      (issue) => issue.assignee_id === state.user?.id || issue.reporter_id === state.user?.id,
    ).length;
  }

  function renderStats() {
    const total = state.issues.length;
    const progress = state.issues.filter((issue) => issue.status === "IN_PROGRESS").length;
    const done = state.issues.filter((issue) => issue.status === "DONE").length;
    const ratio = total ? Math.round((done / total) * 100) : 0;
    byId("stat-total").textContent = total;
    byId("stat-progress").textContent = progress;
    byId("stat-done").textContent = done;
    byId("stat-health").textContent = !total ? "Just started" : ratio === 100 ? "All wrapped up!" : `${ratio}% complete`;
    byId("health-bar").style.width = `${ratio}%`;
  }

  function issueCard(issue) {
    const assignee = userById(issue.assignee_id);
    const name = assignee ? displayName(assignee) : "Unassigned";
    const status = statuses.find((item) => item.key === issue.status);
    const projectKey = state.activeProject?.key || "INSEED";
    return `<article class="issue-card" tabindex="0" role="button" draggable="true" data-issue-id="${issue.id}" aria-label="Open ${esc(issue.title)}">
      <div class="issue-key"><span>${esc(projectKey)}-${issue.id}</span><span class="issue-type" title="Task">◇</span></div>
      <h3 class="issue-title">${esc(issue.title)}</h3>
      ${issue.description ? `<p class="issue-description">${esc(issue.description)}</p>` : ""}
      <div class="issue-card-bottom"><span class="priority priority-${esc((issue.priority || "medium").toLowerCase())}">${esc(priorities[issue.priority] || "Medium")}</span>
      <span class="issue-assignee ${assignee ? "" : "unassigned"}" title="${esc(name)}">${assignee ? esc(initials(name)) : "＋"}</span></div>
      <span class="sr-only">${esc(status?.label || "Backlog")}</span></article>`;
  }

  function renderBoard() {
    const issues = filteredIssues();
    const board = byId("board");
    board.innerHTML = statuses.map((status) => {
      const matching = issues.filter((issue) => issue.status === status.key);
      return `<section class="board-column" data-status="${status.key}">
        <div class="column-heading"><span class="status-dot ${status.style}"></span><h2>${status.label}</h2><span class="column-count">${matching.length}</span>
          <button type="button" class="icon-button column-add" data-create-status="${status.key}" aria-label="Create ${status.label} issue">＋</button></div>
        <div class="issue-list">${matching.map(issueCard).join("")}</div></section>`;
    }).join("");
    const isEmpty = state.issues.length === 0;
    board.hidden = isEmpty || state.view !== "board";
    byId("empty-state").hidden = !isEmpty;
  }

  function renderList() {
    const view = byId("list-view");
    const issues = filteredIssues();
    view.hidden = state.view !== "list" || !state.issues.length;
    if (view.hidden) return;
    view.innerHTML = `<div class="list-row list-header"><span>Issue</span><span>Status</span><span>Priority</span><span>Assignee</span></div>${issues.map((issue) => {
      const assigned = userById(issue.assignee_id);
      const status = statuses.find((item) => item.key === issue.status);
      const projectKey = state.activeProject?.key || "INSEED";
      return `<div class="list-row" role="button" tabindex="0" data-issue-id="${issue.id}">
        <span class="list-issue-title">${esc(projectKey)}-${issue.id} &nbsp; ${esc(issue.title)}</span>
        <span class="list-status">${esc(status?.label || "Backlog")}</span>
        <span class="priority priority-${esc((issue.priority || "medium").toLowerCase())}">${esc(priorities[issue.priority] || "Medium")}</span>
        <span>${esc(assigned ? displayName(assigned) : "Unassigned")}</span></div>`;
    }).join("") || '<div class="list-row"><span>No issues match these filters.</span></div>'}`;
  }

  function openIssueModal(issue = null, status = "TO_DO") {
    state.activeIssue = issue;
    byId("issue-form").reset();
    byId("issue-id").value = issue?.id || "";
    byId("issue-title").value = issue?.title || "";
    byId("issue-description").value = issue?.description || "";
    byId("issue-status").value = issue?.status || status;
    byId("issue-priority").value = issue?.priority || "MEDIUM";
    byId("issue-assignee").value = issue?.assignee_id || "";
    byId("modal-heading").textContent = issue ? "Issue details" : "Create an issue";
    const projectKey = state.activeProject?.key || "INSEED";
    byId("issue-key").textContent = issue ? `${projectKey}-${issue.id} · TASK` : `${projectKey} · NEW ISSUE`;
    byId("save-issue-button").textContent = issue ? "Save changes" : "Create issue";
    byId("delete-issue-button").hidden = !issue;
    byId("comments-section").hidden = !issue;
    byId("comment-body").value = "";
    byId("issue-modal").hidden = false;
    document.body.style.overflow = "hidden";
    if (issue) loadComments(issue.id);
    window.setTimeout(() => byId("issue-title").focus(), 0);
  }

  function closeIssueModal() {
    byId("issue-modal").hidden = true;
    document.body.style.overflow = "";
    state.activeIssue = null;
  }

  function openProjectModal() {
    byId("project-form").reset();
    delete byId("project-key").dataset.edited;
    byId("project-modal").hidden = false;
    document.body.style.overflow = "hidden";
    byId("project-name").focus();
  }

  function closeProjectModal() {
    byId("project-modal").hidden = true;
    document.body.style.overflow = "";
  }

  async function createProject(event) {
    event.preventDefault();
    const button = byId("save-project-button");
    button.disabled = true;
    try {
      const project = await api("/projects/", {
        method: "POST",
        body: JSON.stringify({
          name: byId("project-name").value.trim(),
          key: byId("project-key").value.trim().toUpperCase(),
          description: byId("project-description").value.trim() || null,
        }),
      });
      state.projects.push(project);
      state.activeProject = project;
      state.issues = [];
      state.filterView = "board";
      renderProjects();
      render();
      closeProjectModal();
      showToast(`${project.name} is ready.`);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      button.disabled = false;
    }
  }

  async function loadComments(issueId) {
    const list = byId("comment-list");
    list.innerHTML = '<p class="muted">Loading activity…</p>';
    try {
      const comments = await api(`/issues/${issueId}/comments`);
      byId("comment-count").textContent = `${comments.length} ${comments.length === 1 ? "comment" : "comments"}`;
      list.innerHTML = comments.map((comment) => `<article class="comment">
        <span class="user-avatar">${esc(initials(comment.author_name))}</span>
        <div class="comment-content"><div class="comment-meta"><strong>${esc(comment.author_name)}</strong><time>${esc(formatDate(comment.created_at))}</time></div>
        <p class="comment-body">${esc(comment.body)}</p></div></article>`).join("") || '<p class="muted">No updates yet. Start the conversation.</p>';
    } catch (error) {
      list.innerHTML = "";
      showToast(error.message, true);
    }
  }

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(date);
  }

  async function saveIssue(event) {
    event.preventDefault();
    const id = byId("issue-id").value;
    const assignee = byId("issue-assignee").value;
    const payload = {
      title: byId("issue-title").value.trim(),
      description: byId("issue-description").value.trim() || null,
      status: byId("issue-status").value,
      priority: byId("issue-priority").value,
      assignee_id: assignee ? Number(assignee) : null,
    };
    const button = byId("save-issue-button");
    button.disabled = true;
    try {
      const result = await api(id ? `/issues/${id}` : `/projects/${state.activeProject.id}/issues`, {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      if (id) {
        state.issues = state.issues.map((issue) => issue.id === result.id ? result : issue);
        showToast("Issue updated.");
      } else {
        state.issues.unshift(result);
        showToast("Issue created. Nice work!");
      }
      closeIssueModal();
      render();
    } catch (error) {
      showToast(error.message, true);
    } finally {
      button.disabled = false;
    }
  }

  async function deleteIssue() {
    const issue = state.activeIssue;
    if (!issue || !window.confirm(`Delete ${state.activeProject?.key || "INSEED"}-${issue.id}? This cannot be undone.`)) return;
    try {
      await api(`/issues/${issue.id}`, { method: "DELETE" });
      state.issues = state.issues.filter((item) => item.id !== issue.id);
      closeIssueModal();
      render();
      showToast("Issue deleted.");
    } catch (error) {
      showToast(error.message, true);
    }
  }

  async function addComment() {
    const issue = state.activeIssue;
    const body = byId("comment-body").value.trim();
    if (!issue || !body) return;
    byId("comment-submit").disabled = true;
    try {
      await api(`/issues/${issue.id}/comments`, { method: "POST", body: JSON.stringify({ body }) });
      byId("comment-body").value = "";
      await loadComments(issue.id);
      showToast("Comment added.");
    } catch (error) {
      showToast(error.message, true);
    } finally {
      byId("comment-submit").disabled = false;
    }
  }

  async function moveIssue(issueId, status) {
    const issue = state.issues.find((item) => item.id === Number(issueId));
    if (!issue || issue.status === status) return;
    const oldStatus = issue.status;
    issue.status = status;
    render();
    try {
      const result = await api(`/issues/${issue.id}`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      state.issues = state.issues.map((item) => item.id === result.id ? result : item);
      render();
      showToast(`Moved to ${statuses.find((item) => item.key === status)?.label || status}.`);
    } catch (error) {
      issue.status = oldStatus;
      render();
      showToast(error.message, true);
    }
  }

  async function signOut() {
    try {
      await api("/users/logout", { method: "POST" });
    } catch (error) {
      showToast(error.message, true);
    }
    state.user = null;
    state.issues = [];
    showAuth();
  }

  async function handleAuth(event) {
    event.preventDefault();
    const register = byId("auth-screen").dataset.mode === "register";
    const button = byId("auth-submit");
    const error = byId("auth-error");
    error.textContent = "";
    button.disabled = true;
    try {
      if (register) {
        await api("/users/", {
          method: "POST",
          body: JSON.stringify({
            full_name: byId("auth-name").value.trim(),
            email: byId("auth-email").value.trim(),
            password: byId("auth-password").value,
          }),
        });
      }
      const user = await api("/users/login/session", {
        method: "POST",
        body: JSON.stringify({
          email: byId("auth-email").value.trim(),
          password: byId("auth-password").value,
        }),
      });
      await showWorkspace(user);
    } catch (err) {
      error.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  }

  function setView(view) {
    state.view = view === "list" ? "list" : "board";
    document.querySelectorAll(".view-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.view === state.view));
    render();
  }

  function bindEvents() {
    byId("auth-form").addEventListener("submit", handleAuth);
    byId("auth-switch").addEventListener("click", () => {
      showAuth(byId("auth-screen").dataset.mode !== "register");
    });
    byId("create-issue-button").addEventListener("click", () => openIssueModal());
    byId("empty-create-button").addEventListener("click", () => openIssueModal());
    byId("issue-form").addEventListener("submit", saveIssue);
    byId("project-form").addEventListener("submit", createProject);
    byId("add-project-button").addEventListener("click", openProjectModal);
    byId("delete-issue-button").addEventListener("click", deleteIssue);
    byId("comment-submit").addEventListener("click", addComment);
    document.querySelectorAll(".close-modal").forEach((button) => button.addEventListener("click", closeIssueModal));
    document.querySelectorAll(".project-close").forEach((button) => button.addEventListener("click", closeProjectModal));
    byId("issue-modal").addEventListener("click", (event) => {
      if (event.target === byId("issue-modal")) closeIssueModal();
    });
    byId("project-modal").addEventListener("click", (event) => {
      if (event.target === byId("project-modal")) closeProjectModal();
    });
    byId("project-list").addEventListener("click", (event) => {
      const item = event.target.closest("[data-project-id]");
      if (item) selectProject(item.dataset.projectId);
    });
    byId("board").addEventListener("click", (event) => {
      const createButton = event.target.closest("[data-create-status]");
      if (createButton) return openIssueModal(null, createButton.dataset.createStatus);
      const card = event.target.closest("[data-issue-id]");
      if (card) openIssueModal(state.issues.find((issue) => issue.id === Number(card.dataset.issueId)));
    });
    byId("board").addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const card = event.target.closest("[data-issue-id]");
      if (card) {
        event.preventDefault();
        openIssueModal(state.issues.find((issue) => issue.id === Number(card.dataset.issueId)));
      }
    });
    byId("list-view").addEventListener("click", (event) => {
      const row = event.target.closest("[data-issue-id]");
      if (row) openIssueModal(state.issues.find((issue) => issue.id === Number(row.dataset.issueId)));
    });
    byId("list-view").addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const row = event.target.closest("[data-issue-id]");
      if (row) openIssueModal(state.issues.find((issue) => issue.id === Number(row.dataset.issueId)));
    });
    byId("board").addEventListener("dragstart", (event) => {
      const card = event.target.closest(".issue-card");
      if (!card) return;
      event.dataTransfer.setData("text/plain", card.dataset.issueId);
      event.dataTransfer.effectAllowed = "move";
      card.classList.add("dragging");
    });
    byId("board").addEventListener("dragend", (event) => event.target.closest(".issue-card")?.classList.remove("dragging"));
    byId("board").addEventListener("dragover", (event) => {
      const column = event.target.closest(".board-column");
      if (!column) return;
      event.preventDefault();
      column.classList.add("drop-target");
    });
    byId("board").addEventListener("dragleave", (event) => event.target.closest(".board-column")?.classList.remove("drop-target"));
    byId("board").addEventListener("drop", (event) => {
      const column = event.target.closest(".board-column");
      if (!column) return;
      event.preventDefault();
      column.classList.remove("drop-target");
      moveIssue(event.dataTransfer.getData("text/plain"), column.dataset.status);
    });
    byId("search-input").addEventListener("input", (event) => {
      state.query = event.target.value;
      renderBoard();
      renderList();
    });
    byId("assignee-filter").addEventListener("change", (event) => {
      state.assignee = event.target.value;
      renderBoard();
      renderList();
    });
    byId("priority-filter").addEventListener("change", (event) => {
      state.priority = event.target.value;
      renderBoard();
      renderList();
    });
    document.querySelectorAll(".view-tab").forEach((tab) => tab.addEventListener("click", () => setView(tab.dataset.view)));
    document.querySelectorAll(".side-nav .nav-item").forEach((button) => button.addEventListener("click", () => {
      state.filterView = button.dataset.view;
      document.querySelectorAll(".side-nav .nav-item").forEach((item) => item.classList.toggle("active", item === button));
      document.querySelector(".project-heading h1").childNodes[0].textContent =
        state.filterView === "my-work" ? "My work " : "Project board ";
      render();
    }));
    byId("profile-button").addEventListener("click", signOut);
    byId("workspace-picker").addEventListener("click", () => showToast("This is your private local workspace."));
    byId("notification-button").addEventListener("click", () => showToast("You’re all caught up."));
    byId("project-name").addEventListener("input", (event) => {
      const keyField = byId("project-key");
      if (!keyField.dataset.edited) {
        keyField.value = event.target.value.replace(/[^a-z0-9]/gi, "").slice(0, 10).toUpperCase();
      }
    });
    byId("project-key").addEventListener("input", (event) => {
      event.target.dataset.edited = event.target.value ? "true" : "";
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !byId("issue-modal").hidden) closeIssueModal();
      if (event.key === "Escape" && !byId("project-modal").hidden) closeProjectModal();
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        byId("search-input").focus();
      }
      if (!event.ctrlKey && !event.metaKey && event.key.toLowerCase() === "c" &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) &&
        byId("issue-modal").hidden && !byId("workspace").hidden) openIssueModal();
    });
  }

  async function boot() {
    bindEvents();
    try {
      const user = await api("/users/session");
      if (user) await showWorkspace(user);
      else showAuth();
    } catch {
      showAuth();
    }
  }

  boot();
})();
