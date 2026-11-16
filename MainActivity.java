package com.groove.mixer;

import android.os.Bundle;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TcpSocketPlugin.class);   // dapat BAGO ang super.onCreate
        super.onCreate(savedInstanceState);
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
