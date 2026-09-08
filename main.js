

let currentReciter = null;
let currentSurahData = null; 
let displayedVerses = new Set();
let activeScriptTag = null;
function hideAllViews() {
    document.getElementById('reciters-view').classList.remove('active');
    document.getElementById('surahs-view').classList.remove('active');
    document.getElementById('player-view').classList.remove('active');
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
    renderSurahs();
}
function showPlayerView(surah) {
    hideAllViews();
    document.getElementById('player-view').classList.add('active');
    document.getElementById('lyrics-container').innerHTML = '';
    displayedVerses.clear();
    document.getElementById('surah-title').innerText = surah.name;
    document.getElementById('surah-subtitle').innerText = "بصوت الشيخ " + currentReciter.name;
    const audioEl = document.getElementById('quran-audio');
    audioEl.src = surah.audioUrl;
    audioEl.load();
    loadSurahScript(surah.jsFile);
}
function renderReciters() {
    const grid = document.getElementById('reciters-grid');
    grid.innerHTML = '';
    database.forEach(reciter => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<img src="${reciter.image}" alt="${reciter.name}"><h3>${reciter.name}</h3>`;
        card.onclick = () => { currentReciter = reciter; showSurahsView(); };
        grid.appendChild(card);
    });
}
function renderSurahs() {
    const grid = document.getElementById('surahs-grid');
    grid.innerHTML = '';
    currentReciter.surahs.forEach(surah => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<img src="${surah.image || currentReciter.image}" alt="${surah.name}">`;
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
        const audioEl = document.getElementById('quran-audio');
        audioEl.currentTime = 0; 
    };
    
    document.body.appendChild(activeScriptTag);
}
const arabicNumbers = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
function toArabicNumber(num) {
    return num.toString().split('').map(n => arabicNumbers[parseInt(n)]).join('');
}

function typeVerse(verse) {
    if (displayedVerses.has(verse.id)) return;
    displayedVerses.add(verse.id);

    const container = document.getElementById('lyrics-container');
    const wrapper = document.createElement(verse.type === 'bismillah' ? 'div' : 'span');
    wrapper.className = 'verse ' + (verse.type === 'bismillah' ? 'bismillah' : 'aya');
    wrapper.id = 'verse-' + verse.id;
    
    const textSpan = document.createElement('span');
    textSpan.className = 'text-content';
    wrapper.appendChild(textSpan);
    
    container.appendChild(wrapper);
    wrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
}

function addAyaEnd(id, wrapper) {
    const endWrapper = document.createElement('span');
    endWrapper.className = 'aya-end-wrapper';
    endWrapper.innerHTML = `<span class="aya-num">${toArabicNumber(id)}</span><svg class="aya-svg" viewBox="0 0 50 50"><circle cx="25" cy="25" r="20"></circle></svg>`;
    wrapper.appendChild(endWrapper);
    wrapper.appendChild(document.createTextNode(" ")); 
}
let currentActiveVerseId = null;

document.getElementById('quran-audio').addEventListener('timeupdate', function() {
    if (!window.currentSurahVerses || window.currentSurahVerses.length === 0) return;
    
    const currentTime = this.currentTime;
    let activeVerseFound = false;
    
    window.currentSurahVerses.forEach(verse => {
        if (currentTime >= verse.start_time) {
            typeVerse(verse);
            
            const wrapper = document.getElementById('verse-' + verse.id);
            if (wrapper) {
                const textSpan = wrapper.querySelector('.text-content');
                if (textSpan) {
                    const duration = verse.end_time - verse.start_time;
                    const elapsed = currentTime - verse.start_time;
                    let percentComplete = elapsed / duration;
                    
                    if (percentComplete >= 1) percentComplete = 1;
                    
                    const charsToShow = Math.floor(percentComplete * verse.text.length);
                    textSpan.textContent = verse.text.substring(0, charsToShow);
                    
                    if (percentComplete === 1 && verse.type === 'aya' && !wrapper.querySelector('.aya-end-wrapper')) {
                        addAyaEnd(verse.id, wrapper);
                    }
                }
            }
        }
        
        if (currentTime >= verse.start_time && currentTime <= verse.end_time) {
            activeVerseFound = true;
            if (currentActiveVerseId !== verse.id) {
                const prevActive = document.querySelector('.verse.active');
                if (prevActive) prevActive.classList.remove('active');
                
                const currentActive = document.getElementById('verse-' + verse.id);
                if (currentActive) currentActive.classList.add('active');
                
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
showRecitersView();