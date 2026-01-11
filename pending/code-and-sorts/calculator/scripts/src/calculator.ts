import Big, { BigSource } from 'big.js';

export class Calculator {
    private x: Big;

    constructor(initial: BigSource = 0) {
        this.x = new Big(initial);
    }

    add(v: BigSource) { this.x = this.x.plus(v); return this; }
    sub(v: BigSource) { this.x = this.x.minus(v); return this; }
    mul(v: BigSource) { this.x = this.x.times(v); return this; }
    div(v: BigSource) { this.x = this.x.div(v); return this; }
    pow(v: number) { this.x = this.x.pow(v); return this; }

    value(): Big { return this.x; }
    toString(): string { return this.x.toString(); }

    static evaluate(expression: string): string {
        if (!expression || expression.trim() === '') {
            throw new Error("Empty expression");
        }

        // Remove whitespace
        expression = expression.replace(/\s+/g, '');

        // Tokenize: numbers (including decimals and negative numbers) or operators/parens
        // Handles unary minus at start or after operators/open parens
        const tokens: string[] = [];
        const tokenRegex = /(\d+(\.\d+)?)|[\+\-\*\/\^\(\)]/g;
        let match: RegExpExecArray | null;
        let lastToken: string | null = null;

        while ((match = tokenRegex.exec(expression)) !== null) {
            let token = match[0];

            // Handle unary minus: convert to negative number
            if (token === '-' && (lastToken === null || lastToken === '(' || this.isOperator(lastToken))) {
                const nextMatch = tokenRegex.exec(expression);
                if (nextMatch && !isNaN(parseFloat(nextMatch[0]))) {
                    token = '-' + nextMatch[0];
                } else {
                    throw new Error("Invalid expression: unexpected minus");
                }
            }

            tokens.push(token);
            lastToken = token;
        }

        if (tokens.length === 0) {
            throw new Error("Invalid expression: no valid tokens");
        }

        const outputQueue: string[] = [];
        const operatorStack: string[] = [];

        // Operator precedence and associativity
        const operators: { [key: string]: { precedence: number; rightAssoc: boolean } } = {
            '+': { precedence: 1, rightAssoc: false },
            '-': { precedence: 1, rightAssoc: false },
            '*': { precedence: 2, rightAssoc: false },
            '/': { precedence: 2, rightAssoc: false },
            '^': { precedence: 3, rightAssoc: true }  // Exponent is right-associative
        };

        for (const token of tokens) {
            if (!isNaN(parseFloat(token))) {
                outputQueue.push(token);
            } else if (token in operators) {
                const op1 = operators[token];
                while (
                    operatorStack.length > 0 &&
                    operatorStack[operatorStack.length - 1] !== '(' &&
                    operatorStack[operatorStack.length - 1] in operators
                ) {
                    const op2 = operators[operatorStack[operatorStack.length - 1]];
                    if (op2.precedence > op1.precedence ||
                        (op2.precedence === op1.precedence && !op1.rightAssoc)) {
                        outputQueue.push(operatorStack.pop()!);
                    } else {
                        break;
                    }
                }
                operatorStack.push(token);
            } else if (token === '(') {
                operatorStack.push(token);
            } else if (token === ')') {
                while (operatorStack.length > 0 && operatorStack[operatorStack.length - 1] !== '(') {
                    outputQueue.push(operatorStack.pop()!);
                }
                if (operatorStack.length === 0) {
                    throw new Error("Mismatched parentheses");
                }
                operatorStack.pop(); // Remove the '('
            }
        }

        while (operatorStack.length > 0) {
            const op = operatorStack.pop()!;
            if (op === '(') {
                throw new Error("Mismatched parentheses");
            }
            outputQueue.push(op);
        }

        const evalStack: Big[] = [];
        for (const token of outputQueue) {
            if (!isNaN(parseFloat(token))) {
                evalStack.push(new Big(token));
            } else {
                const b = evalStack.pop();
                const a = evalStack.pop();
                if (a === undefined || b === undefined) {
                    throw new Error("Invalid expression");
                }

                switch (token) {
                    case '+': evalStack.push(a.plus(b)); break;
                    case '-': evalStack.push(a.minus(b)); break;
                    case '*': evalStack.push(a.times(b)); break;
                    case '/': evalStack.push(a.div(b)); break;
                    case '^': evalStack.push(a.pow(b.toNumber())); break;
                }
            }
        }

        if (evalStack.length !== 1) {
            throw new Error("Invalid expression");
        }
        return evalStack[0].toString();
    }

    private static isOperator(token: string): boolean {
        return ['+', '-', '*', '/', '^'].includes(token);
    }
}
