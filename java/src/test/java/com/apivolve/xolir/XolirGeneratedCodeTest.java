
package com.apivolve.xolir;

import org.junit.jupiter.api.Test;
import com.apivolve.xolir.ProgramOuterClass.Program;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class XolirGeneratedCodeTest {
    @Test
    public void buildSmallAst() {
        var prog = Program.newBuilder()
                .setProgramName("HelloWorld")
                .build();
        assertEquals(prog.getProgramName(), "HelloWorld");
    }
}