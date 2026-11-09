package com.knuckls.gateshield.browser;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class MainActivity extends Activity {

    private static final String HOME = "https://knuckls.com/gateshield/";

    private TextView verdict, status, blockScreen;
    private EditText urlBox;
    private LinearLayout tabStrip;
    private FrameLayout tabContainer;

    private static class Tab {
        WebView web; LinearLayout chip; String title = "New Tab";
    }
    private final ArrayList<Tab> tabs = new ArrayList<>();
    private int active = -1;

    // ---- AdGuard DNS verdict lookup (same engine as router-level blocking) ----
    private static final String DOH = "https://dns.adguard-dns.com/resolve?name=";

    // ---- baked-in tracker/ad blocklist (fast path, no network needed) ----
    private static final String[] BLOCK_SUFFIX = {
        "doubleclick.net","googlesyndication.com","googleadservices.com",
        "google-analytics.com","googletagmanager.com","adservice.google.com",
        "adnxs.com","adsrvr.org","criteo.com","criteo.net","outbrain.com",
        "taboola.com","pubmatic.com","rubiconproject.com","openx.net",
        "scorecardresearch.com","quantserve.com","hotjar.com","crazyegg.com",
        "moatads.com","adcolony.com","applovin.com","unityads.unity3d.com",
        "chartboost.com","inmobi.com","facebook.net","connect.facebook.net",
        "analytics.tiktok.com","snap.licdn.com","bat.bing.com","clarity.ms",
        "yieldmo.com","smartadserver.com","sharethrough.com","indexww.com",
        "casalemedia.com","33across.com","bidswitch.net","zedo.com"
    };
    private static final String[] MALWARE_HINTS = {
        "coinhive","cryptoloot","jsecoin","drugspowerstore","accountkit-secure",
        "steamcomunity","appleid-apple","paypa1","amaz0n-secure","netflix-billing"
    };
    private final Set<String> blockCache = new HashSet<>();

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        verdict = findViewById(R.id.verdictBar);
        status = findViewById(R.id.statusLine);
        blockScreen = findViewById(R.id.blockScreen);
        urlBox = findViewById(R.id.urlBox);
        tabStrip = findViewById(R.id.tabStrip);
        tabContainer = findViewById(R.id.tabContainer);

        findViewById(R.id.btnGo).setOnClickListener(x -> navigate());
        urlBox.setOnEditorActionListener((v, a, e) -> { navigate(); return true; });
        findViewById(R.id.btnBack).setOnClickListener(x -> {
            if (active >= 0 && tabs.get(active).web.canGoBack()) tabs.get(active).web.goBack();
        });
        blockScreen.setOnClickListener(x -> hideBlock());
        findViewById(R.id.btnOL).setOnClickListener(x -> openOneLock());
        findViewById(R.id.btnNewTab).setOnClickListener(x -> newTab(HOME));
        findViewById(R.id.btnGear).setOnClickListener(x ->
            startActivity(new android.content.Intent(this, SettingsActivity.class)));
        urlBox.setOnClickListener(x -> urlBox.selectAll());

        newTab(getIntent() != null && getIntent().getData() != null
                ? getIntent().getData().toString() : HOME);
    }

    // ================= TABS =================

    private void newTab(String url) {
        Tab t = new Tab();
        t.web = new WebView(this);
        WebSettings s = t.web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setSafeBrowsingEnabled(true); // Chromium's own malware/phishing DB as backstop
        t.web.setLayoutParams(new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        t.web.setBackgroundColor(Color.parseColor("#0d1117"));
        t.web.setWebViewClient(new ShieldClient(t));
        tabContainer.addView(t.web);

        // chip
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackgroundResource(R.drawable.tab_chip);
        row.setPadding(14, 4, 8, 4);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(2, 0, 2, 0);
        row.setLayoutParams(lp);

        TextView title = new TextView(this);
        title.setTextSize(12); title.setTextColor(Color.parseColor("#e6edf3"));
        title.setTypeface(android.graphics.Typeface.MONOSPACE);
        title.setMaxWidth(220); title.setSingleLine(true);
        row.addView(title);
        t.chip = row;
        row.setTag(title);

        row.setOnClickListener(x -> switchTab(tabs.indexOf(t)));
        TextView close = new TextView(this);
        close.setText(" ✕"); close.setTextColor(Color.parseColor("#8b949e"));
        close.setTextSize(13); close.setPadding(8, 0, 0, 0);
        close.setOnClickListener(x -> closeTab(tabs.indexOf(t)));
        row.addView(close);

        tabStrip.addView(row);
        tabs.add(t);
        switchTab(tabs.size() - 1);
        if (url != null) t.web.loadUrl(url);
    }

    private void switchTab(int i) {
        if (i < 0 || i >= tabs.size()) return;
        active = i;
        for (int k = 0; k < tabs.size(); k++) {
            Tab t = tabs.get(k);
            t.web.setVisibility(k == i ? View.VISIBLE : View.GONE);
            boolean isAct = k == i;
            t.chip.setBackgroundResource(isAct ? R.drawable.tab_chip_on : R.drawable.tab_chip);
            ((TextView) t.chip.getTag()).setTextColor(Color.parseColor(isAct ? "#3fb950" : "#e6edf3"));
        }
        Tab t = tabs.get(i);
        String u = t.web.getUrl();
        urlBox.setText(u == null ? "" : u);
        if (u != null) setVerdictFor(u);
        blockScreen.setVisibility(View.GONE);
    }

    private void closeTab(int i) {
        if (i < 0 || i >= tabs.size()) return;
        Tab t = tabs.get(i);
        tabStrip.removeView(t.chip);
        tabContainer.removeView(t.web);
        t.web.destroy();
        tabs.remove(i);
        if (tabs.isEmpty()) { finish(); return; }
        switchTab(active >= tabs.size() ? tabs.size() - 1 : active);
    }

    // ================= SHIELD =================

    private class ShieldClient extends WebViewClient {
        final Tab tab;
        ShieldClient(Tab t) { tab = t; }

        @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
            if (blockedHost(r.getUrl().getHost())) { if (tabs.indexOf(tab) == active) showBlock(); return true; }
            if (tabs.indexOf(tab) == active) hideBlock();
            return false;
        }
        @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
            String host = r.getUrl().getHost();
            if (host != null && blockedHost(host)) {
                blockCache.add(host);
                runOnUiThread(() -> {
                    if (tabs.indexOf(tab) == active)
                        status.setText("⛔ blocked: " + host + " · " + blockCache.size() + " blocked this session");
                });
                return empty();
            }
            return null;
        }
        @Override public void onPageStarted(WebView v, String u, Bitmap f) {
            tab.title = title(u);
            ((TextView) tab.chip.getTag()).setText(tab.title);
            if (tabs.indexOf(tab) == active) {
                urlBox.setText(u);
                setVerdict("🔎 checking " + host(u) + " …", "#d29922");
                ShieldCheck.check(host(u), result -> runOnUiThread(() -> {
                    if (tabs.indexOf(tab) != active) return;
                    if (result.bad) {
                        setVerdict("⛔ " + host(u) + " — " + result.reason, "#f85149");
                        if (new Prefs(MainActivity.this).malware) { showBlock(); v.stopLoading(); }
                    } else if (result.ad) {
                        setVerdict("⚠ ads/trackers blocked on " + host(u), "#d29922");
                    } else {
                        setVerdict("🛡 " + host(u) + " — clean", "#3fb950");
                    }
                }));
            }
        }
        @Override public void onPageFinished(WebView v, String u) {
            if (tabs.indexOf(tab) == active)
                status.setText("ad+tracker blocking: ON · " + blockCache.size() + " requests blocked this session");
        }
    }

    private void setVerdictFor(String u) { setVerdict("🛡 " + host(u), "#3fb950"); }

    private void openOneLock() {
        try {
            Intent i = getPackageManager().getLaunchIntentForPackage("com.knuckls.onelock");
            if (i != null) { i.putExtra("browser_integration", true); startActivity(i); }
            else Toast.makeText(this, "OneLock not installed", Toast.LENGTH_SHORT).show();
        } catch (Exception e) { Toast.makeText(this, "OneLock not installed", Toast.LENGTH_SHORT).show(); }
    }

    private void navigate() {
        String q = urlBox.getText().toString().trim();
        if (q.isEmpty() || active < 0) return;
        if (!q.contains(".") || q.contains(" ")) {
            load(new Prefs(this).searchUrl(q));
        } else {
            load(q.startsWith("http") ? q : "https://" + q);
        }
    }

    private void load(String u) {
        hideBlock();
        tabs.get(active).web.loadUrl(u);
    }

    private boolean blockedHost(String host) {
        if (host == null) return false;
        if (!new Prefs(this).ads) return false;
        String h = host.toLowerCase();
        for (String suffix : BLOCK_SUFFIX) if (h.equals(suffix) || h.endsWith("." + suffix)) return true;
        for (String hint : MALWARE_HINTS) if (h.contains(hint)) return true;
        return false;
    }

    private void showBlock() {
        verdict.setText("⛔ BLOCKED — malicious site");
        verdict.setTextColor(0xfff85149);
        blockScreen.setVisibility(View.VISIBLE);
        tabs.get(active).web.stopLoading();
    }
    private void hideBlock() { blockScreen.setVisibility(View.GONE); }
    private void setVerdict(String t, String color) { verdict.setText(t); verdict.setTextColor(Color.parseColor(color)); }
    private static String host(String u) { try { return Uri.parse(u).getHost(); } catch (Exception e) { return u; } }
    private static String title(String u) {
        String h = host(u);
        return h == null ? u : h.replaceFirst("^www\\.", "");
    }

    private static WebResourceResponse empty() {
        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));
    }

    @Override public boolean onKeyDown(int c, KeyEvent e) {
        if (c == KeyEvent.KEYCODE_BACK && active >= 0) {
            Tab t = tabs.get(active);
            if (blockScreen.getVisibility() == View.VISIBLE) {
                hideBlock();
                if (t.web.canGoBack()) t.web.goBack();
                return true;
            }
            if (t.web.canGoBack()) { t.web.goBack(); return true; }
            if (tabs.size() > 1) { closeTab(active); return true; }
        }
        return super.onKeyDown(c, e);
    }

    @Override protected void onDestroy() {
        for (Tab t : tabs) t.web.destroy();
        tabs.clear();
        super.onDestroy();
    }

    // ---- async DNS-over-HTTPS check against AdGuard's filtering resolvers ----
    interface Cb { void done(Result r); }
    static class Result { boolean bad, ad; String reason = ""; }

    static class ShieldCheck {
        static void check(String domain, Cb cb) {
            if (domain == null) { cb.done(new Result()); return; }
            new Thread(() -> {
                Result r = new Result();
                try {
                    java.net.HttpURLConnection c = (java.net.HttpURLConnection)
                        new java.net.URL(DOH + domain + "&type=A").openConnection();
                    c.setRequestProperty("Accept", "application/dns-json");
                    c.setConnectTimeout(4000); c.setReadTimeout(4000);
                    StringBuilder sb = new StringBuilder();
                    try (java.io.InputStream in = c.getInputStream()) {
                        int ch; while ((ch = in.read()) != -1) sb.append((char) ch);
                    }
                    String json = sb.toString();
                    if (json.contains("\"data\":\"94.140.14.") || json.contains("\"data\":\"0.0.0.0\"")) {
                        r.bad = true; r.reason = "known malicious/ads domain";
                    } else if (json.contains("\"AD\":true")) {
                        r.ad = true;
                    }
                } catch (Exception ignored) { }
                cb.done(r);
            }).start();
        }
    }
}
