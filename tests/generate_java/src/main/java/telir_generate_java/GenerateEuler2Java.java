package telir_generate_java;

import telir.BuiltinTypeOuterClass;
import telir.FunctionOuterClass;
import telir.StructOuterClass;
import telir.Type;

import static telir.Tel.TelProgram;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class GenerateEuler2Java {
    private static final Set<String> KEYWORDS = Set.of("abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const", "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native", "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void", "volatile", "while");

    public static void main(String[] args) {
        var inputPath = getInputPath(args);
        var tel = readTel(inputPath);
        var outputPath = buildOutputPath(inputPath, tel);
        compileToJava(tel, outputPath);
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
        return Path.of(dirPath.toString(), safeName(tel.getProgramName(), true) + ".java");
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
            writer.println("\n@javax.annotation.processing.Generated(\"telir\")  // do not edit");
            writer.println("public class " + safeName(tel.getProgramName(), true) + " {\n");
            compileStructs(writer, tel.getStructsList());
            compileFunctions(writer, tel.getFunctionsList());
            writer.println("}");
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
    }

    private static void compileStructs(PrintWriter writer, List<StructOuterClass.Struct> structs) {
        for (var cls : structs) {
            String safeClsName = safeName(cls.getName(), true);
            if (!safeClsName.equals(cls.getName())) {
                writer.println("\t// " + cls.getName());
            }
            writer.print("\tprivate record " + safeClsName + "(");
            generateArgument(cls.getFieldsList(), writer);
            writer.println(") {}\n");
        }
    }

    private static void compileFunctions(PrintWriter writer, List<FunctionOuterClass.Function> functions) {
        for (var func : functions) {
            assert func.getResultsList().size() <= 1 : "multiple return values not supported yet";
            String safeFuncName = safeName(func.getName(), false);
            if (!safeFuncName.equals(func.getName())) {
                writer.println("\t// " + func.getName());
            }
            writer.print("\tprivate static " + (func.getResultsList().isEmpty() ? "void" : builtinType(func.getResultsList().get(0).getBuiltin())));
            writer.print(" " + safeFuncName + "(");
            var arg_vars = generateArgument(func.getArgsList(), writer);
            var variables = new ArrayList<Variable>(arg_vars);
            writer.println(") {");
            for (var local : func.getLocalsList()) {
                var javaType = builtinType(local.getTyp().getBuiltin());
                var javaName = safeName(local.getName(), false);
                variables.add(new Variable(javaType, javaName));
                writer.println("\t\t" + javaType +
                        " " + javaName + ";");
            }
            writer.println("\t\t// TODO: code");
            writer.println("\t}\n");
        }
    }

    private static ArrayList<Variable> generateArgument(List<Type.TypedName> argList, PrintWriter writer) {
        var variables = new ArrayList<Variable>(argList.size());
        if (argList.isEmpty()) {
            return variables;
        }
        writer.print("\n");
        boolean first = true;
        for (var field : argList) {
            if (first) {
                first = false;
            } else {
                writer.print(",\n");
            }
            var javaType = builtinType(field.getTyp().getBuiltin());
            var javaName = safeName(field.getName(), false);
            writer.print("\t\t" + javaType + " " + javaName);
        }
        writer.print("\n\t");
        return variables;
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

    private record Variable(String type, String name) {}

    private static String safeName(String rawName, boolean isType) {
        //TODO @mark: it's possible that the_thing and TheThing and up colliding
        int i = 0;
        while (i < rawName.length() && !Character.isLetter(rawName.charAt(i))) {
            i++;
        }
        var cleanName = new StringBuilder();
        if (isType) {
            cleanName.append(Character.toUpperCase(rawName.charAt(i)));
        } else {
            cleanName.append(Character.toLowerCase(rawName.charAt(i)));
        }
        boolean capitalizeNext = false;
        for (i++; i < rawName.length(); i++) {
            var c = rawName.charAt(i);
            if (!Character.isLetter(c) && !Character.isDigit(c)) {
                capitalizeNext = true;
                continue;
            }
            cleanName.append(capitalizeNext ? Character.toUpperCase(c) : c);
            capitalizeNext = false;
        }
        var cleaned = cleanName.toString();
        if (KEYWORDS.contains(cleaned)) {
            // there are no java keywords with underscores, so this is safe
            cleaned += "_";
        }
        assert !cleaned.isEmpty();
        return cleaned;
    }
}
