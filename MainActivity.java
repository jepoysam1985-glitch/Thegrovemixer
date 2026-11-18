package com.groove.mixer;

import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TcpSocketPlugin.class);   // dapat BAGO ang super.onCreate
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);   // LANDSCAPE LANG: walang portrait
        super.onCreate(savedInstanceState);
        goWide();
        tuneWebView();
        // Isang beses lang: hilingin sa user na huwag i-restrict ng battery saver ang app (para hindi mamatay ang tugtog sa background)
        try {
            getWindow().getDecorView().postDelayed(new Runnable() {
                @Override
                public void run() { askBatteryOnce(); }
            }, 5000);
        } catch (Throwable ignored) {
        }
    }

    // PINAKAMAHALAGA: kapag hindi nakikita ang WebView (lumabas sa app, screen lock, file picker), ibinababa ng Android
    // ang priority ng renderer kaya pumuputol-putol o namamatay ang tunog. Dito natin pinipilit na manatiling IMPORTANT.
    private void tuneWebView() {
        try {
            if (getBridge() == null) return;
            WebView wv = getBridge().getWebView();
            if (wv == null) return;
            if (Build.VERSION.SDK_INT >= 26) {
                wv.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT, false);
            }
            wv.getSettings().setMediaPlaybackRequiresUserGesture(false);
        } catch (Throwable ignored) {
        }
    }


    // WIDE SCREEN: itago ang status/navigation bar (swipe lang para lumabas saglit) at sakupin pati ang notch/camera area
    private void goWide() {
        try {
            android.view.Window w = getWindow();
            if (Build.VERSION.SDK_INT >= 28) {
                android.view.WindowManager.LayoutParams lp = w.getAttributes();
                lp.layoutInDisplayCutoutMode = Build.VERSION.SDK_INT >= 30
                    ? android.view.WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                    : android.view.WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
                w.setAttributes(lp);
            }
            androidx.core.view.WindowCompat.setDecorFitsSystemWindows(w, false);
            androidx.core.view.WindowInsetsControllerCompat c = androidx.core.view.WindowCompat.getInsetsController(w, w.getDecorView());
            if (c != null) {
                c.setSystemBarsBehavior(androidx.core.view.WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                c.hide(androidx.core.view.WindowInsetsCompat.Type.systemBars());
            }
        } catch (Throwable ignored) {
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) goWide();
    }

    private void askBatteryOnce() {
        try {
            if (Build.VERSION.SDK_INT < 23) return;
            SharedPreferences sp = getSharedPreferences("tgm", MODE_PRIVATE);
            if (sp.getBoolean("batAsked", false)) return;
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            if (pm == null || pm.isIgnoringBatteryOptimizations(getPackageName())) return;
            sp.edit().putBoolean("batAsked", true).apply();
            Intent i = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
            i.setData(Uri.parse("package:" + getPackageName()));
            startActivity(i);
        } catch (Throwable ignored) {
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        tuneWebView();
    }

    @Override
    public void onResume() {
        super.onResume();
        goWide();
        tuneWebView();
    }

    // Huwag patayin ang tunog ng WebView kapag lumabas saglit sa app (Add Track / file picker, atbp.)
    @Override
    public void onPause() {
        super.onPause();
        keepWebViewAlive();
    }

    @Override
    public void onStop() {
        super.onStop();
        keepWebViewAlive();
    }

    private void keepWebViewAlive() {
        try {
            if (getBridge() == null) return;
            WebView wv = getBridge().getWebView();
            if (wv != null) {
                wv.onResume();
                wv.resumeTimers();
            }
        } catch (Exception ignored) {
        }
    }
}
