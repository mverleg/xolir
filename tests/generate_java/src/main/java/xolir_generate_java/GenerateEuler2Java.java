package xolir_generate_java;

import com.apivolve.xolir.ExpressionOuterClass;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import static com.apivolve.xolir.ProgramOuterClass.Program;
import static com.apivolve.xolir.ExpressionOuterClass.Expression;
import static com.apivolve.xolir.FunctionOuterClass.Function;
import static com.apivolve.xolir.TypeStruct.StructType;
import static com.apivolve.xolir.Refs.TypedName;
import static com.apivolve.xolir.Refs.TypeRef;
import static com.apivolve.xolir.BuiltinTypeOuterClass.BuiltinType;

import com.apivolve.xolir.BuiltinFunction.BuiltinFunc;
import com.apivolve.xolir.Type.TypeDef;

public class GenerateEuler2Java {
    private static final Set<String> KEYWORDS = Set.of("abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const", "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native", "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void", "volatile", "while");

    public static void main(String[] args) {
        var inputPath = getInputPath(args);
        var tel = readTel(inputPath);
        var outputPath = buildOutputPath(inputPath, tel);
        System.out.printf("read program from %s, writing to %s%n", inputPath, outputPath);
        compileToJava(tel, outputPath);
    }

    private static Path getInputPath(String[] args) {
        if (args.length != 1) {
            System.err.println("First argument should be the path to xolir binary proto file");
            System.exit(1);
        }
        return FileSystems.getDefault().getPath(args[0]);
    }

    private static Path buildOutputPath(Path inputPath, Program tel) {
        var dirPath = Path.of(inputPath.getParent().toString(), "generated", "src", "main", "java");
        try {
            Files.createDirectories(dirPath);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
        return Path.of(dirPath.toString(), safeName(tel.getProgramName(), true) + ".java");
    }

    private static Program readTel(Path inputPath) {
        try {
            var proto = Files.readAllBytes(inputPath);
            return Program.parseFrom(proto);
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
    }

    private static void compileToJava(Program tel, Path outputPath) {
        try (PrintWriter writer = new PrintWriter(outputPath.toFile(), StandardCharsets.UTF_8)) {
            for (var source : tel.getFilesList()) {
                writer.println("\n// ** Tel source: " + source.getName() + " **");
                source.getSource().lines().forEach(line -> writer.println("//   " + line));
            }
            writer.println("\n@javax.annotation.processing.Generated(\"xolir\")  // do not edit");
            writer.println("public class " + safeName(tel.getProgramName(), true) + " {\n");
            var structTypes = tel.getTypesList().stream()
                    .filter(td -> td.getTargetCase() == TypeDef.TargetCase.STRUCT)
                    .map(TypeDef::getStruct)
                    .toList();
            compileStructs(writer, structTypes);
            var functions = tel.getFuncsList().stream().map(f -> new Func(safeName(f.getName(), false))).toList();
            compileFunctions(writer, tel.getFuncsList(), functions);
            writer.println("}");
        } catch (IOException exception) {
            throw new RuntimeException(exception);
        }
    }

    private static void compileStructs(PrintWriter writer, List<StructType> structs) {
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

    private static void compileFunctions(PrintWriter writer, List<Function> functions, List<Func> funcs) {
        for (var func : functions) {
            assert func.getTyp().getResultsList().size() <= 1 : "multiple return values not supported yet";
            String safeFuncName = safeName(func.getName(), false);
            if (!safeFuncName.equals(func.getName())) {
                writer.println("\t// " + func.getName());
            }
            writer.print("\tprivate static " + (func.getTyp().getResultsList().isEmpty() ? "void" : builtinType(func.getTyp().getResultsList().get(0))));
            writer.print(" " + safeFuncName + "(");
            var arg_vars = generateArgument(func.getTyp().getArgsList(), writer);
            var variables = new ArrayList<>(arg_vars);
            writer.println(") {");
            for (var local : func.getLocalsList()) {
                var javaType = builtinType(local.getTypeId());
                var javaName = safeName(local.getName(), false);
                variables.add(new Variable(javaType, javaName));
                writer.println("\t\t" + javaType + " " + javaName + ";");
            }
            compileStatements(writer, func.getCodeList(), funcs, variables, 2);
            writer.println("\t}\n");
        }
    }

    private static void compileStatements(PrintWriter writer, List<Expression> stmts, List<Func> funcs, List<Variable> variables, int indent) {
        for (var stmt : stmts) {
            writeIndented(writer, indent, "");
            compileExpression(writer, stmt, funcs, variables, indent);
            writer.println(";");
        }
    }

    private static void compileExpression(PrintWriter writer, Expression expr, List<Func> funcs, List<Variable> variables, int indent) {
        switch (expr.getExprCase()) {
            case READ -> {
                writer.print(variables.get(expr.getRead().getVarIx()).name());
            }
            case STORE -> {
                writer.print(variables.get(expr.getStore().getVarIx()).name() + " = ");
                compileExpression(writer, expr.getStore().getValue(), funcs, variables, indent);
            }
            case CALL -> {
                ExpressionOuterClass.Call call = expr.getCall();
                var funcRef = call.getFunc();
                switch (funcRef.getTargetCase()) {
                    case BUILTIN -> {
                        compileBuiltinFunc(writer, funcRef.getBuiltin(), call.getArgumentsList(), funcs, variables, indent);
                    }
                    case FUNC_IX -> {
                        writer.print(funcs.get((int) funcRef.getFuncIx()).name() + "(");
                        boolean first = true;
                        for (var arg : call.getArgumentsList()) {
                            if (first) {
                                first = false;
                            } else {
                                writer.print(", ");
                            }
                            compileExpression(writer, arg, funcs, variables, indent);
                        }
                        writer.print(")");
                    }
                    case TARGET_NOT_SET -> throw new AssertionError("call target not recognized");
                }
            }
            case IF_ -> {
                writer.print("if (");
                ExpressionOuterClass.If ifExpr = expr.getIf();
                compileExpression(writer, ifExpr.getCondition(), funcs, variables, indent);
                writer.print(") {\n");
                compileStatements(writer, ifExpr.getCodeList(), funcs, variables, indent + 1);
                if (ifExpr.getElseList() != null && !ifExpr.getElseList().isEmpty()) {
                    writeIndented(writer, indent, "} else {\n");
                    compileStatements(writer, ifExpr.getElseList(), funcs, variables, indent + 1);
                }
                writeIndented(writer, indent, "}");
            }
            case WHILE_ -> {
                writer.print("while (");
                compileExpression(writer, expr.getWhile().getCondition(), funcs, variables, indent);
                writer.print(") {\n");
                compileStatements(writer, expr.getWhile().getCodeList(), funcs, variables, indent + 1);
                writeIndented(writer, indent, "}");
            }
            case RETURN_ -> {
                writer.print("return ");
                compileExpression(writer, expr.getReturn().getValue(), funcs, variables, indent);
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
            var javaType = builtinType(field.getTypeId());
            var javaName = safeName(field.getName(), false);
            variables.add(new Variable(javaType, javaName));
            writer.print("\t\t" + javaType + " " + javaName);
        }
        writer.print("\n\t");
        return variables;
    }

    private static String builtinType(TypeRef typeRef) {
        return switch (typeRef.getTargetCase()) {
            case BUILTIN -> switch (typeRef.getBuiltin()) {
                case S_INT_32 -> "int";
                case S_INT_64 -> "long";
                case REAL_64 -> "double";
                case BOOL -> "boolean";
                case UNRECOGNIZED -> throw new AssertionError("unrecognized builtin type");
            };
            case TYPE_ID -> throw new AssertionError("only builtin types supported for Java output in this test");
            case TARGET_NOT_SET -> throw new AssertionError("type not set");
        };
    }

    private record Func(String name) {}

    private record Variable(String type, String name) {}

    private static void compileBuiltinFunc(PrintWriter writer, BuiltinFunc builtin, List<Expression> argumentsList, List<Func> funcs, List<Variable> variables, int indent) {
        var myBinaryOp = switch (builtin) {
            case ADD_U32 -> "+";
            case SUB_U32 -> "-";
            case MUL_U32 -> "*";
            case DIV_U32 -> "/";
            case LT_U32 -> "<";
            case LTE_U32 -> "<=";
            case EQ_U32 -> "==";
            case ADD_S64 -> "+";
            case SUB_S64 -> "-";
            case MUL_S64 -> "*";
            case DIV_S64 -> "/";
            case MOD_S64 -> "%";
            case LT_S64 -> "<";
            case LTE_S64 -> "<=";
            case EQ_S64 -> "==";
            case UNRECOGNIZED -> throw new AssertionError("unrecognized builtin function");
        };
        assert argumentsList.size() == 2: "binary operation " + builtin + " must have exactly 2 args";
        writer.print("(");
        compileExpression(writer, argumentsList.get(0), funcs, variables, indent);
        writer.print(" " + myBinaryOp + " ");
        compileExpression(writer, argumentsList.get(1), funcs, variables, indent);
        writer.print(")");
    }

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
