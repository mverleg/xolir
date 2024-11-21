package telir_generate_java;

import telir.ExpressionOuterClass;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import static telir.BuiltinTypeOuterClass.BuiltinType;
import static telir.ExpressionOuterClass.Expression;
import static telir.FunctionOuterClass.Function;
import static telir.StructOuterClass.Struct;
import static telir.Tel.TelProgram;
import static telir.Type.TypedName;

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

    private static void compileStructs(PrintWriter writer, List<Struct> structs) {
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

    private static void compileFunctions(PrintWriter writer, List<Function> functions) {
        for (var func : functions) {
            assert func.getResultsList().size() <= 1 : "multiple return values not supported yet";
            String safeFuncName = safeName(func.getName(), false);
            if (!safeFuncName.equals(func.getName())) {
                writer.println("\t// " + func.getName());
            }
            writer.print("\tprivate static " + (func.getResultsList().isEmpty() ? "void" : builtinType(func.getResultsList().get(0).getBuiltin())));
            writer.print(" " + safeFuncName + "(");
            var arg_vars = generateArgument(func.getArgsList(), writer);
            var variables = new ArrayList<>(arg_vars);
            writer.println(") {");
            for (var local : func.getLocalsList()) {
                var javaType = builtinType(local.getTyp().getBuiltin());
                var javaName = safeName(local.getName(), false);
                variables.add(new Variable(javaType, javaName));
                writer.println("\t\t" + javaType +
                        " " + javaName + ";");
            }
            compileStatements(writer, func.getCodeList(), variables, 2);
            writer.println("\t}\n");
        }
    }

    private static void compileStatements(PrintWriter writer, List<Expression> stmts, List<Variable> variables, int indent) {
        for (var stmt : stmts) {
            writeIndented(writer, indent, "");
            compileExpression(writer, stmt, variables, indent);
            writer.println(";");
        }
    }

    private static void compileExpression(PrintWriter writer, Expression expr, List<Variable> variables, int indent) {
        switch (expr.getExprCase()) {
            case READ -> {
                writer.print(variables.get(expr.getRead().getVarIx()).name());
            }
            case STORE -> {
                writer.print(variables.get(expr.getStore().getVarIx()).name() + " = ");
                compileExpression(writer, expr.getStore().getValue(), variables, indent);
            }
            case CALL -> {
                writer.print("/* TODO: CALL */");  //TODO @mark:
            }
            case IF_ -> {
                writer.print("if (");
                ExpressionOuterClass.If ifExpr = expr.getIf();
                compileExpression(writer, ifExpr.getCondition(), variables, indent);
                writeIndented(writer, indent, ") {\n");
                compileStatements(writer, ifExpr.getCodeList(), variables, indent + 1);
                if (ifExpr.getElseList() != null && !ifExpr.getElseList().isEmpty()) {
                    writeIndented(writer, indent, "} else {\n");
                    compileStatements(writer, ifExpr.getElseList(), variables, indent + 1);
                }
                writeIndented(writer, indent, "}");
            }
            case WHILE_ -> {
                writer.print("while (");
                compileExpression(writer, expr.getWhile().getCondition(), variables, indent);
                writeIndented(writer, indent, ") {\n");
                compileStatements(writer, expr.getWhile().getCodeList(), variables, indent + 1);
                writeIndented(writer, indent, "}");
            }
            case RETURN_ -> {
                writer.print("return ");
                compileExpression(writer, expr.getReturn().getValue(), variables, indent);
            }
            case INT -> {
                writer.print(expr.getInt());
            }
            case REAL -> {
                writer.print(expr.getReal());
            }
            case TEXT -> {
                assert !expr.getText().contains("\""): "strings with double-quotes not supported yet";
                writer.print(expr.getText());
            }
            case BOOL -> {
                writer.print(expr.getBool() ? "true" : "false");
            }
            case EXPR_NOT_SET -> throw new AssertionError("expression type not recognized");
        }
    }

    private static void writeIndented(PrintWriter writer, int indent, String text) {
        writer.print("\t".repeat(indent));
        writer.print(text);
    }

    private static List<Variable> generateArgument(List<TypedName> argList, PrintWriter writer) {
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
            variables.add(new Variable(javaType, javaName));
            writer.print("\t\t" + javaType + " " + javaName);
        }
        writer.print("\n\t");
        return variables;
    }

    private static String builtinType(BuiltinType bultinType) {
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
