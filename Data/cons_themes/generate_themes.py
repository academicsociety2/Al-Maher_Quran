import json
import os
import colorsys

def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

themes = {
    "1. دارك": {"bg_color": "#1e1e2e", "text_color": "#cdd6f4", "cover_color": "#313244"},
    "2. دارك2": {"bg_color": "#282a36", "text_color": "#f8f8f2", "cover_color": "#44475a"},
    "3.  الجليدي": {"bg_color": "#2e3440", "text_color": "#eceff4", "cover_color": "#3b4252"},
    "4. جروف بوكس": {"bg_color": "#282828", "text_color": "#ebdbb2", "cover_color": "#3c3836"},
    "5.  هادي": {"bg_color": "#0f2027", "text_color": "#a8e063", "cover_color": "#203a43"},
}


GOLDEN_RATIO = 0.618033988749895

for i in range(6, 3001):
    hue = (i * GOLDEN_RATIO) % 1.0
    s_bg = 0.15 + (i % 20) / 100.0  
    l_bg = 0.08 + (i % 15) / 100.0     
    s_txt = 0.4 + (i % 30) / 100.0     
    l_txt = 0.75 + (i % 15) / 100.0    
    s_cov = min(1.0, s_bg + 0.1)       
    l_cov = min(1.0, l_bg + 0.1)       
    
    bg = hsl_to_hex(hue, s_bg, l_bg)
    txt = hsl_to_hex(hue, s_txt, l_txt)
    cov = hsl_to_hex(hue, s_cov, l_cov)
    
    themes[f"{i}. Theme  {i}"] = {"bg_color": bg, "text_color": txt, "cover_color": cov}

# حفظ الثيمات في الملف
with open("themes.json", "w", encoding="utf-8") as f:
    json.dump(themes, f, ensure_ascii=False, indent=4)

print(f"عاش يسطا! تم إنشاء {len(themes)} ثيم بنجاح في ملف themes.json!")
