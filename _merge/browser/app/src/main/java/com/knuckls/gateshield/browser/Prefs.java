package com.knuckls.gateshield.browser;

import android.content.Context;
import android.content.SharedPreferences;

public class Prefs {
    final SharedPreferences sp;
    final boolean ads, malware;
    final int engine; // 0=ddg 1=bing 2=google

    Prefs(Context c) {
        sp = c.getSharedPreferences("gateshield", Context.MODE_PRIVATE);
        ads = sp.getBoolean("ads", true);
        malware = sp.getBoolean("malware", true);
        engine = sp.getInt("engine", 0);
    }

    void setAds(boolean v) { sp.edit().putBoolean("ads", v).apply(); }
    void setMalware(boolean v) { sp.edit().putBoolean("malware", v).apply(); }
    void setEngine(int v) { sp.edit().putInt("engine", v).apply(); }

    String searchUrl(String q) {
        String e = Uri_enc(q);
        switch (engine) {
            case 1: return "https://www.bing.com/search?q=" + e;
            case 2: return "https://www.google.com/search?q=" + e;
            default: return "https://duckduckgo.com/?q=" + e;
        }
    }
    private static String Uri_enc(String s) { return android.net.Uri.encode(s); }
}
