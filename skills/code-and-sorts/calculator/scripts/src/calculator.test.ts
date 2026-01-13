import { Calculator } from './calculator.js';

describe('Calculator', () => {
    describe('static evaluate()', () => {
        describe('basic operations', () => {
            it('should add two numbers', () => {
                expect(Calculator.evaluate('3 + 2')).toBe('5');
            });

            it('should subtract two numbers', () => {
                expect(Calculator.evaluate('5 - 3')).toBe('2');
            });

            it('should multiply two numbers', () => {
                expect(Calculator.evaluate('4 * 3')).toBe('12');
            });

            it('should divide two numbers', () => {
                expect(Calculator.evaluate('10 / 4')).toBe('2.5');
            });

            it('should calculate exponents', () => {
                expect(Calculator.evaluate('2 ^ 10')).toBe('1024');
            });
        });

        describe('operator precedence', () => {
            it('should respect multiplication over addition', () => {
                expect(Calculator.evaluate('2 + 3 * 4')).toBe('14');
            });

            it('should respect division over subtraction', () => {
                expect(Calculator.evaluate('10 - 6 / 2')).toBe('7');
            });

            it('should respect exponent over multiplication', () => {
                expect(Calculator.evaluate('2 * 3 ^ 2')).toBe('18');
            });

            it('should handle complex precedence', () => {
                expect(Calculator.evaluate('1 + 4.5 * (3-6) / 5')).toBe('-1.7');
            });
        });

        describe('parentheses', () => {
            it('should evaluate parentheses first', () => {
                expect(Calculator.evaluate('(2 + 3) * 4')).toBe('20');
            });

            it('should handle nested parentheses', () => {
                expect(Calculator.evaluate('((2 + 3) * 2) + 1')).toBe('11');
            });

            it('should handle multiple parentheses groups', () => {
                expect(Calculator.evaluate('(2 + 3) * (4 + 5)')).toBe('45');
            });
        });

        describe('right-associativity of exponent', () => {
            it('should evaluate exponents right-to-left', () => {
                expect(Calculator.evaluate('2 ^ 3 ^ 2')).toBe('512');
            });
        });

        describe('unary minus', () => {
            it('should handle negative number at start', () => {
                expect(Calculator.evaluate('-5 + 3')).toBe('-2');
            });

            it('should handle negative number after operator', () => {
                expect(Calculator.evaluate('3 * -2')).toBe('-6');
            });

            it('should handle negative number after open paren', () => {
                expect(Calculator.evaluate('(-5 + 3)')).toBe('-2');
            });

            it('should handle negative in complex expression', () => {
                expect(Calculator.evaluate('10 + -5 * 2')).toBe('0');
            });
        });

        describe('decimal precision (big.js)', () => {
            it('should avoid floating-point errors', () => {
                expect(Calculator.evaluate('0.1 + 0.2')).toBe('0.3');
            });

            it('should handle decimal multiplication', () => {
                expect(Calculator.evaluate('0.1 * 0.2')).toBe('0.02');
            });

            it('should handle large numbers', () => {
                expect(Calculator.evaluate('999999999999999999 + 1')).toBe('1000000000000000000');
            });

            it('should support negative numbers', () => {
                expect(Calculator.evaluate('-0.1 + 0.2')).toBe('0.1');
            });
        });

        describe('whitespace handling', () => {
            it('should ignore whitespace', () => {
                expect(Calculator.evaluate('  3  +   2  ')).toBe('5');
            });

            it('should work without whitespace', () => {
                expect(Calculator.evaluate('3+2*4')).toBe('11');
            });
        });

        describe('error handling', () => {
            it('should throw on empty expression', () => {
                expect(() => Calculator.evaluate('')).toThrow('Empty expression');
            });

            it('should throw on whitespace-only expression', () => {
                expect(() => Calculator.evaluate('   ')).toThrow('Empty expression');
            });

            it('should throw on mismatched opening parenthesis', () => {
                expect(() => Calculator.evaluate('(2 + 3')).toThrow('Mismatched parentheses');
            });

            it('should throw on mismatched closing parenthesis', () => {
                expect(() => Calculator.evaluate('2 + 3)')).toThrow('Mismatched parentheses');
            });

            it('should throw on trailing operator', () => {
                expect(() => Calculator.evaluate('2 +')).toThrow();
            });
        });
    });

    describe('chainable instance methods', () => {
        it('should chain add operations', () => {
            const calc = new Calculator(10);
            expect(calc.add(5).add(3).toString()).toBe('18');
        });

        it('should chain mixed operations', () => {
            const calc = new Calculator(10);
            expect(calc.add(5).sub(3).mul(2).toString()).toBe('24');
        });

        it('should chain with division', () => {
            const calc = new Calculator(100);
            expect(calc.div(4).add(5).toString()).toBe('30');
        });

        it('should chain with exponent', () => {
            const calc = new Calculator(2);
            expect(calc.pow(3).add(2).toString()).toBe('10');
        });

        it('should return current value', () => {
            const calc = new Calculator(42);
            expect(calc.value().toString()).toBe('42');
        });

        it('should accept string input', () => {
            const calc = new Calculator('10.5');
            expect(calc.add('0.5').toString()).toBe('11');
        });
    });
});
