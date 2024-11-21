package telir_generate_java;

import static telir.Tel.TelProgram;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;

public class GenerateEuler2Java {
    public static void main(String[] args) {
        var inputPath = getInputPath(args);
        var tel = readTel(inputPath);
        var outputPath = buildOutputPath(inputPath, tel);
        compileToJava(tel, outputPath);
        System.out.println(tel);
    }

    private static Path getInputPath(String[] args) {
        if (args.length != 1) {
            System.err.println("First argument should be the path to Telir binary proto file");
            System.exit(1);
        }
        return FileSystems.getDefault().getPath(args[0]);
    }

    private static Path buildOutputPath(Path inputPath, TelProgram tel) {
        var dirPath = Path.of(inputPath.getParent().toString(), "generated", "src", "main", "java", tel.getProgramName() + ".java");
        try {
            Files.createDirectories(dirPath);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
        return Path.of(dirPath.toString(), tel.getProgramName() + ".java");
    }

    private static TelProgram readTel(Path inputPath) {
        TelProgram tel;
        try {
            byte[] proto = Files.readAllBytes(inputPath);
            tel = TelProgram.parseFrom(proto);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
        return tel;
    }

    private static void compileToJava(TelProgram tel, Path outputPath) {

    }
}
