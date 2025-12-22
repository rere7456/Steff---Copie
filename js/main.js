document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const gallery = document.getElementById('gallery');
    const menuBtn = document.getElementById('menu-btn');
    const closeMenuBtn = document.getElementById('close-menu');
    const menuOverlay = document.getElementById('menu-overlay');
    const detailView = document.getElementById('detail-view');

    let allDescriptions = null; // Sera chargé au premier clic

    // 1. INTRO
    window.addEventListener('load', () => {
        setTimeout(() => body.classList.remove('loading'), 5500);
    });

    // 2. GESTION MENU
    menuBtn.onclick = () => { menuOverlay.classList.add('active'); body.style.overflow = 'hidden'; };
    closeMenuBtn.onclick = () => { menuOverlay.classList.remove('active'); body.style.overflow = ''; };
    document.querySelectorAll('.menu-link').forEach(link => {
        link.onclick = () => { menuOverlay.classList.remove('active'); body.style.overflow = ''; };
    });

    // 3. CHARGEMENT GALERIE (Léger)
    if (typeof GALLERY_ITEMS !== 'undefined') {
        renderGallery(GALLERY_ITEMS);
        setupFilters(GALLERY_ITEMS);
    }

    function renderGallery(photos) {
        gallery.innerHTML = '';
        photos.forEach((photo, index) => {
            const item = document.createElement('div');
            item.className = 'grid-item';
            item.innerHTML = `
                <div class="img-container">
                    <img src="${photo.src}" alt="${photo.title}" loading="lazy">
                </div>
                <div class="item-info" style="display:flex; justify-content:space-between; margin-top:10px; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; opacity:0.6;">
                    <span>${photo.title}</span>
                    <span>${photo.year}</span>
                </div>
            `;
            item.onclick = () => openDetail(photo);
            gallery.appendChild(item);
            setTimeout(() => item.classList.add('visible'), 100 + (index * 50));
        });
    }

    // 4. FILTRES
    function setupFilters(allPhotos) {
        document.querySelectorAll('#gallery-filters li').forEach(link => {
            link.onclick = () => {
                document.querySelectorAll('#gallery-filters li').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                const filter = link.dataset.filter;
                const filtered = filter === 'all' ? allPhotos : allPhotos.filter(p => p.category === filter);
                document.querySelectorAll('.grid-item').forEach(i => i.classList.remove('visible'));
                setTimeout(() => renderGallery(filtered), 400);
            };
        });
    }

    // 5. VUE DÉTAIL (Chargement optimisé de la description)
    async function openDetail(photo) {
        document.getElementById('detail-img').src = photo.src;
        document.getElementById('detail-title').textContent = photo.title;
        document.getElementById('detail-category').textContent = photo.category.replace('-', ' • ');
        document.getElementById('detail-year').textContent = photo.year;
        
        const descElement = document.getElementById('detail-desc');
        descElement.textContent = "Chargement...";
        
        detailView.classList.add('open');
        body.style.overflow = 'hidden';

        // Chargement du fichier de descriptions seulement si nécessaire
        if (!allDescriptions) {
            try {
                // On ajoute un timestamp (GALLERY_VERSION) pour forcer le browser à ignorer le cache
                const v = typeof GALLERY_VERSION !== 'undefined' ? GALLERY_VERSION : Date.now();
                const response = await fetch(`data/descriptions.json?v=${v}`);
                allDescriptions = await response.json();
            } catch (e) {
                console.error("Erreur chargement descriptions");
            }
        }

        if (allDescriptions && allDescriptions[photo.id]) {
            descElement.innerHTML = allDescriptions[photo.id].replace(/\n/g, '<br>');
        } else {
            descElement.textContent = "Pas de description disponible.";
        }
    }

    document.getElementById('close-detail').onclick = () => {
        detailView.classList.remove('open');
        body.style.overflow = '';
    };
});
