package com.groovemixer.app;

import android.Manifest;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.webkit.WebView;
import androidx.activity.OnBackPressedCallback;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TcpSocketPlugin.class);   // custom plugin (ang ForegroundService ay galing sa npm package)
        super.onCreate(savedInstanceState);
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
