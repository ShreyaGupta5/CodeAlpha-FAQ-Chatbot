/**
 * AlphaBot • Frontend Logic & Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatContainer = document.getElementById('chatContainer');
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userQueryInput = document.getElementById('userQueryInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const welcomeCard = document.getElementById('welcomeCard');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const soundToggleBtn = document.getElementById('soundToggleBtn');
    const speechIcon = document.getElementById('speechIcon');

    // Drawer Elements
    const exploreFaqsBtn = document.getElementById('exploreFaqsBtn');
    const faqModalBackdrop = document.getElementById('faqModalBackdrop');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const faqSearchInput = document.getElementById('faqSearchInput');
    const categoryFilters = document.getElementById('categoryFilters');
    const faqListContainer = document.getElementById('faqListContainer');

    // State
    let speechEnabled = false;
    let allFaqsCache = [];
    let currentCategory = 'all';

    // -------------------------------------------------------------
    // Theme Management
    // -------------------------------------------------------------
    const savedTheme = localStorage.getItem('alphabot_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-theme');
        const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('alphabot_theme', nextTheme);
    });

    // -------------------------------------------------------------
    // Speech Synthesis Toggle
    // -------------------------------------------------------------
    soundToggleBtn.addEventListener('click', () => {
        speechEnabled = !speechEnabled;
        speechIcon.textContent = speechEnabled ? '🔊' : '🔇';
        soundToggleBtn.title = speechEnabled ? 'Voice read-out: ON' : 'Voice read-out: OFF';
    });

    function speakText(text) {
        if (!speechEnabled || !('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel(); // Stop any pending speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }

    // -------------------------------------------------------------
    // Scroll Utilities
    // -------------------------------------------------------------
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // -------------------------------------------------------------
    // Message Rendering
    // -------------------------------------------------------------
    function appendUserMessage(text) {
        const row = document.createElement('div');
        row.className = 'message-row-user';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble-user';
        bubble.textContent = text;
        
        row.appendChild(bubble);
        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function appendBotMessage(data) {
        const row = document.createElement('div');
        row.className = 'message-row-bot';

        const avatar = document.createElement('div');
        avatar.className = 'bot-msg-avatar';
        avatar.textContent = '🤖';

        const body = document.createElement('div');
        body.className = 'message-body-bot';

        // Bot speech bubble
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble-bot';
        bubble.textContent = data.reply;
        body.appendChild(bubble);

        // Metadata Bar
        const metaBar = document.createElement('div');
        metaBar.className = 'bot-meta-bar';

        // Confidence Pill
        const confPill = document.createElement('span');
        const isMatched = data.matched;
        confPill.className = `confidence-pill ${isMatched ? 'confidence-high' : 'confidence-low'}`;
        confPill.innerHTML = `${isMatched ? '✓' : '⚠'} ${data.confidence_percent}% Match`;
        metaBar.appendChild(confPill);

        // Category Tag
        if (data.best_faq && data.best_faq.category) {
            const catTag = document.createElement('span');
            catTag.className = 'category-tag';
            catTag.textContent = data.best_faq.category;
            metaBar.appendChild(catTag);
        }

        // Copy Button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'action-pill-btn';
        copyBtn.innerHTML = '📋 Copy';
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(data.reply);
            copyBtn.innerHTML = '✓ Copied!';
            setTimeout(() => { copyBtn.innerHTML = '📋 Copy'; }, 2000);
        });
        metaBar.appendChild(copyBtn);

        // Speak aloud button
        const speakBtn = document.createElement('button');
        speakBtn.className = 'action-pill-btn';
        speakBtn.innerHTML = '🔊 Speak';
        speakBtn.addEventListener('click', () => {
            speakText(data.reply);
        });
        metaBar.appendChild(speakBtn);

        body.appendChild(metaBar);

        // Suggestions block (if any)
        if (data.suggestions && data.suggestions.length > 0) {
            const sugBox = document.createElement('div');
            sugBox.className = 'bot-suggestions-box';

            const sugTitle = document.createElement('div');
            sugTitle.className = 'suggestions-title';
            sugTitle.textContent = isMatched ? 'Related Questions:' : 'Did you mean:';
            sugBox.appendChild(sugTitle);

            const list = document.createElement('div');
            list.className = 'suggestions-list';

            data.suggestions.forEach(item => {
                const btn = document.createElement('button');
                btn.className = 'suggestion-item-btn';
                btn.innerHTML = `<span>${item.question}</span><span class="suggestion-arrow">→</span>`;
                btn.addEventListener('click', () => {
                    handleSendMessage(item.question);
                });
                list.appendChild(btn);
            });

            sugBox.appendChild(list);
            body.appendChild(sugBox);
        }

        row.appendChild(avatar);
        row.appendChild(body);
        chatMessages.appendChild(row);
        scrollToBottom();

        // Speak response if enabled
        if (speechEnabled) {
            speakText(data.reply);
        }
    }

    // -------------------------------------------------------------
    // Send Message Handler
    // -------------------------------------------------------------
    async function handleSendMessage(messageText) {
        const text = (messageText || userQueryInput.value).trim();
        if (!text) return;

        // Hide welcome card once chat starts
        if (welcomeCard) {
            welcomeCard.style.display = 'none';
        }

        appendUserMessage(text);
        userQueryInput.value = '';
        userQueryInput.focus();

        // Show typing indicator
        typingIndicator.classList.add('active');
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            typingIndicator.classList.remove('active');

            if (data.status === 'success') {
                appendBotMessage(data);
            } else {
                appendBotMessage({
                    reply: data.reply || "An unexpected error occurred. Please try again.",
                    matched: false,
                    confidence_percent: 0,
                    suggestions: []
                });
            }
        } catch (error) {
            typingIndicator.classList.remove('active');
            appendBotMessage({
                reply: "Unable to connect to the FAQ server. Please make sure Flask is running.",
                matched: false,
                confidence_percent: 0,
                suggestions: []
            });
            console.error('Chat error:', error);
        }
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSendMessage();
    });

    // -------------------------------------------------------------
    // Quick Prompt Chips in Welcome Card
    // -------------------------------------------------------------
    document.querySelectorAll('.prompt-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            handleSendMessage(query);
        });
    });

    // -------------------------------------------------------------
    // Clear Chat
    // -------------------------------------------------------------
    clearChatBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear your current conversation?')) return;
        
        try {
            await fetch('/api/reset', { method: 'POST' });
        } catch (e) {
            console.warn(e);
        }

        chatMessages.innerHTML = '';
        if (welcomeCard) {
            welcomeCard.style.display = 'flex';
            chatMessages.appendChild(welcomeCard);
        }
    });

    // -------------------------------------------------------------
    // FAQ Drawer & Catalog Explorer
    // -------------------------------------------------------------
    async function loadFaqCatalog() {
        if (allFaqsCache.length > 0) return;
        try {
            const res = await fetch('/api/faqs');
            const data = await res.json();
            if (data.status === 'success') {
                allFaqsCache = data.faqs;
                renderCategoryFilters(data.categories);
                renderFaqList(allFaqsCache);
            }
        } catch (err) {
            console.error('Failed to load FAQs:', err);
        }
    }

    function renderCategoryFilters(categories) {
        categoryFilters.innerHTML = '';
        
        // "All" pill
        const allBtn = document.createElement('button');
        allBtn.className = 'cat-filter-chip active';
        allBtn.textContent = 'All Topics';
        allBtn.addEventListener('click', () => {
            document.querySelectorAll('.cat-filter-chip').forEach(c => c.classList.remove('active'));
            allBtn.classList.add('active');
            currentCategory = 'all';
            filterAndRenderFaqs();
        });
        categoryFilters.appendChild(allBtn);

        // Specific category pills
        Object.keys(categories).forEach(cat => {
            const btn = document.createElement('button');
            btn.className = 'cat-filter-chip';
            btn.textContent = cat;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.cat-filter-chip').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                currentCategory = cat;
                filterAndRenderFaqs();
            });
            categoryFilters.appendChild(btn);
        });
    }

    function filterAndRenderFaqs() {
        const query = faqSearchInput.value.toLowerCase().trim();
        const filtered = allFaqsCache.filter(item => {
            const matchesCategory = (currentCategory === 'all') || (item.category === currentCategory);
            const matchesSearch = !query || 
                item.question.toLowerCase().includes(query) || 
                item.answer.toLowerCase().includes(query);
            return matchesCategory && matchesSearch;
        });
        renderFaqList(filtered);
    }

    function renderFaqList(faqs) {
        faqListContainer.innerHTML = '';
        if (faqs.length === 0) {
            faqListContainer.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;padding:12px;">No matching FAQs found.</p>';
            return;
        }

        faqs.forEach(faq => {
            const card = document.createElement('div');
            card.className = 'faq-card-item';
            card.innerHTML = `
                <div class="faq-card-header">
                    <span class="faq-card-category">${faq.category || 'General'}</span>
                    <span style="font-size:0.75rem;color:var(--primary);">Ask ↗</span>
                </div>
                <div class="faq-card-question">${faq.question}</div>
                <div class="faq-card-answer">${faq.answer}</div>
            `;
            card.addEventListener('click', () => {
                faqModalBackdrop.classList.remove('open');
                handleSendMessage(faq.question);
            });
            faqListContainer.appendChild(card);
        });
    }

    exploreFaqsBtn.addEventListener('click', () => {
        faqModalBackdrop.classList.add('open');
        loadFaqCatalog();
    });

    closeModalBtn.addEventListener('click', () => {
        faqModalBackdrop.classList.remove('open');
    });

    faqModalBackdrop.addEventListener('click', (e) => {
        if (e.target === faqModalBackdrop) {
            faqModalBackdrop.classList.remove('open');
        }
    });

    faqSearchInput.addEventListener('input', filterAndRenderFaqs);
});
