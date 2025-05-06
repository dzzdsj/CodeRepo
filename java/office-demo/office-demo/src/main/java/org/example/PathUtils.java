package org.example;
import java.io.File;
import java.net.URL;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class PathUtils {
    public static String getJarDirectory() {
        URL url = PathUtils.class.getProtectionDomain().getCodeSource().getLocation();
        String jarPath = url.getFile();
        try {
            jarPath = URLDecoder.decode(jarPath, StandardCharsets.UTF_8.name());
        } catch (Exception e) {
            throw new RuntimeException("Error decoding URL", e);
        }
        File jarFile = new File(jarPath);
        return jarFile.getParentFile().getAbsolutePath();
    }

    public static void main(String[] args) {
        System.out.println(getJarDirectory());
    }
}

