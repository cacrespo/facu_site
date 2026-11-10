// State Management
let cart = {}; // { [productId]: quantity }

// Format currency in Argentine Pesos style: $ 18.500
function formatPrice(amount) {
  return '$' + Math.round(amount).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// Get product by ID from embedded catalog
function getProductById(id) {
  if (!window.PRODUCTS_CATALOG) return null;
  return window.PRODUCTS_CATALOG.find(p => p.id === id);
}

// Filter products by category
function filterCategory(categoryId) {
  // Update pill buttons visual state
  document.querySelectorAll('.cat-pill').forEach(btn => {
    btn.classList.remove('bg-dulce-600', 'text-white', 'shadow-sm');
    btn.classList.add('bg-white', 'text-stone-700', 'border', 'border-stone-200/70');
  });

  const activeBtn = document.getElementById(`btn-cat-${categoryId}`);
  if (activeBtn) {
    activeBtn.classList.remove('bg-white', 'text-stone-700', 'border', 'border-stone-200/70');
    activeBtn.classList.add('bg-dulce-600', 'text-white', 'shadow-sm');
  }

  // Filter cards
  const cards = document.querySelectorAll('.product-card');
  cards.forEach(card => {
    const cardCat = card.getAttribute('data-category');
    if (categoryId === 'todos') {
      card.style.display = 'flex';
    } else if (categoryId === 'destacados') {
      // show if category is destacados or marked featured
      const pid = card.getAttribute('data-id');
      const prod = getProductById(pid);
      if (cardCat === 'destacados' || (prod && prod.is_featured)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    } else {
      if (cardCat === categoryId) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    }
  });
}

// Add 1 item to cart
function addToCart(productId) {
  if (!cart[productId]) {
    cart[productId] = 0;
  }
  cart[productId] += 1;
  updateCartUI();
  saveCartToStorage();
}

// Remove 1 item from cart
function removeFromCart(productId) {
  if (cart[productId]) {
    cart[productId] -= 1;
    if (cart[productId] <= 0) {
      delete cart[productId];
    }
  }
  updateCartUI();
  saveCartToStorage();
}

// Delete item completely
function deleteItem(productId) {
  delete cart[productId];
  updateCartUI();
  saveCartToStorage();
}

// Calculate totals
function getCartTotals() {
  let count = 0;
  let total = 0;
  for (const [id, qty] of Object.entries(cart)) {
    const prod = getProductById(id);
    if (prod && qty > 0) {
      count += qty;
      total += prod.price * qty;
    }
  }
  return { count, total };
}

// Update all UI components linked to cart
function updateCartUI() {
  const { count, total } = getCartTotals();

  // 1. Update Card Action buttons
  if (window.PRODUCTS_CATALOG) {
    window.PRODUCTS_CATALOG.forEach(p => {
      const container = document.getElementById(`cart-actions-${p.id}`);
      if (!container) return;

      const qty = cart[p.id] || 0;
      if (qty === 0) {
        container.innerHTML = `
          <button 
            type="button"
            onclick="addToCart('${p.id}')" 
            class="inline-flex items-center gap-1 px-3.5 py-2 rounded-xl bg-dulce-600 hover:bg-dulce-700 text-white text-xs sm:text-sm font-bold shadow-xs active:scale-95 transition-all"
            aria-label="Agregar ${p.name} al pedido"
          >
            <i class="ph-bold ph-plus"></i>
            <span>Agregar</span>
          </button>
        `;
      } else {
        container.innerHTML = `
          <div class="inline-flex items-center bg-amber-100 rounded-xl p-1 gap-1 border border-amber-300">
            <button 
              type="button" 
              onclick="removeFromCart('${p.id}')" 
              class="w-7 h-7 rounded-lg bg-white text-stone-800 hover:bg-amber-200 flex items-center justify-center font-bold text-sm shadow-xs active:scale-90"
              aria-label="Restar una unidad"
            >
              <i class="ph-bold ph-minus"></i>
            </button>
            <span class="w-6 text-center font-extrabold text-xs text-stone-900">${qty}</span>
            <button 
              type="button" 
              onclick="addToCart('${p.id}')" 
              class="w-7 h-7 rounded-lg bg-dulce-600 text-white hover:bg-dulce-700 flex items-center justify-center font-bold text-sm shadow-xs active:scale-90"
              aria-label="Sumar una unidad"
            >
              <i class="ph-bold ph-plus"></i>
            </button>
          </div>
        `;
      }
    });
  }

  // 2. Update Sticky Bottom Bar
  const stickyBar = document.getElementById('sticky-cart-bar');
  const badgeCount = document.getElementById('cart-badge-count');
  const barTotal = document.getElementById('cart-bar-total');

  if (stickyBar && badgeCount && barTotal) {
    if (count > 0) {
      badgeCount.textContent = count;
      barTotal.textContent = formatPrice(total);
      stickyBar.classList.remove('translate-y-full');
    } else {
      stickyBar.classList.add('translate-y-full');
    }
  }

  // 3. Update Drawer content if open
  renderCartDrawerItems(total);
}

// Render items inside the drawer/bottom sheet
function renderCartDrawerItems(total) {
  const container = document.getElementById('cart-items-container');
  const drawerTotal = document.getElementById('drawer-total-amount');
  const sendBtn = document.getElementById('btn-send-whatsapp');

  if (!container || !drawerTotal) return;

  drawerTotal.textContent = formatPrice(total);

  const entries = Object.entries(cart);

  if (entries.length === 0) {
    container.innerHTML = `
      <div class="py-12 text-center space-y-3">
        <span class="text-4xl">🧺</span>
        <h4 class="font-bold text-stone-700 text-sm">Tu canasta está vacía</h4>
        <p class="text-xs text-stone-500 max-w-xs mx-auto">Elegí tus tortas o tartas preferidas desde el menú para empezar a armar tu pedido.</p>
      </div>
    `;
    if (sendBtn) {
      sendBtn.disabled = true;
      sendBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
    return;
  }

  if (sendBtn) {
    sendBtn.disabled = false;
    sendBtn.classList.remove('opacity-50', 'cursor-not-allowed');
  }

  let html = '';
  entries.forEach(([id, qty]) => {
    const prod = getProductById(id);
    if (!prod) return;
    const subtotal = prod.price * qty;

    html += `
      <div class="pt-3 first:pt-0 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <img src="${prod.image}" alt="${prod.name}" class="w-12 h-12 rounded-xl object-cover border border-stone-200">
          <div>
            <h4 class="font-bold text-xs sm:text-sm text-stone-900 leading-snug">${prod.name}</h4>
            <span class="text-[11px] text-stone-500 block">${formatPrice(prod.price)} c/u</span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Stepper -->
          <div class="inline-flex items-center bg-stone-100 rounded-lg p-0.5 border border-stone-200">
            <button 
              type="button" 
              onclick="removeFromCart('${prod.id}')" 
              class="w-6 h-6 rounded bg-white text-stone-800 flex items-center justify-center font-bold text-xs active:scale-90"
            >
              <i class="ph-bold ph-minus"></i>
            </button>
            <span class="w-6 text-center font-bold text-xs text-stone-900">${qty}</span>
            <button 
              type="button" 
              onclick="addToCart('${prod.id}')" 
              class="w-6 h-6 rounded bg-dulce-600 text-white flex items-center justify-center font-bold text-xs active:scale-90"
            >
              <i class="ph-bold ph-plus"></i>
            </button>
          </div>

          <div class="text-right min-w-[65px]">
            <span class="font-extrabold text-xs sm:text-sm text-stone-900">${formatPrice(subtotal)}</span>
          </div>

          <button 
            type="button" 
            onclick="deleteItem('${prod.id}')" 
            class="text-stone-400 hover:text-red-600 text-base p-1 transition-colors"
            title="Quitar producto"
          >
            <i class="ph-bold ph-trash"></i>
          </button>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// Open Drawer
function openCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const panel = document.getElementById('cart-drawer-panel');
  if (drawer && panel) {
    drawer.classList.remove('opacity-0', 'pointer-events-none');
    drawer.classList.add('opacity-100');
    panel.classList.remove('translate-y-full', 'sm:translate-y-4');
    panel.classList.add('translate-y-0');
    document.body.style.overflow = 'hidden';
  }
}

// Close Drawer
function closeCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const panel = document.getElementById('cart-drawer-panel');
  if (drawer && panel) {
    drawer.classList.add('opacity-0', 'pointer-events-none');
    drawer.classList.remove('opacity-100');
    panel.classList.add('translate-y-full', 'sm:translate-y-4');
    panel.classList.remove('translate-y-0');
    document.body.style.overflow = '';
  }
}

// Build and launch WhatsApp order
function submitOrderToWhatsApp() {
  const { count, total } = getCartTotals();
  if (count === 0) return;

  const customerName = document.getElementById('order-customer-name')?.value.trim() || '';
  const deliveryType = document.getElementById('order-delivery-type')?.value || 'Entrega en Hurlingham';
  const notes = document.getElementById('order-notes')?.value.trim() || '';

  const greeting = window.BUSINESS_CONFIG?.settings?.whatsapp_greeting || "👋 ¡Hola Facu! Te contacto desde tu página web para hacer un pedido:";
  const footer = window.BUSINESS_CONFIG?.settings?.whatsapp_footer || "¿Cómo coordinamos el pago y horario? ¡Muchas gracias!";
  const supportNote = window.BUSINESS_CONFIG?.settings?.support_note || "💙 *Colaboración voluntaria:* Me gustaría sumar un aporte de corazón para tus medicamentos.";

  const lines = [
    greeting,
    "",
    "🍰 *DETALLE DEL PEDIDO:*"
  ];

  for (const [id, qty] of Object.entries(cart)) {
    const prod = getProductById(id);
    if (prod && qty > 0) {
      lines.push(`• ${qty}x ${prod.name} (${formatPrice(prod.price * qty)})`);
    }
  }

  lines.push("");
  lines.push(`💰 *Total estimado:* ${formatPrice(total)}`);
  lines.push("");

  if (customerName) {
    lines.push(`👤 *A nombre de:* ${customerName}`);
  }
  lines.push(`📍 *Modalidad:* ${deliveryType}`);
  if (notes) {
    lines.push(`📝 *Aclaraciones / Fecha:* ${notes}`);
  }

  // Voluntary donation check
  const voluntarySupport = document.getElementById('order-voluntary-support')?.checked;
  if (voluntarySupport) {
    lines.push(supportNote);
  }

  lines.push("");
  lines.push(footer);

  const fullText = lines.join("\n");
  const encodedText = encodeURIComponent(fullText);
  const phone = window.BUSINESS_CONFIG?.phone_raw || '5491164546785';
  const whatsappUrl = `https://wa.me/${phone}?text=${encodedText}`;

  // Open in new window/app
  window.open(whatsappUrl, '_blank');
}

// Storage helpers
function saveCartToStorage() {
  try {
    localStorage.setItem('facu_cart', JSON.stringify(cart));
  } catch (e) {}
}

function loadCartFromStorage() {
  try {
    const saved = localStorage.getItem('facu_cart');
    if (saved) {
      cart = JSON.parse(saved);
    }
  } catch (e) {}
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  loadCartFromStorage();
  updateCartUI();

  // Close drawer when clicking backdrop
  const drawer = document.getElementById('cart-drawer');
  drawer?.addEventListener('click', (e) => {
    if (e.target === drawer) {
      closeCartDrawer();
    }
  });

  // ESC to close drawer
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeCartDrawer();
    }
  });
});

// Copy Support Alias to clipboard
function copySupportAlias() {
  const alias = window.BUSINESS_CONFIG?.support?.alias || 'juarezdownes.tortas';
  navigator.clipboard.writeText(alias).then(() => {
    const btn = document.getElementById('btn-copy-alias');
    const label = document.getElementById('btn-copy-alias-label');
    if (btn && label) {
      const originalText = label.textContent;
      label.textContent = '¡Copiado! ✓';
      btn.classList.remove('bg-stone-900', 'hover:bg-stone-800');
      btn.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
      setTimeout(() => {
        label.textContent = originalText;
        btn.classList.remove('bg-emerald-600', 'hover:bg-emerald-700');
        btn.classList.add('bg-stone-900', 'hover:bg-stone-800');
      }, 2000);
    }
  }).catch(() => {
    const textEl = document.getElementById('support-alias-text');
    if (textEl) {
      window.prompt('Copiá el alias de Facu:', alias);
    }
  });
}

// ==========================================
// CLIENT REVIEWS & TESTIMONIALS LOGIC
// ==========================================

let currentRating = 5;

function openReviewModal() {
  const modal = document.getElementById('review-modal');
  const panel = document.getElementById('review-modal-panel');
  if (modal && panel) {
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modal.classList.add('opacity-100');
    panel.classList.remove('scale-95');
    panel.classList.add('scale-100');
    document.body.style.overflow = 'hidden';
  }
}

function closeReviewModal() {
  const modal = document.getElementById('review-modal');
  const panel = document.getElementById('review-modal-panel');
  if (modal && panel) {
    modal.classList.add('opacity-0', 'pointer-events-none');
    modal.classList.remove('opacity-100');
    panel.classList.add('scale-95');
    panel.classList.remove('scale-100');
    document.body.style.overflow = '';
  }
}

function setReviewRating(rating) {
  currentRating = rating;
  const hiddenInput = document.getElementById('rev-rating');
  if (hiddenInput) hiddenInput.value = rating;

  const starBtns = document.querySelectorAll('#star-rating-container .star-btn i');
  starBtns.forEach((icon, idx) => {
    if (idx < rating) {
      icon.className = 'ph-fill ph-star';
      icon.parentElement.classList.remove('text-stone-300');
      icon.parentElement.classList.add('text-amber-400');
    } else {
      icon.className = 'ph-bold ph-star';
      icon.parentElement.classList.remove('text-amber-400');
      icon.parentElement.classList.add('text-stone-300');
    }
  });
}

async function submitReviewForm(event) {
  event.preventDefault();
  const name = document.getElementById('rev-name')?.value.trim();
  const neighborhood = document.getElementById('rev-neighborhood')?.value.trim() || 'Hurlingham';
  const comment = document.getElementById('rev-comment')?.value.trim();
  const rating = parseInt(document.getElementById('rev-rating')?.value || '5', 10);
  const submitBtn = document.getElementById('btn-submit-review');

  if (!name || !comment) return;

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="ph-bold ph-spinner animate-spin"></i> Publicando...';
  }

  try {
    const res = await fetch('/api/reviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, neighborhood, rating, comment }),
    });

    if (!res.ok) throw new Error('Error al enviar reseña');
    const data = await res.json();

    // Insert new review card on the grid dynamically
    const grid = document.getElementById('reviews-grid');
    if (grid && data.review) {
      const card = document.createElement('div');
      card.className = 'bg-white rounded-2xl p-5 border border-amber-300 shadow-sm flex flex-col justify-between space-y-4 animate-pop';
      let starsHtml = '';
      for (let i = 0; i < (data.review.rating || 5); i++) {
        starsHtml += '<i class="ph-fill ph-star"></i>';
      }
      card.innerHTML = `
        <div class="space-y-2.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-0.5 text-amber-400 text-sm">
              ${starsHtml}
            </div>
            <span class="text-[11px] text-stone-400 font-medium">${data.review.date}</span>
          </div>
          <p class="text-xs sm:text-sm text-stone-700 leading-relaxed italic">
            "${data.review.comment}"
          </p>
        </div>
        <div class="pt-3 border-t border-stone-100 flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center shrink-0">
            ${data.review.name.charAt(0).toUpperCase()}
          </div>
          <div class="min-w-0">
            <span class="font-bold text-xs text-stone-900 block truncate">${data.review.name}</span>
            <span class="text-[10px] text-stone-500 block truncate flex items-center gap-1">
              <i class="ph-fill ph-map-pin text-stone-400 text-[10px]"></i>
              ${data.review.neighborhood}
            </span>
          </div>
        </div>
      `;
      grid.prepend(card);
    }

    closeReviewModal();
    alert('¡Muchas gracias por tu mensaje de cariño! Ya quedó publicado.');
    document.getElementById('review-form')?.reset();
    setReviewRating(5);
  } catch (err) {
    alert('Hubo un error al publicar el mensaje. Por favor intentalo nuevamente o envialo por WhatsApp.');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="ph-bold ph-paper-plane-tilt"></i><span>Publicar en la web</span>';
    }
  }
}

function sendReviewToWhatsApp() {
  const name = document.getElementById('rev-name')?.value.trim() || 'Un vecino de Hurlingham';
  const neighborhood = document.getElementById('rev-neighborhood')?.value.trim();
  const comment = document.getElementById('rev-comment')?.value.trim();
  const rating = document.getElementById('rev-rating')?.value || '5';

  if (!comment) {
    alert('Por favor escribí tu mensaje antes de enviar.');
    return;
  }

  let stars = '⭐'.repeat(parseInt(rating, 10));
  let place = neighborhood ? ` (${neighborhood})` : '';
  const text = `👋 ¡Hola Facu! Te dejo un mensaje de cariño desde tu web:\n\n💬 *Mensaje de ${name}${place}:*\n"${comment}"\n\n${stars}\n¡Muchas gracias por tus ricas tortas de siempre!`;
  const phone = window.BUSINESS_CONFIG?.phone_raw || '5491164546785';
  window.open(`https://wa.me/${phone}?text=${encodeURIComponent(text)}`, '_blank');
}
