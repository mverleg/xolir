package telir_generate_java;

import telir.BuiltinTypeOuterClass;

import static telir.Tel.TelProgram;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
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
        var dirPath = Path.of(inputPath.getParent().toString(), "generated", "src", "main", "java");
        try {
            Files.createDirectories(dirPath);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
        return Path.of(dirPath.toString(), tel.getProgramName() + ".java");
    }

    private static TelProgram readTel(Path inputPath) {
        try {
            var proto = Files.readAllBytes(inputPath);
            return TelProgram.parseFrom(proto);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
    }

    private static void compileToJava(TelProgram tel, Path outputPath) {
        try (PrintWriter writer = new PrintWriter(outputPath.toFile(), StandardCharsets.UTF_8)) {
            for (var source : tel.getSourcesList()) {
                writer.println("\n// ** Tel source: " + source.getName() + " **");
                source.getSource().lines().forEach(line -> writer.println("//   " + line));
            }
            writer.println("\n@javax.annotation.processing.Generated  // do not edit");
            writer.println("public class " + safeName(tel.getProgramName()) + " {");
            for (var cls : tel.getStructsList()) {
                writer.println("\tprivate record " + safeName(cls.getName()) + " {");
                for (var field : cls.getFieldsList()) {
                    writer.println("\t\tprivate final " + builtinType(field.getTyp().getBuiltin()) +
                            " " + safeName(field.getName()) + ";");
                }
                writer.println("\t}\n");
            }
            //TODO @mark: functions
            writer.println("}");
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
    }

    private static String builtinType(BuiltinTypeOuterClass.BuiltinType bultinType) {
        return switch (bultinType) {
            case S_INT_32 -> "int";
            case S_INT_64 -> "long";
            case REAL_64 -> "double";
            case BOOL -> "boolean";
            case UNRECOGNIZED -> throw new AssertionError("unrecognized type");
        };
    }

    private static String safeName(String rawName) {
        assert !rawName.isBlank();
        return rawName;
    }
}
