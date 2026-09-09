

let currentReciter = null;
let currentSurahData = null; 
let displayedVerses = new Set();
let activeScriptTag = null;
let surahEndTime = 0;
let hasShownCompletionModal = false;
function hideAllViews() {
    document.getElementById('reciters-view').classList.remove('active');
    document.getElementById('surahs-view').classList.remove('active');
    document.getElementById('player-view').classList.remove('active');
    hideCompletionModal();
    document.getElementById('quran-audio').pause(); 
}

function showRecitersView() {
    hideAllViews();
    document.getElementById('reciters-view').classList.add('active');
    renderReciters();
}

function showSurahsView() {
    if (!currentReciter) return;
    hideAllViews();
    document.getElementById('surahs-view').classList.add('active');
    document.getElementById('selected-reciter-name').innerText = "سور بصوت: " + currentReciter.name;
    document.getElementById('surah-search').value = '';
    const surahClear = document.getElementById('surah-clear');
    if (surahClear) surahClear.style.display = 'none';
    renderSurahs();
}
function showPlayerView(surah) {
    hideAllViews();
    document.getElementById('player-view').classList.add('active');
    document.getElementById('lyrics-container').innerHTML = '';
    displayedVerses.clear();
    surahEndTime = 0;
    hasShownCompletionModal = false;
    document.getElementById('surah-title').innerText = surah.name;
    document.getElementById('surah-subtitle').innerText = "بصوت الشيخ " + currentReciter.name;
    const audioEl = document.getElementById('quran-audio');
    audioEl.src = surah.audioUrl;
    audioEl.load();
    
    document.getElementById('progress-bar').value = 0;
    document.getElementById('current-time').innerText = "0:00";
    document.getElementById('total-time').innerText = "0:00";
    
    loadSurahScript(surah.jsFile);
}
function renderReciters(searchTerm = '') {
    const grid = document.getElementById('reciters-grid');
    grid.innerHTML = '';
    const filtered = database.filter(r => r.name.includes(searchTerm.trim()));
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1.5-10c.83 0 1.5-.67 1.5-1.5S11.33 7 10.5 7 9 7.67 9 8.5s.67 1.5 1.5 1.5zm3 0c.83 0 1.5-.67 1.5-1.5S14.33 7 13.5 7 12 7.67 12 8.5s.67 1.5 1.5 1.5zm-1.5 4c-2.33 0-4.31 1.46-5.11 3.5h10.22c-.8-2.04-2.78-3.5-5.11-3.5z"/></svg>
                <div>عذراً، لم يتم العثور على نتائج</div>
            </div>`;
        return;
    }
    filtered.forEach(reciter => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<img src="${reciter.image}" alt="${reciter.name}"><h3>${reciter.name}</h3>`;
        card.onclick = () => { currentReciter = reciter; showSurahsView(); };
        grid.appendChild(card);
    });
}
function renderSurahs(searchTerm = '') {
    const grid = document.getElementById('surahs-grid');
    grid.innerHTML = '';
    const filtered = currentReciter.surahs.filter(s => s.name.includes(searchTerm.trim()));
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1.5-10c.83 0 1.5-.67 1.5-1.5S11.33 7 10.5 7 9 7.67 9 8.5s.67 1.5 1.5 1.5zm3 0c.83 0 1.5-.67 1.5-1.5S14.33 7 13.5 7 12 7.67 12 8.5s.67 1.5 1.5 1.5zm-1.5 4c-2.33 0-4.31 1.46-5.11 3.5h10.22c-.8-2.04-2.78-3.5-5.11-3.5z"/></svg>
                <div>عذراً، لم يتم العثور على نتائج</div>
            </div>`;
        return;
    }
    filtered.forEach(surah => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<img src="${surah.image || currentReciter.image}" alt="${surah.name}">`;
        card.onmouseenter = () => { const link = document.createElement('link'); link.rel = 'preload'; link.as = 'script'; link.href = surah.jsFile; document.head.appendChild(link); };
        card.onclick = () => { showPlayerView(surah); };
        grid.appendChild(card);
    });
}
function loadSurahScript(scriptUrl) {
    if (activeScriptTag) {
        document.body.removeChild(activeScriptTag);
    }
    window.currentSurahVerses = []; 
    
    activeScriptTag = document.createElement('script');
    activeScriptTag.src = scriptUrl;
    
    activeScriptTag.onload = function() {
        console.log("تم تحميل بيانات السورة بنجاح");
        if (window.currentSurahVerses && window.currentSurahVerses.length > 0) {
            const fragment = document.createDocumentFragment();
            window.currentSurahVerses.forEach(verse => {
                const verseEl = createVerseElement(verse);
                if (verseEl) fragment.appendChild(verseEl);
            });
            document.getElementById('lyrics-container').appendChild(fragment);
            surahEndTime = Math.max(...window.currentSurahVerses.map(v => v.end_time));
            document.getElementById('total-time').innerText = formatTime(surahEndTime);
        }
        const audioEl = document.getElementById('quran-audio');
        audioEl.currentTime = 0; 
    };
    
    document.body.appendChild(activeScriptTag);
}
const arabicNumbers = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
function toArabicNumber(num) {
    return num.toString().split('').map(n => arabicNumbers[parseInt(n)]).join('');
}

function createVerseElement(verse) {
    if (displayedVerses.has(verse.id)) return null;
    displayedVerses.add(verse.id);

    const wrapper = document.createElement(verse.type === 'bismillah' ? 'div' : 'span');
    wrapper.className = 'verse ' + (verse.type === 'bismillah' ? 'bismillah' : 'aya');
    wrapper.id = 'verse-' + verse.id;
    
    const textSpan = document.createElement('span');
    textSpan.className = 'text-content';
    textSpan.textContent = verse.text;
    wrapper.appendChild(textSpan);
    
    if (verse.type === 'aya') {
        addAyaEnd(verse.id, wrapper);
    }

    return wrapper;
}

function addAyaEnd(id, wrapper) {
    const endWrapper = document.createElement('span');
    endWrapper.className = 'aya-end-wrapper';
    endWrapper.innerHTML = `<span class="aya-num">${toArabicNumber(id)}</span><svg class="aya-svg" viewBox="0 0 50 50"><circle cx="25" cy="25" r="20"></circle></svg>`;
    wrapper.appendChild(endWrapper);
    wrapper.appendChild(document.createTextNode(" ")); 
}
let currentActiveVerseId = null;

function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return m + ":" + (s < 10 ? "0" : "") + s;
}

document.getElementById('quran-audio').addEventListener('timeupdate', function() {
    const audioEl = this;
    const progress = document.getElementById('progress-bar');
    const maxTime = surahEndTime > 0 ? surahEndTime : (audioEl.duration || 0);

    if (maxTime > 0) {
        progress.value = Math.min((audioEl.currentTime / maxTime) * 100, 100);
        document.getElementById('current-time').innerText = formatTime(Math.min(audioEl.currentTime, maxTime));
    }

    if (surahEndTime > 0 && audioEl.currentTime >= surahEndTime) {
        if (!hasShownCompletionModal) {
            hasShownCompletionModal = true;
            audioEl.pause();
            audioEl.currentTime = surahEndTime;
            showCompletionModal();
        }
        return;
    }

    if (audioEl.currentTime < surahEndTime - 0.5) {
        hasShownCompletionModal = false;
    }

    if (!window.currentSurahVerses || window.currentSurahVerses.length === 0) return;
    
    const currentTime = this.currentTime;
    let activeVerseFound = false;
    
    window.currentSurahVerses.forEach(verse => {
        if (currentTime >= verse.start_time && currentTime <= verse.end_time) {
            activeVerseFound = true;
            if (currentActiveVerseId !== verse.id) {
                const prevActive = document.querySelector('.verse.active');
                if (prevActive) prevActive.classList.remove('active');
                
                const currentActive = document.getElementById('verse-' + verse.id);
                if (currentActive) {
                    currentActive.classList.add('active');
                    currentActive.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                currentActiveVerseId = verse.id;
            }
        }
    });
    
    if (!activeVerseFound && currentActiveVerseId !== null) {
        const prevActive = document.querySelector('.verse.active');
        if (prevActive) prevActive.classList.remove('active');
        currentActiveVerseId = null;
    }
});
function downloadPDF() {
    const element = document.getElementById('mushaf-target');
    html2pdf(element, {
        margin: 10,
        filename: 'سورة.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    });
}

function copyText() {
    if(!window.currentSurahVerses) return;
    const fullText = window.currentSurahVerses.map(v => v.text).join(' ۝ ') + ' ۝';
    navigator.clipboard.writeText(fullText).then(() => alert('تم النسخ بنجاح!'));
}

function downloadText() {
    if(!window.currentSurahVerses) return;
    const fullText = window.currentSurahVerses.map(v => v.text).join(' ۝ ') + ' ۝';
    const blob = new Blob([fullText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "سورة.txt";
    link.click();
}

document.getElementById('quran-audio').addEventListener('loadedmetadata', function() {
    const maxTime = surahEndTime > 0 ? surahEndTime : (this.duration || 0);
    document.getElementById('total-time').innerText = formatTime(maxTime);
});

document.getElementById('quran-audio').addEventListener('play', function() {
    document.getElementById('play-icon').style.display = 'none';
    document.getElementById('pause-icon').style.display = 'block';
});

document.getElementById('quran-audio').addEventListener('pause', function() {
    document.getElementById('play-icon').style.display = 'block';
    document.getElementById('pause-icon').style.display = 'none';
});

document.getElementById('quran-audio').addEventListener('ended', function() {
    document.getElementById('progress-bar').value = 0;
    document.getElementById('current-time').innerText = "0:00";
});

document.getElementById('play-pause-btn').addEventListener('click', function() {
    const audioEl = document.getElementById('quran-audio');
    if (audioEl.paused) {
        audioEl.play().catch(error => console.log("خطأ في تشغيل الصوت أو الرابط غير صحيح:", error));
    } else {
        audioEl.pause();
    }
});

document.getElementById('progress-bar').addEventListener('input', function() {
    const audioEl = document.getElementById('quran-audio');
    const maxTime = surahEndTime > 0 ? surahEndTime : (audioEl.duration || 0);
    if (maxTime > 0) {
        audioEl.currentTime = (this.value / 100) * maxTime;
        if (audioEl.currentTime < surahEndTime) {
            hasShownCompletionModal = false;
        }
    }
});

function showCompletionModal() {
    document.getElementById('completion-modal').classList.add('active');
}

function hideCompletionModal() {
    document.getElementById('completion-modal').classList.remove('active');
}

document.getElementById('reciter-search').addEventListener('input', (e) => {
    renderReciters(e.target.value);
});

document.getElementById('surah-search').addEventListener('input', (e) => {
    renderSurahs(e.target.value);
});

function setupSearchControls(inputId, clearId, micId, renderFunc) {
    const input = document.getElementById(inputId);
    const clearBtn = document.getElementById(clearId);
    const micBtn = document.getElementById(micId);

    if (!input) return;

    input.addEventListener('input', (e) => {
        const val = e.target.value;
        clearBtn.style.display = val ? 'block' : 'none';
        renderFunc(val);
    });

    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        renderFunc('');
        input.focus();
    });

    if (micBtn) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            micBtn.style.display = 'none';
        } else {
            micBtn.addEventListener('click', () => {
                const recognition = new SpeechRecognition();
                recognition.lang = 'ar-SA';
                recognition.interimResults = false;

                recognition.onstart = () => {
                    micBtn.classList.add('listening');
                };

                recognition.onend = () => {
                    micBtn.classList.remove('listening');
                };

                recognition.onresult = (event) => {
                    let transcript = event.results[0][0].transcript.trim();
                    transcript = transcript.replace(/^سورة\s+/g, '').replace(/^الشيخ\s+/g, '').trim();
                    input.value = transcript;
                    clearBtn.style.display = transcript ? 'block' : 'none';
                    renderFunc(transcript);
                };

                recognition.onerror = () => {
                    micBtn.classList.remove('listening');
                };

                recognition.start();
            });
        }
    }
}

setupSearchControls('reciter-search', 'reciter-clear', 'reciter-mic', renderReciters);
setupSearchControls('surah-search', 'surah-clear', 'surah-mic', renderSurahs);

showRecitersView();