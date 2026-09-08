import os

os.makedirs("Data", exist_ok=True)

ar_surahs = [
    "سورة الفاتحة", "سورة البقرة", "سورة آل عمران", "سورة النساء", "سورة المائدة", "سورة الأنعام", "سورة الأعراف", "سورة الأنفال", "سورة التوبة", "سورة يونس",
    "سورة هود", "سورة يوسف", "سورة الرعد", "سورة إبراهيم", "سورة الحجر", "سورة النحل", "سورة الإسراء", "سورة الكهف", "سورة مريم", "سورة طه",
    "سورة الأنبياء", "سورة الحج", "سورة المؤمنون", "سورة النور", "سورة الفرقان", "سورة الشعراء", "سورة النمل", "سورة القصص", "سورة العنكبوت", "سورة الروم",
    "سورة لقمان", "سورة السجدة", "سورة الأحزاب", "سورة سبأ", "سورة فاطر", "سورة يس", "سورة الصافات", "سورة ص", "سورة الزمر", "سورة غافر",
    "سورة فصلت", "سورة الشورى", "سورة الزخرف", "سورة الدخان", "سورة الجاثية", "سورة الأحقاف", "سورة محمد", "سورة الفتح", "سورة الحجرات", "سورة ق",
    "سورة الذاريات", "سورة الطور", "سورة النجم", "سورة القمر", "سورة الرحمن", "سورة الواقعة", "سورة الحديد", "سورة المجادلة", "سورة الحشر", "سورة الممتحنة",
    "سورة الصف", "سورة الجمعة", "سورة المنافقون", "سورة التغابن", "سورة الطلاق", "سورة التحريم", "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج",
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", "سورة القيامة", "سورة الإنسان", "سورة المرسلات", "سورة النبأ", "سورة النازعات", "سورة عبس",
    "سورة التكوير", "سورة الانفطار", "سورة المطففين", "سورة الانشقاق", "سورة البروج", "سورة الطارق", "سورة الأعلى", "سورة الغاشية", "سورة الفجر", "سورة البلد",
    "سورة الشمس", "سورة الليل", "سورة الضحى", "سورة الشرح", "سورة التين", "سورة العلق", "سورة القدر", "سورة البينة", "سورة الزلزلة", "سورة العاديات",
    "سورة القارعة", "سورة التكاثر", "سورة العصر", "سورة الهمزة", "سورة الفيل", "سورة قريش", "سورة الماعون", "سورة الكوثر", "سورة الكافرون", "سورة النصر",
    "سورة المسد", "سورة الإخلاص", "سورة الفلق", "سورة الناس"
]

en_surahs = [
    "alfatihah", "albaqarah", "aalimran", "annisa", "almaidah", "alanam", "araf", "alanfal", "attawbah", "yunus",
    "hud", "yusuf", "arrad", "ibrahim", "alhijr", "annahl", "alisra", "alkahf", "maryam", "taha",
    "alanbiya", "alhajj", "almuminun", "annur", "alfurqan", "ashshuara", "annaml", "alqasas", "alankabut", "arum",
    "luqman", "assajdah", "alahzab", "saba", "fatir", "yaseen", "assaffat", "sad", "azzumar", "ghafir",
    "fussilat", "ashshura", "azzukhruf", "addukhan", "aljathiyah", "alahqaf", "muhammad", "alfath", "alhujurat", "qaf",
    "addhariyat", "attur", "annajm", "alqamar", "arrahman", "alwaqiah", "alhadid", "almujadila", "alhashr", "almumtahanah",
    "assaff", "aljumuah", "almunafiqun", "attaghabun", "attalaq", "attahrim", "almulk", "alqalam", "alhaqqah", "almaarij",
    "nuh", "aljinn", "almuzzammil", "almuddaththir", "alqiyamah", "alinsan", "almursalat", "annaba", "annaziat", "abasa",
    "attakwir", "alinfitar", "almutaffifin", "alinshiqaq", "alburooj", "attariq", "alala", "alghashiyah", "alfajr", "albalad",
    "ashshams", "allayl", "adduha", "ashsharh", "atteen", "alalaq", "alqadr", "albayyinah", "azzalzalah", "aladiyat",
    "alqariah", "attakathur", "alasr", "alhumazah", "alfeel", "quraysh", "almaun", "alkawthar", "alkafirun", "annasr",
    "almasad", "alikhlas", "alfalaq", "alnas"
]

with open("Data/cons_surah_ar.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(ar_surahs))

with open("Data/cons_surah_en.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(en_surahs))

print("تم إنشاء ملفات السور بنجاح في مجلد Data!")