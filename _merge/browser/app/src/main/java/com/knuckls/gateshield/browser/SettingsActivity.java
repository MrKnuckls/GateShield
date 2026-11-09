package com.knuckls.gateshield.browser;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebStorage;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.Switch;
import android.widget.Toast;

public class SettingsActivity extends Activity {

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_settings);
        final Prefs p = new Prefs(this);

        Switch swAds = findViewById(R.id.swAds);
        Switch swMal = findViewById(R.id.swMalware);
        swAds.setChecked(p.ads);
        swMal.setChecked(p.malware);
        swAds.setOnCheckedChangeListener((v, on) -> p.setAds(on));
        swMal.setOnCheckedChangeListener((v, on) -> p.setMalware(on));

        RadioGroup rg = findViewById(R.id.rgEngine);
        if (p.engine == 1) rg.check(R.id.rbBing);
        else if (p.engine == 2) rg.check(R.id.rbGoogle);
        else rg.check(R.id.rbDdg);
        rg.setOnCheckedChangeListener((g, id) -> {
            if (id == R.id.rbBing) p.setEngine(1);
            else if (id == R.id.rbGoogle) p.setEngine(2);
            else p.setEngine(0);
        });

        findViewById(R.id.btnClear).setOnClickListener(x -> {
            CookieManager.getInstance().removeAllCookies(null);
            WebStorage.getInstance().deleteAllData();
            Toast.makeText(this, "Cookies + site data cleared", Toast.LENGTH_SHORT).show();
        });

        findViewById(R.id.btnAbout).setOnClickListener(x ->
            Toast.makeText(this, "GateShield Browser v2 — scans everything before it loads. Part of the GateShield suite at knuckls.com/shield", Toast.LENGTH_LONG).show());
    }
}
