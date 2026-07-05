import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class OddOrPosTest {

    @Test
    @DisplayName("CACC-major-A: odd-negative and even-nonpositive")
    void caccMajorA() {
        assertEquals(1, OddOrPos.oddOrPos(new int[] {-3}));
        assertEquals(0, OddOrPos.oddOrPos(new int[] {0}));
    }

    @Test
    @DisplayName("CACC-major-B: even-positive and even-nonpositive")
    void caccMajorB() {
        assertEquals(1, OddOrPos.oddOrPos(new int[] {2}));
        assertEquals(0, OddOrPos.oddOrPos(new int[] {0}));
    }

    @Test
    @DisplayName("GICC-major-A: A inactive when B is true")
    void giccMajorA() {
        assertEquals(1, OddOrPos.oddOrPos(new int[] {1}));
        assertEquals(1, OddOrPos.oddOrPos(new int[] {2}));
    }

    @Test
    @DisplayName("GICC-major-B: B inactive when A is true")
    void giccMajorB() {
        assertEquals(1, OddOrPos.oddOrPos(new int[] {1}));
        assertEquals(1, OddOrPos.oddOrPos(new int[] {-3}));
    }

    @Test
    @DisplayName("Regression: textbook sample should count three values")
    void regressionSample() {
        assertEquals(3, OddOrPos.oddOrPos(new int[] {-3, -2, 0, 1, 4}));
    }
}
