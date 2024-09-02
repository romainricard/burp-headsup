package romainricard.burp.headsup;

import burp.api.montoya.BurpExtension;
import burp.api.montoya.extension.Extension;
import burp.api.montoya.extension.ExtensionUnloadingHandler;
import burp.api.montoya.MontoyaApi;
import burp.api.montoya.proxy.Proxy;
import burp.api.montoya.logging.Logging;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.InetAddress;
import java.util.Collections;

import org.jboss.com.sun.net.httpserver.HttpExchange;
import org.jboss.com.sun.net.httpserver.HttpServer;

public class Headsup implements BurpExtension
{
    private Logging logging;
    private HttpServer server;
    private Proxy proxy;

    @Override
    public void initialize(MontoyaApi api){

        int port = 47674;

        proxy = api.proxy();
        logging = api.logging();

        Extension extension = api.extension();
        extension.registerUnloadingHandler(new ExtensionUnloadHandler());
       
        logging.logToOutput("Creating server on port " + port + "...");

        try{
            InetSocketAddress sockAddr = new InetSocketAddress(InetAddress.getLoopbackAddress(), port);
            server = HttpServer.create(sockAddr, 0);
           
            server.createContext("/server/status", httpExchange -> {
                sendStatus(httpExchange, 200, "running");
            });

            server.createContext("/intercept/status", httpExchange -> {
                sendStatus(httpExchange, 200, proxy.isInterceptEnabled() ? "intercept" : "pass");
            });

            server.createContext("/intercept/enable", httpExchange -> {
                proxy.enableIntercept();
                sendStatus(httpExchange, 200, "intercept");
            });

            server.createContext("/intercept/disable", httpExchange -> {
                proxy.disableIntercept();
                sendStatus(httpExchange, 200, "pass");
            });

            server.createContext("/intercept/toggle", httpExchange -> {
                if(proxy.isInterceptEnabled()){
                    proxy.disableIntercept();
                    sendStatus(httpExchange, 200, "pass");

                } else {
                    proxy.enableIntercept();
                    sendStatus(httpExchange, 200, "intercept");
                }
            });

            server.setExecutor(null); // creates a default executor
            server.start();

            logging.logToOutput("Done creating server!");
            logging.logToOutput("Listening to HTTP requests on port " + port + "...");

        } catch(IOException e){
            logging.logToError("Can't start server: " + e);
        }
    }

    public void sendStatus(HttpExchange httpInterface, int httpStatusCode, String status) throws IOException {
        String jsonContent = "{\"status\": \"" + status + "\"}";
        httpInterface.getResponseHeaders().put("Content-Type", Collections.singletonList("application/json")); 
        httpInterface.sendResponseHeaders(httpStatusCode, jsonContent.length());
        OutputStream outStream = httpInterface.getResponseBody();
        outStream.write(jsonContent.getBytes());
        outStream.close();
    }

    private class ExtensionUnloadHandler implements ExtensionUnloadingHandler {
        @Override
        public void extensionUnloaded() {
            logging.logToOutput("Unloading....");
            server.stop(0);
            logging.logToOutput("Done unloading!");
        }
    }
}
