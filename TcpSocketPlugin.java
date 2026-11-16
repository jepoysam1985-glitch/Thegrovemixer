package com.example.app; // PALITAN ito ng package name ng app mo (nasa MainActivity.java sa taas)

import android.util.Base64;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@CapacitorPlugin(name = "TcpSocket")
public class TcpSocketPlugin extends Plugin {
    private Socket socket;
    private InputStream in;
    private OutputStream out;
    private final ExecutorService io = Executors.newSingleThreadExecutor();

    @PluginMethod
    public void connect(PluginCall call) {
        final String host = call.getString("host");
        final int port = call.getInt("port", 0);
        io.execute(() -> {
            try {
                closeQuiet();
                socket = new Socket();
                socket.setTcpNoDelay(true);
                socket.connect(new InetSocketAddress(host, port), 10000);
                in = socket.getInputStream();
                out = socket.getOutputStream();
                call.resolve();
            } catch (Exception e) {
                closeQuiet();
                call.reject("Connect failed: " + e.getMessage());
            }
        });
    }

    @PluginMethod
    public void write(PluginCall call) {
        final String data = call.getString("data", "");
        io.execute(() -> {
            try {
                if (out == null) { call.reject("Not connected"); return; }
                out.write(Base64.decode(data, Base64.DEFAULT));
                out.flush();
                call.resolve();
            } catch (Exception e) {
                call.reject("Write failed: " + e.getMessage());
            }
        });
    }

    @PluginMethod
    public void read(PluginCall call) {
        final int timeout = call.getInt("timeoutMs", 5000);
        io.execute(() -> {
            try {
                if (in == null) { call.reject("Not connected"); return; }
                socket.setSoTimeout(timeout);
                byte[] buf = new byte[4096];
                int n;
                try { n = in.read(buf); } catch (java.net.SocketTimeoutException t) { n = 0; }
                JSObject r = new JSObject();
                r.put("text", n > 0 ? new String(buf, 0, n, StandardCharsets.ISO_8859_1) : "");
                call.resolve(r);
            } catch (Exception e) {
                call.reject("Read failed: " + e.getMessage());
            }
        });
    }

    @PluginMethod
    public void close(PluginCall call) {
        io.execute(() -> { closeQuiet(); call.resolve(); });
    }

    private void closeQuiet() {
        try { if (socket != null) socket.close(); } catch (Exception ignored) {}
        socket = null; in = null; out = null;
    }
}
