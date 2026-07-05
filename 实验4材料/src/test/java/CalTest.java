import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.stream.Stream;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

import szu.csse.softwaretesting.ch8.Cal;

class CalTest {

    record CalCase(String id, int month1, int day1, int month2, int day2, int year, Integer expectedDays,
            boolean expectException) {
    }

    static Stream<CalCase> caccCases() {
        return Stream.of(
                new CalCase("CACC-A-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-A-F", 0, 15, 3, 10, 2024, null, true),
                new CalCase("CACC-B-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-B-F", 1, 15, 13, 10, 2024, null, true),
                new CalCase("CACC-C-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-C-F", 4, 15, 3, 10, 2024, null, true),
                new CalCase("CACC-D-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-D-F", 1, 0, 3, 10, 2024, null, true),
                new CalCase("CACC-E-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-E-F", 1, 15, 3, 0, 2024, null, true),
                new CalCase("CACC-F-T", 3, 10, 3, 20, 2024, 10, false),
                new CalCase("CACC-F-F", 3, 20, 3, 10, 2024, null, true),
                new CalCase("CACC-G-T", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("CACC-G-F", 1, 15, 3, 10, 0, null, true));
    }

    static Stream<CalCase> giccCases() {
        return Stream.of(
                new CalCase("GICC-A-T", 1, 15, 3, 10, 0, null, true),
                new CalCase("GICC-A-F", 0, 15, 3, 10, 0, null, true),
                new CalCase("GICC-B-T", 1, 15, 3, 10, 0, null, true),
                new CalCase("GICC-B-F", 1, 15, 13, 10, 0, null, true),
                new CalCase("GICC-C-T", 1, 15, 3, 10, 0, null, true),
                new CalCase("GICC-C-F", 4, 15, 3, 10, 0, null, true),
                new CalCase("GICC-D-T", 1, 15, 3, 10, 0, null, true),
                new CalCase("GICC-D-F", 1, 0, 3, 10, 0, null, true),
                new CalCase("GICC-E-T", 1, 15, 3, 10, 0, null, true),
                new CalCase("GICC-E-F", 1, 15, 3, 0, 0, null, true),
                new CalCase("GICC-F-T", 3, 10, 3, 20, 0, null, true),
                new CalCase("GICC-F-F", 3, 20, 3, 10, 0, null, true),
                new CalCase("GICC-G-T", 3, 20, 3, 10, 2024, null, true),
                new CalCase("GICC-G-F", 3, 20, 3, 10, 0, null, true));
    }

    static Stream<CalCase> mumcutCases() {
        return Stream.of(
                new CalCase("MUMCUT-UTP", 1, 15, 3, 10, 2024, 55, false),
                new CalCase("MUMCUT-NFP-A", 0, 15, 3, 10, 2024, null, true),
                new CalCase("MUMCUT-NFP-B", 1, 15, 13, 10, 2024, null, true),
                new CalCase("MUMCUT-NFP-C", 4, 15, 3, 10, 2024, null, true),
                new CalCase("MUMCUT-NFP-D", 1, 0, 3, 10, 2024, null, true),
                new CalCase("MUMCUT-NFP-E", 1, 15, 3, 0, 2024, null, true),
                new CalCase("MUMCUT-NFP-F", 3, 20, 3, 10, 2024, null, true),
                new CalCase("MUMCUT-NFP-G", 1, 15, 3, 10, 0, null, true));
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("caccCases")
    @DisplayName("Cal CACC coverage cases")
    void caccCases(CalCase testCase) {
        assertCalCase(testCase);
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("giccCases")
    @DisplayName("Cal GICC coverage cases")
    void giccCases(CalCase testCase) {
        assertCalCase(testCase);
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("mumcutCases")
    @DisplayName("Cal MUMCUT coverage cases")
    void mumcutCases(CalCase testCase) {
        assertCalCase(testCase);
    }

    @Test
    @DisplayName("Leap year regression across February")
    void leapYearRegression() {
        assertEquals(2, Cal.cal(2, 28, 3, 1, 2024));
    }

    @Test
    @DisplayName("January regression should count remaining days correctly")
    void januaryRegression() {
        assertEquals(17, Cal.cal(1, 15, 2, 1, 2024));
    }

    private void assertCalCase(CalCase testCase) {
        if (testCase.expectException) {
            assertThrows(IllegalArgumentException.class,
                    () -> Cal.cal(testCase.month1, testCase.day1, testCase.month2, testCase.day2, testCase.year),
                    testCase.id);
            return;
        }

        assertEquals(testCase.expectedDays.intValue(),
                Cal.cal(testCase.month1, testCase.day1, testCase.month2, testCase.day2, testCase.year),
                testCase.id);
    }
}
