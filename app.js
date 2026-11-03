// ==========================================
// Primal Haven - Application Logic
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    currentCategory: "crops",
    currentSeason: "all",
    searchQuery: "",
    sortBy: "default",
    favorites: JSON.parse(localStorage.getItem("primal_favorites") || "[]"),
    activeZoneId: "zone-village"
  };

  // DOM Elements
  const itemsGrid = document.getElementById("items-grid");
  const categoryTabs = document.getElementById("category-tabs");
  const seasonFilters = document.getElementById("season-filters");
  const resultsCount = document.getElementById("results-count");
  const sortSelect = document.getElementById("sort-order");
  const globalSearch = document.getElementById("global-search");
  const filterControls = document.getElementById("filter-controls");

  // Sections
  const sectionCalculator = document.getElementById("section-calculator");
  const sectionGiftMatcher = document.getElementById("section-gift-matcher");
  const sectionMap = document.getElementById("section-map");

  // Modal Elements
  const detailModal = document.getElementById("detail-modal");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalHeaderContent = document.getElementById("modal-header-content");
  const modalBodyContent = document.getElementById("modal-body-content");

  // Favorites Drawer & Theme
  const favDrawer = document.getElementById("favorites-drawer");
  const favToggleBtn = document.getElementById("favorites-toggle-btn");
  const closeDrawerBtn = document.getElementById("close-drawer-btn");
  const favCounter = document.getElementById("fav-counter");
  const favItemsContainer = document.getElementById("fav-items-container");
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = document.getElementById("theme-icon");
  const toastNotification = document.getElementById("toast-notification");
  const toastMessage = document.getElementById("toast-message");

  // Initialize
  initTheme();
  updateFavoritesUI();
  updateStats();
  renderCurrentView();
  initCalculator();
  initGiftMatcher();
  initMap();

  // ==========================================
  // Navigation & Category Switching
  // ==========================================
  categoryTabs.addEventListener("click", (e) => {
    const tab = e.target.closest(".tab-btn");
    if (!tab) return;

    categoryTabs.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    tab.classList.add("active");

    const category = tab.dataset.category;
    state.currentCategory = category;

    // Reset season filter when leaving crops
    if (category !== "crops") {
      seasonFilters.style.display = "none";
    } else {
      seasonFilters.style.display = "flex";
    }

    renderCurrentView();
  });

  // Season filter chips
  seasonFilters.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip-btn");
    if (!chip) return;

    seasonFilters.querySelectorAll(".chip-btn").forEach(btn => btn.classList.remove("active"));
    chip.classList.add("active");

    state.currentSeason = chip.dataset.season;
    renderGridItems();
  });

  // Sorting
  sortSelect.addEventListener("change", (e) => {
    state.sortBy = e.target.value;
    renderGridItems();
  });

  // Global Instant Search
  globalSearch.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.trim().toLowerCase();
    
    if (state.searchQuery.length > 0) {
      // If user starts searching from special tools, switch back to cards view
      if (["calculator", "gift-matcher", "map"].includes(state.currentCategory)) {
        categoryTabs.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
        const cropsTab = categoryTabs.querySelector('[data-category="crops"]');
        if (cropsTab) cropsTab.classList.add("active");
        state.currentCategory = "crops";
      }
    }
    renderCurrentView();
  });

  // Keyboard shortcut '/' to search
  window.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== globalSearch) {
      e.preventDefault();
      globalSearch.focus();
      globalSearch.select();
    }
  });

  // Logo home button
  document.getElementById("brand-home-btn").addEventListener("click", () => {
    globalSearch.value = "";
    state.searchQuery = "";
    state.currentSeason = "all";
    seasonFilters.querySelectorAll(".chip-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.season === "all");
    });
    switchTab("crops");
  });

  function switchTab(cat) {
    state.currentCategory = cat;
    categoryTabs.querySelectorAll(".tab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.category === cat);
    });
    seasonFilters.style.display = (cat === "crops") ? "flex" : "none";
    renderCurrentView();
  }

  // ==========================================
  // Rendering Views
  // ==========================================
  function renderCurrentView() {
    // Hide all special sections by default
    sectionCalculator.style.display = "none";
    sectionGiftMatcher.style.display = "none";
    sectionMap.style.display = "none";
    itemsGrid.style.display = "grid";
    filterControls.style.display = "flex";

    if (state.currentCategory === "calculator") {
      sectionCalculator.style.display = "block";
      itemsGrid.style.display = "none";
      filterControls.style.display = "none";
      return;
    }

    if (state.currentCategory === "gift-matcher") {
      sectionGiftMatcher.style.display = "block";
      itemsGrid.style.display = "none";
      filterControls.style.display = "none";
      return;
    }

    if (state.currentCategory === "map") {
      sectionMap.style.display = "block";
      itemsGrid.style.display = "none";
      filterControls.style.display = "none";
      return;
    }

    renderGridItems();
  }

  function getItemsForCategory(category) {
    switch (category) {
      case "crops": return GAME_DATA.crops;
      case "animals": return GAME_DATA.animals;
      case "crafting": return GAME_DATA.crafting;
      case "villagers": return GAME_DATA.villagers;
      case "recipes": return GAME_DATA.recipes;
      default: return [];
    }
  }

  function renderGridItems() {
    let items = [];

    // If searching, search across all categories or current category
    if (state.searchQuery) {
      const allItems = [
        ...GAME_DATA.crops.map(i => ({ ...i, categoryType: "พืชพันธุ์" })),
        ...GAME_DATA.animals.map(i => ({ ...i, categoryType: "สัตว์โบราณ" })),
        ...GAME_DATA.crafting.map(i => ({ ...i, categoryType: "เครื่องมือ" })),
        ...GAME_DATA.villagers.map(i => ({ ...i, categoryType: "ชาวเผ่า" })),
        ...GAME_DATA.recipes.map(i => ({ ...i, categoryType: "สูตรอาหาร" }))
      ];

      items = allItems.filter(item => {
        const text = `${item.name} ${item.nameEn || ""} ${item.description || ""} ${item.role || ""} ${item.habitat || ""}`.toLowerCase();
        return text.includes(state.searchQuery);
      });
    } else {
      items = [...getItemsForCategory(state.currentCategory)];

      // Season filter for crops
      if (state.currentCategory === "crops" && state.currentSeason !== "all") {
        items = items.filter(item => item.season.includes(state.currentSeason));
      }
    }

    // Sort items
    if (state.sortBy === "name-asc") {
      items.sort((a, b) => a.name.localeCompare(b.name, 'th'));
    } else if (state.sortBy === "price-desc") {
      items.sort((a, b) => (b.sellPrice || 0) - (a.sellPrice || 0));
    } else if (state.sortBy === "days-asc") {
      items.sort((a, b) => (a.growthDays || 99) - (b.growthDays || 99));
    }

    resultsCount.textContent = `พบ ${items.length} รายการ`;

    if (items.length === 0) {
      itemsGrid.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>ไม่พบข้อมูลที่ตรงกับเงื่อนไข</h3>
          <p>ลองเปลี่ยนคำค้นหา หรือรีเซ็ตตัวกรองฤดูกาลดูใหม่อีกครั้ง</p>
        </div>
      `;
      return;
    }

    itemsGrid.innerHTML = items.map(item => createCardHTML(item)).join("");

    // Attach card event listeners
    itemsGrid.querySelectorAll(".item-card").forEach(card => {
      card.addEventListener("click", (e) => {
        if (e.target.closest(".fav-btn")) return; // Don't open modal when clicking favorite button
        const itemId = card.dataset.id;
        openModal(itemId);
      });
    });

    itemsGrid.querySelectorAll(".fav-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const itemId = btn.dataset.id;
        toggleFavorite(itemId);
      });
    });
  }

  // ==========================================
  // Card HTML Templates
  // ==========================================
  function createCardHTML(item) {
    const isFav = state.favorites.includes(item.id);
    const rarityClass = item.rarity ? `rarity-${item.rarity}` : 'rarity-common';
    const rarityLabel = item.rarity ? item.rarity.toUpperCase() : (item.tier || 'INFO');

    // Dynamic stats based on item type
    let statsHTML = '';
    let footerDetail = '';

    if (item.growthDays !== undefined) {
      // Crop Card
      statsHTML = `
        <div class="stat-item">⏱️ โต: <strong>${item.growthDays} วัน</strong></div>
        <div class="stat-item">🪙 ขาย: <strong>${item.sellPrice} หิน</strong></div>
        <div class="stat-item">⚡ ฟื้นฟู: <strong>+${item.energy}</strong></div>
      `;
      footerDetail = `<div class="card-season">${item.seasonName || item.season}</div>`;
    } else if (item.habitat) {
      // Beast Card
      statsHTML = `
        <div class="stat-item">🏠 ถิ่นที่อยู่: <strong>${item.habitat}</strong></div>
        <div class="stat-item">🍖 ชอบ: <strong>${item.favoriteFood.split(',')[0]}</strong></div>
      `;
      footerDetail = `<div class="card-season" style="color: #60a5fa;">🐾 ${item.type}</div>`;
    } else if (item.materials) {
      // Crafting Card
      const matSummary = item.materials.map(m => `${m.count} ${m.name}`).slice(0, 2).join(", ");
      statsHTML = `
        <div class="stat-item">🔨 วัตถุดิบ: <strong>${matSummary}...</strong></div>
        <div class="stat-item">🛡️ ความคงทน: <strong>${item.durability}</strong></div>
      `;
      footerDetail = `<div class="card-season" style="color: #fbbf24;">🪵 ${item.categoryName}</div>`;
    } else if (item.role) {
      // NPC Card
      statsHTML = `
        <div class="stat-item">🎂 วันเกิด: <strong>${item.birthday}</strong></div>
        <div class="stat-item">❤️ ชอบมาก: <strong>${item.loves[0]}</strong></div>
      `;
      footerDetail = `<div class="card-season" style="color: #34d399;">🏕️ ${item.role}</div>`;
    } else if (item.buff) {
      // Recipe Card
      statsHTML = `
        <div class="stat-item">✨ บัฟ: <strong>${item.buff}</strong></div>
        <div class="stat-item">⚡ Stamina: <strong>+${item.energyRestore}</strong></div>
      `;
      footerDetail = `<div class="card-season" style="color: #f87171;">🍲 ${item.station}</div>`;
    }

    return `
      <div class="item-card" data-id="${item.id}">
        <div>
          <div class="card-top">
            <div class="item-icon-box">${item.icon || '📦'}</div>
            <div class="card-actions-top">
              <span class="rarity-pill ${rarityClass}">${rarityLabel}</span>
              <button class="fav-btn ${isFav ? 'active' : ''}" data-id="${item.id}" title="${isFav ? 'นำออกจากที่บันทึก' : 'บันทึกเป็นรายการโปรด'}">
                ${isFav ? '★' : '☆'}
              </button>
            </div>
          </div>
          <h3 class="item-title">${item.name}</h3>
          <div class="item-subtitle">${item.nameEn || item.categoryType || ''}</div>
          <p class="item-desc">${item.description || item.personality || ''}</p>
        </div>

        <div>
          <div class="card-stats">
            ${statsHTML}
          </div>
          <div class="card-footer">
            ${footerDetail}
            <button class="card-view-btn">
              ดูรายละเอียด <span>→</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // ==========================================
  // Detail Modal Popup
  // ==========================================
  function findItemById(id) {
    const all = [
      ...GAME_DATA.crops,
      ...GAME_DATA.animals,
      ...GAME_DATA.crafting,
      ...GAME_DATA.villagers,
      ...GAME_DATA.recipes
    ];
    return all.find(item => item.id === id);
  }

  function openModal(itemId) {
    const item = findItemById(itemId);
    if (!item) return;

    modalHeaderContent.innerHTML = `
      <div class="modal-icon-lg">${item.icon || '📦'}</div>
      <div>
        <h2 style="font-size: 1.4rem; color: var(--text-main);">${item.name}</h2>
        <div style="font-size: 0.9rem; color: var(--primary); margin-top: 2px;">
          ${item.nameEn || item.role || item.tier || 'ข้อมูลดึกดำบรรพ์'}
        </div>
      </div>
    `;

    let bodyHTML = '';

    if (item.description) {
      bodyHTML += `<div class="modal-desc-box">${item.description}</div>`;
    }

    if (item.growthDays !== undefined) {
      // Crops detailed view
      bodyHTML += `
        <div class="modal-section-title">📊 สถิติและข้อมูลการเพาะปลูก</div>
        <div class="modal-stats-grid">
          <div class="modal-stat-box"><span>ฤดูกาลที่ปลูกได้:</span> <strong>${item.seasonName}</strong></div>
          <div class="modal-stat-box"><span>ระยะเวลาเติบโต:</span> <strong>${item.growthDays} วัน</strong></div>
          <div class="modal-stat-box"><span>การเก็บเกี่ยวซ้ำ:</span> <strong>${item.regrow ? `ได้ (ทุกๆ ${item.regrowDays} วัน)` : 'ไม่ได้'}</strong></div>
          <div class="modal-stat-box"><span>ราคาเมล็ด:</span> <strong>${item.seedPrice} หิน</strong></div>
          <div class="modal-stat-box"><span>ราคาขายผลผลิต:</span> <strong>${item.sellPrice} หิน</strong></div>
          <div class="modal-stat-box"><span>ฟื้นฟูพลังงาน:</span> <strong>+${item.energy} Stamina</strong></div>
        </div>

        <div class="modal-section-title">📍 แหล่งที่พบเมล็ดป่า</div>
        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px;">${item.location}</p>

        <div class="modal-section-title">💡 เคล็ดลับจากผู้เชี่ยวชาญ</div>
        <p style="font-size: 0.9rem; color: #fbbf24; background: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 8px;">
          ${item.tips}
        </p>
      `;
    } else if (item.habitat) {
      // Animal detailed view
      const productsHTML = item.products.map(p => `<li>${p}</li>`).join("");
      bodyHTML += `
        <div class="modal-section-title">🍖 ข้อมูลสัตว์และการฝึกให้เชื่อง</div>
        <div class="modal-stats-grid">
          <div class="modal-stat-box"><span>ประเภท:</span> <strong>${item.type}</strong></div>
          <div class="modal-stat-box"><span>ถิ่นอาศัย:</span> <strong>${item.habitat}</strong></div>
          <div class="modal-stat-box"><span>นิสัย:</span> <strong>${item.personality}</strong></div>
          <div class="modal-stat-box"><span>อาหารโปรด:</span> <strong>${item.favoriteFood}</strong></div>
        </div>

        <div class="modal-section-title">🎶 วิธีการฝึกให้เชื่อง (Taming Method)</div>
        <p style="font-size: 0.9rem; color: var(--text-main); background: var(--bg-secondary); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          ${item.tamingMethod}
        </p>

        <div class="modal-section-title">🎁 ผลผลิตและประโยชน์ที่ได้รับ</div>
        <ul style="font-size: 0.9rem; color: var(--text-muted); padding-left: 20px;">
          ${productsHTML}
        </ul>
      `;
    } else if (item.materials) {
      // Crafting detailed view
      const matsHTML = item.materials.map(m => `
        <div class="modal-stat-box">
          <span>${m.icon} ${m.name}</span>
          <strong>x ${m.count}</strong>
        </div>
      `).join("");

      bodyHTML += `
        <div class="modal-section-title">🔨 วัตถุดิบที่ต้องใช้ในการสร้าง</div>
        <div class="modal-stats-grid">
          ${matsHTML}
        </div>

        <div class="modal-section-title">⚙️ รายละเอียดอุปกรณ์</div>
        <div class="modal-stats-grid">
          <div class="modal-stat-box"><span>ระดับ Tier:</span> <strong>${item.tier}</strong></div>
          <div class="modal-stat-box"><span>ความคงทน (Durability):</span> <strong>${item.durability}</strong></div>
          <div class="modal-stat-box" style="grid-column: span 2;"><span>แท่นคราฟต์ที่ต้องใช้:</span> <strong>${item.workbench}</strong></div>
        </div>
      `;
    } else if (item.role) {
      // Villager detailed view
      bodyHTML += `
        <div class="modal-section-title">💬 คำพูดทักทาย</div>
        <p style="font-style: italic; color: #fef08a; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          "${item.dialogue}"
        </p>

        <div class="modal-section-title">🎁 รสนิยมของขวัญ (Gift Preferences)</div>
        <div style="margin-bottom: 12px;">
          <strong style="color: #ef4444; font-size: 0.88rem;">❤️ ชอบมากเป็นพิเศษ (Loves):</strong>
          <p style="font-size: 0.88rem; color: var(--text-muted);">${item.loves.join(", ")}</p>
        </div>
        <div style="margin-bottom: 12px;">
          <strong style="color: #10b981; font-size: 0.88rem;">👍 ชอบทั่วไป (Likes):</strong>
          <p style="font-size: 0.88rem; color: var(--text-muted);">${item.likes.join(", ")}</p>
        </div>
        <div style="margin-bottom: 16px;">
          <strong style="color: #6b7280; font-size: 0.88rem;">❌ ไม่ชอบ / เกลียด (Dislikes):</strong>
          <p style="font-size: 0.88rem; color: var(--text-muted);">${item.dislikes.join(", ")}</p>
        </div>

        <div class="modal-section-title">⏰ ตารางกิจวัตรประจำวัน (Daily Schedule)</div>
        <p style="font-size: 0.88rem; color: var(--text-muted); background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
          ${item.schedule}
        </p>
      `;
    } else if (item.buff) {
      // Recipe detailed view
      const ingsHTML = item.ingredients.map(i => `<div class="modal-stat-box" style="grid-column: span 2;"><span>ส่วนผสม:</span> <strong>${i}</strong></div>`).join("");
      bodyHTML += `
        <div class="modal-section-title">🍲 ส่วนผสมที่ต้องใช้</div>
        <div class="modal-stats-grid">
          ${ingsHTML}
        </div>

        <div class="modal-section-title">✨ ผลกระทบบัฟและพลังงาน</div>
        <div class="modal-stats-grid">
          <div class="modal-stat-box" style="grid-column: span 2;"><span>บัฟพิเศษ:</span> <strong style="color: var(--secondary);">${item.buff}</strong></div>
          <div class="modal-stat-box"><span>พลังงานที่ฟื้นฟู:</span> <strong>+${item.energyRestore} Stamina</strong></div>
          <div class="modal-stat-box"><span>เครื่องมือปรุง:</span> <strong>${item.station}</strong></div>
        </div>
      `;
    }

    modalBodyContent.innerHTML = bodyHTML;
    detailModal.classList.add("active");
  }

  modalCloseBtn.addEventListener("click", () => detailModal.classList.remove("active"));
  detailModal.addEventListener("click", (e) => {
    if (e.target === detailModal) detailModal.classList.remove("active");
  });

  // ==========================================
  // Interactive Tool 1: Crop Harvest Calculator
  // ==========================================
  function initCalculator() {
    const select = document.getElementById("calc-crop-select");
    const plotInput = document.getElementById("calc-plot-count");
    const startDayInput = document.getElementById("calc-start-day");

    // Populate crops
    select.innerHTML = GAME_DATA.crops.map(crop => `
      <option value="${crop.id}">${crop.icon} ${crop.name} (${crop.seasonName})</option>
    `).join("");

    function recalculate() {
      const cropId = select.value;
      const crop = GAME_DATA.crops.find(c => c.id === cropId);
      if (!crop) return;

      const plots = Math.max(1, parseInt(plotInput.value) || 1);
      const startDay = Math.min(28, Math.max(1, parseInt(startDayInput.value) || 1));
      const daysRemaining = 28 - startDay + 1;

      let harvestCount = 0;
      let totalSeedCost = 0;

      if (!crop.regrow) {
        // Single harvest crop
        harvestCount = Math.floor(daysRemaining / crop.growthDays);
        totalSeedCost = harvestCount * plots * crop.seedPrice;
      } else {
        // Regrow crop
        if (daysRemaining >= crop.growthDays) {
          harvestCount = 1 + Math.floor((daysRemaining - crop.growthDays) / crop.regrowDays);
        } else {
          harvestCount = 0;
        }
        totalSeedCost = plots * crop.seedPrice; // Buy seeds only once!
      }

      const totalYield = harvestCount * plots;
      const grossRevenue = totalYield * crop.sellPrice;
      const netProfit = grossRevenue - totalSeedCost;

      // Update UI
      document.getElementById("res-growth-days").textContent = `${crop.growthDays} วัน ${crop.regrow ? `(โตซ้ำทุก ${crop.regrowDays} วัน)` : ''}`;
      document.getElementById("res-regrow-info").textContent = crop.regrow ? "ได้ตลอดทั้งฤดู (ซื้อเมล็ดแค่รอบเดียว)" : "ไม่ได้ (ต้องปลูกใหม่ทุกรอบ)";
      document.getElementById("res-harvest-count").textContent = `${harvestCount} รอบ (${totalYield.toLocaleString()} ชิ้น)`;
      document.getElementById("res-total-cost").textContent = `${totalSeedCost.toLocaleString()} หิน`;
      document.getElementById("res-total-revenue").textContent = `${grossRevenue.toLocaleString()} หิน`;
      
      const profitElem = document.getElementById("res-net-profit");
      profitElem.textContent = `${netProfit >= 0 ? '+' : ''}${netProfit.toLocaleString()} หิน`;
      profitElem.style.color = netProfit >= 0 ? 'var(--secondary)' : 'var(--accent)';
    }

    select.addEventListener("change", recalculate);
    plotInput.addEventListener("input", recalculate);
    startDayInput.addEventListener("input", recalculate);
    recalculate();
  }

  // ==========================================
  // Interactive Tool 2: NPC Gift Matcher
  // ==========================================
  function initGiftMatcher() {
    const giftSelect = document.getElementById("gift-item-select");
    const resultsContainer = document.getElementById("gift-matcher-results");

    // Collect unique gift items
    const allGifts = new Set();
    GAME_DATA.villagers.forEach(v => {
      v.loves.forEach(g => allGifts.add(g));
      v.likes.forEach(g => allGifts.add(g));
      v.dislikes.forEach(g => allGifts.add(g));
    });

    const sortedGifts = Array.from(allGifts).sort();
    giftSelect.innerHTML = sortedGifts.map(gift => `<option value="${gift}">${gift}</option>`).join("");

    function matchGifts() {
      const selectedGift = giftSelect.value;
      
      const matched = GAME_DATA.villagers.map(npc => {
        let affinity = "neutral";
        let reaction = "รู้สึกเฉยๆ ขอบคุณนะ";
        let icon = "😐";

        if (npc.loves.some(item => selectedGift.includes(item) || item.includes(selectedGift))) {
          affinity = "love";
          reaction = "ว้าว! ข้าชอบสิ่งนี้มากที่สุด ขอบคุณเจ้าจากใจจริง!";
          icon = "❤️ ชอบมากที่สุด (Loves)";
        } else if (npc.likes.some(item => selectedGift.includes(item) || item.includes(selectedGift))) {
          affinity = "like";
          reaction = "ของขวัญที่ดีมาก! ข้าขอรับไว้ด้วยความยินดี";
          icon = "👍 ชอบ (Likes)";
        } else if (npc.dislikes.some(item => selectedGift.includes(item) || item.includes(selectedGift))) {
          affinity = "dislike";
          reaction = "ข้าไม่ชอบของสิ่งนี้เลย... เอาไปให้คนอื่นเถอะ";
          icon = "❌ ไม่ชอบ (Dislikes)";
        }

        return { npc, affinity, reaction, icon };
      });

      resultsContainer.innerHTML = matched.map(m => {
        const bgColors = {
          love: 'border-color: #ef4444; background: rgba(239, 68, 68, 0.08);',
          like: 'border-color: #10b981; background: rgba(16, 185, 129, 0.08);',
          dislike: 'border-color: #6b7280; opacity: 0.7;',
          neutral: 'border-color: var(--border-color);'
        };

        return `
          <div class="item-card" style="${bgColors[m.affinity]}">
            <div class="card-top">
              <div class="item-icon-box">${m.npc.icon}</div>
              <span class="rarity-pill" style="font-size: 0.8rem;">${m.icon}</span>
            </div>
            <h3 class="item-title">${m.npc.name}</h3>
            <div class="item-subtitle">${m.npc.role}</div>
            <p style="font-size: 0.88rem; font-style: italic; color: #fef08a; margin: 10px 0;">"${m.reaction}"</p>
          </div>
        `;
      }).join("");
    }

    giftSelect.addEventListener("change", matchGifts);
    matchGifts();
  }

  // ==========================================
  // Interactive Tool 3: World Map
  // ==========================================
  function initMap() {
    const nodes = document.querySelectorAll(".map-zone-node");
    const container = document.getElementById("zone-details-container");

    function renderZoneDetails(zoneId) {
      const zone = GAME_DATA.mapZones.find(z => z.id === zoneId);
      if (!zone) return;

      container.innerHTML = `
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 16px;">
          <div style="font-size: 2.5rem; background: var(--bg-secondary); padding: 10px; border-radius: 12px;">${zone.icon}</div>
          <div>
            <h3 style="font-size: 1.3rem; color: var(--primary);">${zone.name}</h3>
            <span style="font-size: 0.8rem; background: rgba(245, 158, 11, 0.15); color: var(--primary); padding: 2px 8px; border-radius: 4px;">${zone.level}</span>
          </div>
        </div>

        <p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 20px;">
          ${zone.description}
        </p>

        <div style="margin-bottom: 16px;">
          <strong style="font-size: 0.88rem; color: var(--text-main); display: block; margin-bottom: 8px;">🌾 ทรัพยากรเด่นที่เก็บเกี่ยวได้:</strong>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            ${zone.resources.map(r => `<span class="stat-chip" style="font-size: 0.78rem;">✨ ${r}</span>`).join("")}
          </div>
        </div>

        <div>
          <strong style="font-size: 0.88rem; color: var(--text-main); display: block; margin-bottom: 6px;">👥 บุคคลหรือสิ่งมีชีวิตที่พบได้:</strong>
          <p style="font-size: 0.88rem; color: #60a5fa;">${zone.notableNpc}</p>
        </div>
      `;
    }

    nodes.forEach(node => {
      node.addEventListener("click", () => {
        nodes.forEach(n => n.classList.remove("active"));
        node.classList.add("active");
        renderZoneDetails(node.dataset.zoneId);
      });
    });

    renderZoneDetails(state.activeZoneId);
  }

  // ==========================================
  // Favorites System
  // ==========================================
  function toggleFavorite(id) {
    const index = state.favorites.indexOf(id);
    const item = findItemById(id);
    const name = item ? item.name : "ไอเทม";

    if (index > -1) {
      state.favorites.splice(index, 1);
      showToast(`นำ "${name}" ออกจากรายการบันทึกแล้ว`);
    } else {
      state.favorites.push(id);
      showToast(`บันทึก "${name}" เรียบร้อยแล้ว ⭐`);
    }

    localStorage.setItem("primal_favorites", JSON.stringify(state.favorites));
    updateFavoritesUI();
    renderGridItems();
  }

  function updateFavoritesUI() {
    const count = state.favorites.length;
    favCounter.textContent = count;
    favCounter.style.display = count > 0 ? "flex" : "none";

    if (count === 0) {
      favItemsContainer.innerHTML = `
        <p style="color: var(--text-dim); text-align: center; margin-top: 40px;">
          ยังไม่มีไอเทมที่บันทึกไว้<br>กดไอคอนรูปดาว ⭐ บนการ์ดเพื่อบันทึก
        </p>
      `;
      return;
    }

    const items = state.favorites.map(id => findItemById(id)).filter(Boolean);
    favItemsContainer.innerHTML = items.map(item => `
      <div class="fav-item-row" data-id="${item.id}">
        <div style="display: flex; align-items: center; gap: 10px; cursor: pointer;" class="fav-open-item">
          <span style="font-size: 1.4rem;">${item.icon || '📦'}</span>
          <div>
            <div style="font-size: 0.88rem; font-weight: 600;">${item.name}</div>
            <div style="font-size: 0.75rem; color: var(--text-dim);">${item.categoryType || item.role || item.tier || 'ไอเทม'}</div>
          </div>
        </div>
        <button class="fav-remove-btn btn-icon" style="width: 28px; height: 28px; font-size: 0.9rem;" title="ลบออก">✕</button>
      </div>
    `).join("");

    favItemsContainer.querySelectorAll(".fav-open-item").forEach(el => {
      el.addEventListener("click", () => {
        const id = el.closest(".fav-item-row").dataset.id;
        favDrawer.classList.remove("open");
        openModal(id);
      });
    });

    favItemsContainer.querySelectorAll(".fav-remove-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = btn.closest(".fav-item-row").dataset.id;
        toggleFavorite(id);
      });
    });
  }

  favToggleBtn.addEventListener("click", () => favDrawer.classList.toggle("open"));
  closeDrawerBtn.addEventListener("click", () => favDrawer.classList.remove("open"));

  // ==========================================
  // Theme Toggle (Dark vs Warm Light)
  // ==========================================
  function initTheme() {
    const savedTheme = localStorage.getItem("primal_theme") || "dark";
    if (savedTheme === "light") {
      document.body.classList.add("theme-light");
      themeIcon.textContent = "☀️";
    }
  }

  themeToggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("theme-light");
    const isLight = document.body.classList.contains("theme-light");
    themeIcon.textContent = isLight ? "☀️" : "🌙";
    localStorage.setItem("primal_theme", isLight ? "light" : "dark");
  });

  // ==========================================
  // Helper: Stats & Toast
  // ==========================================
  function updateStats() {
    document.getElementById("stat-crops").textContent = GAME_DATA.crops.length;
    document.getElementById("stat-animals").textContent = GAME_DATA.animals.length;
    document.getElementById("stat-tools").textContent = GAME_DATA.crafting.length;
    document.getElementById("stat-npcs").textContent = GAME_DATA.villagers.length;
    document.getElementById("stat-recipes").textContent = GAME_DATA.recipes.length;
  }

  let toastTimer = null;
  function showToast(msg) {
    toastMessage.textContent = msg;
    toastNotification.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastNotification.classList.remove("show");
    }, 2500);
  }
});
