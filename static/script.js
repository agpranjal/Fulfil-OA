const api = {
  async uploadFile(file) {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/upload", { method: "POST", body: form });
    if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
    return res.json();
  },
  async uploadStatus(taskId) {
    const res = await fetch(`/upload/status/${taskId}`);
    if (!res.ok) throw new Error("Unable to fetch status");
    return res.json();
  },
  async listProducts(params = {}) {
    const query = new URLSearchParams(params);
    const res = await fetch(`/products?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch products");
    return res.json();
  },
  async createProduct(payload) {
    const res = await fetch("/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to create product");
    return res.json();
  },
  async updateProduct(id, payload) {
    const res = await fetch(`/products/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to update product");
    return res.json();
  },
  async deleteProduct(id) {
    const res = await fetch(`/products/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete product");
  },
  async deleteAllProducts() {
    const res = await fetch("/products?confirm=true", { method: "DELETE" });
    if (!res.ok) throw new Error((await res.json()).detail || "Delete failed");
    return res.json();
  },
  async listWebhooks() {
    const res = await fetch("/webhooks");
    if (!res.ok) throw new Error("Failed to fetch webhooks");
    return res.json();
  },
  async createWebhook(payload) {
    const res = await fetch("/webhooks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to create webhook");
    return res.json();
  },
  async updateWebhook(id, payload) {
    const res = await fetch(`/webhooks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to update webhook");
    return res.json();
  },
  async deleteWebhook(id) {
    const res = await fetch(`/webhooks/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete webhook");
  },
  async testWebhook(id) {
    const res = await fetch(`/webhooks/test/${id}`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to trigger test webhook");
    return res.json();
  },
};

function qs(selector) {
  return document.querySelector(selector);
}

function qsa(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function toggle(el, show) {
  if (!el) return;
  el.classList[show ? "remove" : "add"]("hidden");
}

function getFormData(form) {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

function parseBool(val) {
  if (val === "" || val === null || val === undefined) return undefined;
  return val === true || val === "true";
}

function initUploadPage() {
  const form = qs("#upload-form");
  if (!form) return;

  const input = qs("#upload-input");
  const statusCard = qs("#upload-status");
  const progressBar = qs("#progress-bar");
  const processed = qs("#processed-count");
  const total = qs("#total-count");
  const statusLabel = qs("#status-label");
  const statusMessage = qs("#status-message");
  const taskLabel = qs("#task-id-label");
  const errorBox = qs("#error-box");
  const refreshBtn = qs("#refresh-status");
  let pollId = null;
  let currentTask = null;

  async function fetchStatus() {
    if (!currentTask) return;
    try {
      const data = await api.uploadStatus(currentTask);
      progressBar.style.width = `${data.percent}%`;
      processed.textContent = data.processed;
      total.textContent = data.total;
      statusLabel.textContent = data.status;
      statusMessage.textContent = data.message || "";
    } catch (err) {
      statusMessage.textContent = err.message;
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!input.files.length) return;
    try {
      const { task_id } = await api.uploadFile(input.files[0]);
      currentTask = task_id;
      taskLabel.textContent = `Task ID: ${task_id}`;
      toggle(statusCard, true);
      toggle(errorBox, false);
      await fetchStatus();
      if (pollId) clearInterval(pollId);
      pollId = setInterval(fetchStatus, 2000);
    } catch (err) {
      errorBox.textContent = err.message || "Upload failed";
      toggle(errorBox, true);
    }
  });

  refreshBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    fetchStatus();
  });
}

function initProductsPage() {
  const filtersForm = qs("#product-filters");
  const tableBody = qs("#products-table tbody");
  const pagination = qs("#products-pagination");
  const modal = qs("#product-modal");
  const openCreate = qs("#open-create");
  const form = qs("#product-form");
  const resetFilters = qs("#reset-filters");

  if (!filtersForm || !tableBody) return;

  let page = 1;
  let totalPages = 1;

   const renderMessageRow = (message) => {
    tableBody.innerHTML = `<tr><td colspan="6" class="muted">${message}</td></tr>`;
  };

  function openModal(mode = "create", product = null) {
    qs("#product-modal-title").textContent = mode === "edit" ? "Edit Product" : "Create Product";
    form.reset();
    form.dataset.mode = mode;
    if (product) {
      qs("#product-id").value = product.id;
      qs("#product-sku").value = product.sku;
      qs("#product-name").value = product.name || "";
      qs("#product-description").value = product.description || "";
      qs("#product-price").value = product.price ?? "";
      qs("#product-active").value = product.active ? "true" : "false";
    } else {
      qs("#product-active").value = "true";
    }
    toggle(modal, true);
  }

  function closeModal() {
    toggle(modal, false);
  }

  async function loadProducts() {
    try {
      const query = Object.fromEntries(new FormData(filtersForm).entries());
      const params = {
        page,
        limit: 10,
        ...query,
        active: query.active === "" ? undefined : query.active,
      };
      const data = await api.listProducts(params);
      page = data.page;
      totalPages = data.total_pages;
      if (!data.items.length) {
        renderMessageRow("No products found.");
      } else {
        tableBody.innerHTML = data.items
          .map(
            (p) => `<tr data-id="${p.id}">
              <td>${p.sku}</td>
              <td>${p.name || ""}</td>
              <td>${p.description || ""}</td>
              <td>${p.price ?? ""}</td>
              <td>${p.active ? "Active" : "Inactive"}</td>
              <td class="table-actions">
                <button class="btn btn--ghost" data-action="edit">Edit</button>
                <button class="btn btn--ghost" data-action="delete">Delete</button>
              </td>
            </tr>`
          )
          .join("");
      }
      pagination.querySelector("[data-page-current]").textContent = data.page;
      pagination.querySelector("[data-page-total]").textContent = data.total_pages || 1;
    } catch (err) {
      renderMessageRow(err.message || "Error loading products");
      console.error(err);
    }
  }

  filtersForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    page = 1;
    await loadProducts();
  });

  resetFilters?.addEventListener("click", async () => {
    filtersForm.reset();
    page = 1;
    await loadProducts();
  });

  pagination.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-page]");
    if (!btn) return;
    const dir = btn.dataset.page;
    if (dir === "prev" && page > 1) page -= 1;
    if (dir === "next" && page < totalPages) page += 1;
    await loadProducts();
  });

  openCreate?.addEventListener("click", () => openModal("create"));

  modal?.addEventListener("click", (e) => {
    if (e.target === modal || e.target.hasAttribute("data-close-modal")) closeModal();
  });

  tableBody.addEventListener("click", async (e) => {
    const actionBtn = e.target.closest("[data-action]");
    if (!actionBtn) return;
    const row = e.target.closest("tr");
    const id = row?.dataset.id;
    if (!id) return;
    if (actionBtn.dataset.action === "edit") {
      const cells = row.querySelectorAll("td");
      openModal("edit", {
        id,
        sku: cells[0].textContent.trim(),
        name: cells[1].textContent.trim(),
        description: cells[2].textContent.trim(),
        price: cells[3].textContent.trim() || null,
        active: cells[4].textContent.trim().toLowerCase() === "active",
      });
    }
    if (actionBtn.dataset.action === "delete") {
      await api.deleteProduct(id);
      await loadProducts();
    }
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mode = form.dataset.mode || "create";
    const payload = getFormData(form);
    payload.price = payload.price === "" ? null : parseFloat(payload.price);
    payload.active = parseBool(payload.active);
    if (mode === "edit") {
      const id = payload.id;
      delete payload.id;
      await api.updateProduct(id, payload);
    } else {
      delete payload.id;
      await api.createProduct(payload);
    }
    closeModal();
    await loadProducts();
  });

  loadProducts();
}

function initAdminPage() {
  const btn = qs("#delete-all");
  const confirm = qs("#confirm-delete");
  const result = qs("#delete-result");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    if (!confirm.checked) {
      result.textContent = "Please confirm before deleting.";
      result.className = "alert alert--warning";
      toggle(result, true);
      return;
    }
    try {
      const res = await api.deleteAllProducts();
      result.textContent = `Deleted ${res.deleted} products.`;
      result.className = "alert alert--warning";
      toggle(result, true);
    } catch (err) {
      result.textContent = err.message;
      result.className = "alert alert--error";
      toggle(result, true);
    }
  });
}

function initWebhooksPage() {
  const tableBody = qs("#webhooks-table tbody");
  const modal = qs("#webhook-modal");
  const openCreate = qs("#open-webhook-create");
  const form = qs("#webhook-form");

  if (!tableBody) return;

  function openModal(mode = "create", webhook = null) {
    qs("#webhook-modal-title").textContent = mode === "edit" ? "Edit Webhook" : "Create Webhook";
    form.reset();
    form.dataset.mode = mode;
    if (webhook) {
      qs("#webhook-id").value = webhook.id;
      qs("#webhook-url").value = webhook.url;
      qs("#webhook-event").value = webhook.event_type;
      qs("#webhook-active").value = webhook.active ? "true" : "false";
    } else {
      qs("#webhook-active").value = "true";
    }
    toggle(modal, true);
  }

  function closeModal() {
    toggle(modal, false);
  }

  async function loadWebhooks() {
    const items = await api.listWebhooks();
    tableBody.innerHTML = items
      .map(
        (w) => `<tr data-id="${w.id}">
          <td>${w.url}</td>
          <td>${w.event_type}</td>
          <td>${w.active ? "Enabled" : "Disabled"}</td>
          <td class="table-actions">
            <button class="btn btn--ghost" data-action="test">Test</button>
            <button class="btn btn--ghost" data-action="edit">Edit</button>
            <button class="btn btn--ghost" data-action="delete">Delete</button>
          </td>
        </tr>`
      )
      .join("");
  }

  openCreate?.addEventListener("click", () => openModal("create"));

  modal?.addEventListener("click", (e) => {
    if (e.target === modal || e.target.hasAttribute("data-close-modal")) closeModal();
  });

  tableBody.addEventListener("click", async (e) => {
    const actionBtn = e.target.closest("[data-action]");
    if (!actionBtn) return;
    const row = e.target.closest("tr");
    const id = row?.dataset.id;
    if (!id) return;
    const cells = row.querySelectorAll("td");
    const webhook = {
      id,
      url: cells[0].textContent.trim(),
      event_type: cells[1].textContent.trim(),
      active: cells[2].textContent.trim().toLowerCase() === "enabled",
    };
    if (actionBtn.dataset.action === "edit") {
      openModal("edit", webhook);
    }
    if (actionBtn.dataset.action === "delete") {
      await api.deleteWebhook(id);
      await loadWebhooks();
    }
    if (actionBtn.dataset.action === "test") {
      const res = await api.testWebhook(id);
      alert(`Test triggered. Task ID: ${res.task_id}`);
    }
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mode = form.dataset.mode || "create";
    const payload = getFormData(form);
    payload.active = parseBool(payload.active);
    if (mode === "edit") {
      const id = payload.id;
      delete payload.id;
      await api.updateWebhook(id, payload);
    } else {
      delete payload.id;
      await api.createWebhook(payload);
    }
    closeModal();
    await loadWebhooks();
  });

  loadWebhooks();
}

document.addEventListener("DOMContentLoaded", () => {
  initUploadPage();
  initProductsPage();
  initAdminPage();
  initWebhooksPage();
});
