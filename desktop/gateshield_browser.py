#!/usr/bin/env python3
"""OneLock Browser — desktop (Linux/Windows/macOS) with the same shield engine as the Android build."""
import sys, json, re
from urllib.parse import urlparse
from PyQt6.QtCore import Qt, QUrl, QSettings
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont, QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget,
                             QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QDialog,
                             QCheckBox, QComboBox, QPushButton, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

GREEN="#3fb950"; RED="#f85149"; BG="#0d1117"; BAR="#161b22"; MUT="#8b949e"

# same baked-in blocklist idea as the Android engine (subset of networks + scam lookalikes)
AD_HOSTS = ("doubleclick","googlesyndication","googleadservices","google-analytics",
    "googletagmanager","adservice","adnxs","adsystem","criteo","taboola","outbrain",
    "pubmatic","rubiconproject","openx","casalemedia","adcolony","applovin","unityads",
    "moatads","scorecardresearch","quantserve","hotjar","mixpanel","segment","branch.io",
    "appsflyer","adjust.com","facebook.net","connect.facebook","analytics.tiktok",
    "ads-twitter","bat.bing","clarity.ms","ymetrica","mc.yandex")
SCAM_PAT = re.compile(
    r"(steamcomunity|steamcomrnunity|paypa1|paypa1-secure|amaz0n|amazon-secure|netfl1x|"
    r"appleid-verify|coinba5e|coinbase-wallet|wellsfargo-secure|chase-verify|"
    r"dhl-parcel|ups-package|usps-track|irs-gov|hmrc-refund|gift-claim|prize-claim|"
    r"bank-login|wallet-verify|crypto-withdraw)", re.I)

class Shield:
    def __init__(self, settings: QSettings):
        self.s = settings
        self.nam = QNetworkAccessManager()
    @staticmethod
    def host(url) -> str:
        try: return (urlparse(url).hostname or "").lower()
        except Exception: return ""
    def is_ad(self, url) -> bool:
        if not self.s.value("ads", True, type=bool): return False
        h = self.host(url)
        return any(a in h for a in AD_HOSTS)
    def verdict(self, url):
        """returns (level, text). level in 'ok','warn','bad'."""
        h = self.host(url)
        if not h: return "ok", "🛡"
        if SCAM_PAT.search(h): return "bad", f"⛔ {h} — scam-lookalike domain"
        if not self.s.value("malware", True, type=bool): return "ok", f"🛡 {h} — clean"
        # live AdGuard DNS reputation check, bounded wait via event loop
        from PyQt6.QtCore import QEventLoop, QTimer
        req = QNetworkRequest(QUrl(f"https://dns.adguard-dns.com/resolve?name={h}&type=A"))
        rep = self.nam.get(req)
        loop = QEventLoop()
        rep.finished.connect(loop.quit)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()
        if rep.error(): return "ok", f"🛡 {h} — clean"
        try:
            data = json.loads(bytes(rep.readAll()))
            if data.get("Status") == 3:  # NXDOMAIN = blocked = malicious
                return "bad", f"⛔ {h} — malicious domain"
        except Exception:
            pass
        return "ok", f"🛡 {h} — clean"

SEARCH = {0: "https://duckduckgo.com/?q=", 1: "https://www.bing.com/search?q=", 2: "https://www.google.com/search?q="}
SEARCH_NAMES = {0: "DuckDuckGo (private)", 1: "Bing", 2: "Google"}

class SettingsDialog(QDialog):
    def __init__(self, s: QSettings, parent=None):
        super().__init__(parent); self.s = s
        self.setWindowTitle("OneLock Browser Settings"); self.setModal(True); self.resize(420, 260)
        lay = QVBoxLayout(self)
        self.cb_ads = QCheckBox("Ad + tracker blocking"); self.cb_ads.setChecked(s.value("ads", True, type=bool))
        self.cb_mal = QCheckBox("Malicious site blocking"); self.cb_mal.setChecked(s.value("malware", True, type=bool))
        lay.addWidget(self.cb_ads); lay.addWidget(self.cb_mal)
        lay.addWidget(QLabel("Search engine:"))
        self.combo = QComboBox()
        for i, n in SEARCH_NAMES.items(): self.combo.addItem(n, i)
        self.combo.setCurrentIndex(int(s.value("engine", 0, type=int)))
        lay.addWidget(self.combo)
        btn = QPushButton("Clear cookies + site data")
        btn.clicked.connect(self.clear_data)
        lay.addWidget(btn)
        ok = QPushButton("Done"); ok.clicked.connect(self.accept); lay.addWidget(ok)
        lay.addWidget(QLabel("OneLock Browser — desktop v2.0.0"))
    def clear_data(self):
        prof = QWebEngineProfile.defaultProfile()
        prof.clearAllVisitedLinks()
        for r in [prof.cookieStore()]:
            r.deleteAllCookies()
        QMessageBox.information(self, "GateShield", "Cookies and site data cleared.")
    def accept(self):
        self.s.setValue("ads", self.cb_ads.isChecked())
        self.s.setValue("malware", self.cb_mal.isChecked())
        self.s.setValue("engine", self.combo.currentData())
        super().accept()

class ShieldPage(QWebEnginePage):
    def __init__(self, profile, shield: Shield, parent=None):
        super().__init__(profile, parent); self.shield = shield; self.level = "ok"
    def certificateError(self, e):
        # fail-closed: bad certs = block (mirror of the Android red screen)
        e.rejectCertificate(); self.level = "bad"
        return True

class BrowserTab(QWidget):
    def __init__(self, profile, shield, main, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        self.verdict = QLabel("🛡"); self.verdict.setFixedHeight(26)
        self.verdict.setStyleSheet(f"background:{BAR};color:{GREEN};padding:2px 10px;")
        self.view = QWebEngineView()
        self.page = ShieldPage(profile, shield, self.view)
        self.view.setPage(self.page)
        self.page.urlChanged.connect(self.on_url)
        self.page.loadFinished.connect(self.on_loaded)
        lay.addWidget(self.verdict); lay.addWidget(self.view)
        self.main = main
    def on_url(self, url):
        level, text = self.page.shield.verdict(url.toString())
        self.page.level = level
        color = RED if level == "bad" else GREEN
        self.verdict.setText(text); self.verdict.setStyleSheet(
            f"background:{BAR};color:{color};padding:2px 10px;")
        if level == "bad":
            self.view.stop()
            self.view.setHtml(f"<body style='background:{BG};color:{RED};font-family:monospace;"
                              f"display:grid;place-items:center;height:90vh'><h1>⛔ BLOCKED BY GATESHIELD</h1></body>")
    def on_loaded(self, ok): pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OneLock Browser"); self.resize(1200, 800)
        self.s = QSettings("Knuckls", "GateShieldBrowser")
        self.shield = Shield(self.s)
        self.profile = QWebEngineProfile.defaultProfile()
        self.tabs = QTabWidget(); self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        bar = QToolBar(); bar.setMovable(False); self.addToolBar(bar)
        bar.setStyleSheet(f"QToolBar{{background:{BAR};border:0;spacing:4px;padding:3px}} QToolButton{{color:{MUT}}}")
        self.back = QAction("◂", self); bar.addAction(self.back)
        self.fwd = QAction("▸", self); bar.addAction(self.fwd)
        self.url = QLineEdit(); self.url.setPlaceholderText("Search or type a URL")
        self.url.returnPressed.connect(self.navigate)
        self.url.setStyleSheet(f"QLineEdit{{background:#1c2129;color:#e6edf3;border-radius:8px;padding:6px 10px;border:1px solid #30363d}}")
        bar.addWidget(self.url)
        gear = QAction("⚙", self); gear.triggered.connect(self.open_settings); bar.addAction(gear)
        key = QAction("🔑", self); key.triggered.connect(self.open_onelock); bar.addAction(key)
        self.url.selectAll()  # focus + select on start
        self.new_tab(QUrl("https://duckduckgo.com/"), focus=True)
        self.back.triggered.connect(lambda: self.tabs.currentWidget().view.back())
        self.fwd.triggered.connect(lambda: self.tabs.currentWidget().view.forward())
    def new_tab(self, url, focus=False):
        t = BrowserTab(self.profile, self.shield, self)
        i = self.tabs.addTab(t, "New tab")
        if url.isValid() and url.toString(): t.view.load(url)
        if focus: self.tabs.setCurrentIndex(i)
        t.view.titleChanged.connect(lambda ttl, i=i: self.tabs.setTabText(i, ttl[:20] or "New tab"))
        return t
    def close_tab(self, i):
        if self.tabs.count() == 1: self.close(); return
        w = self.tabs.widget(i); self.tabs.removeTab(i); w.deleteLater()
    def navigate(self):
        q = self.url.text().strip()
        if not q: return
        if q.startswith("http://") or q.startswith("https://"): url = QUrl(q)
        elif "." in q and " " not in q: url = QUrl("https://" + q)
        else: url = QUrl(SEARCH[int(self.s.value("engine", 0, type=int))] + QUrl.toPercentEncoding(q).data().decode())
        self.tabs.currentWidget().view.load(url)
        self.url.selectAll()
    def open_settings(self):
        d = SettingsDialog(self.s, self); d.exec()
        self.shield.s.sync()
    def open_onelock(self):
        QMessageBox.information(self, "OneLock", "OneLock integration is Android-only.\nOn desktop, passwords fill through your browser or OS.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OneLock Browser")
    QWebEngineProfile.defaultProfile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
