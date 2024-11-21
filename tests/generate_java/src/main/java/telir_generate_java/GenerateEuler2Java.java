package telir_generate_java;

import static telir.Tel.TelProgram;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;

public class GenerateEuler2Java {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("First argument should be the path to Telir binary proto file");
            System.exit(1);
        }
        TelProgram tel = readTel(args);
        System.out.println(tel);
    }

    private static TelProgram readTel(String[] args) {
        TelProgram tel;
        try {
            Path path = FileSystems.getDefault().getPath(args[0]);
            byte[] proto = Files.readAllBytes(path);
            tel = TelProgram.parseFrom(proto);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
        return tel;
    }
}
