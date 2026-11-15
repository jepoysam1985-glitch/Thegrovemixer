package com.groovemixer.app;

import android.Manifest;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.WebView;
import androidx.activity.OnBackPressedCallback;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TcpSocketPlugin.class);   // custom plugin (ang ForegroundService ay galing sa npm package)
        goFullScreen();
        super.onCreate(savedInstanceState);
        goFullScreen();
        // Hingin ang mic permission agad para hindi mag-crash ang foreground service (type: microphone) pag GO LIVE
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.RECORD_AUDIO}, 1);
        }

        // Back button ng phone: isara muna ang bukas na panel (Settings, FX, atbp.). Kapag wala na, magtanong kung lalabas.
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                WebView wv = (getBridge() != null) ? getBridge().getWebView() : null;
                if (wv != null && wv.canGoBack()) {
                    wv.goBack();
                    return;
                }
                confirmExit();
            }
        });
    }

    @Override
    public void onResume() {
        super.onResume();
        goFullScreen();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) goFullScreen();
    }

    // FULL SCREEN: itinatago ang status bar at navigation bar, at sinasakop pati ang notch/cutout sa gilid
    private void goFullScreen() {
        try {
            Window w = getWindow();
            if (Build.VERSION.SDK_INT >= 28) {
                WindowManager.LayoutParams lp = w.getAttributes();
                lp.layoutInDisplayCutoutMode = Build.VERSION.SDK_INT >= 30
                    ? WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                    : WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
                w.setAttributes(lp);
            }
            WindowCompat.setDecorFitsSystemWindows(w, false);
            w.setStatusBarColor(Color.TRANSPARENT);
            w.setNavigationBarColor(Color.TRANSPARENT);
            w.getDecorView().setBackgroundColor(Color.parseColor("#02030a"));
            WindowInsetsControllerCompat c = WindowCompat.getInsetsController(w, w.getDecorView());
            if (c != null) {
                c.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                c.hide(WindowInsetsCompat.Type.systemBars());
            }
        } catch (Throwable ignored) { }
    }

    private void confirmExit() {
        new AlertDialog.Builder(this)
            .setTitle("Exit The Groove Mixer?")
            .setMessage("Titigil ang music at ang broadcast kapag lumabas ka.")
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    finishAndRemoveTask();
                    android.os.Process.killProcess(android.os.Process.myPid());
                }
            })
            .show();
    }
}
