package com.example.app; // PALITAN ng package name mo

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(TcpSocketPlugin.class);   // dapat BAGO ang super.onCreate
        super.onCreate(savedInstanceState);
    }
}
