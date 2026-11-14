package com.groovemixer.app;

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
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Diretsong TCP papuntang Icecast/Shoutcast. JS API: connect({host,port}), write({data:base64}), read({timeoutMs}) -> {text}, close(). */
@CapacitorPlugin(name = "TcpSocket")
public class TcpSocketPlugin extends Plugin {
    private volatile Socket socket;
    private volatile InputStream in;
    private volatile OutputStream out;
    private final ExecutorService connEx = Executors.newSingleThreadExecutor();
    private final ExecutorService wrEx = Executors.newSingleThreadExecutor();   // isang thread = tama ang pagkakasunod ng bytes
    private final ExecutorService rdEx = Executors.newSingleThreadExecutor();

    private void closeQuietly() {
        Socket s = socket;
        socket = null; in = null; out = null;
        if (s != null) { try { s.close(); } catch (Exception ignored) {} }
    }

    @PluginMethod
    public void connect(final PluginCall call) {
        final String host = call.getString("host");
        final Integer port = call.getInt("port");
        if (host == null || port == null) { call.reject("host and port are required"); return; }
        connEx.execute(() -> {
            try {
                closeQuietly();
                Socket s = new Socket();
                s.connect(new InetSocketAddress(host, port), 10000);
                s.setTcpNoDelay(true);
                s.setKeepAlive(true);
                socket = s; in = s.getInputStream(); out = s.getOutputStream();
                call.resolve();
            } catch (Exception e) {
                closeQuietly();
                call.reject("Cannot connect: " + e.getMessage());
            }
        });
    }

    @PluginMethod
    public void write(final PluginCall call) {
        final String data = call.getString("data");
        if (data == null) { call.reject("data is required"); return; }
        wrEx.execute(() -> {
            try {
                OutputStream o = out;
                if (o == null) throw new Exception("Not connected");
                o.write(Base64.decode(data, Base64.DEFAULT));
                o.flush();
                call.resolve();
            } catch (Exception e) {
                call.reject(e.getMessage() == null ? "Write failed" : e.getMessage());
            }
        });
    }

    @PluginMethod
    public void read(final PluginCall call) {
        final int ms = call.getInt("timeoutMs", 5000);
        rdEx.execute(() -> {
            JSObject r = new JSObject();
            try {
                Socket s = socket; InputStream i = in;
                if (s == null || i == null) throw new Exception("Not connected");
                s.setSoTimeout(ms);
                byte[] buf = new byte[4096];
                int n = i.read(buf);
                r.put("text", n > 0 ? new String(buf, 0, n, StandardCharsets.UTF_8) : "");
                call.resolve(r);
            } catch (SocketTimeoutException e) {
                r.put("text", "");
                call.resolve(r);
            } catch (Exception e) {
                call.reject(e.getMessage() == null ? "Read failed" : e.getMessage());
            }
        });
    }

    @PluginMethod
    public void close(PluginCall call) {
        closeQuietly();
        call.resolve();
    }

    @Override
    protected void handleOnDestroy() { closeQuietly(); }
}
