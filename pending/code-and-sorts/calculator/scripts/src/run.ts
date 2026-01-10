import { Calculator } from './calculator.js';
import process from 'node:process';

const args = process.argv.slice(2);
const expression = args.join(' ');

try {
    const result = Calculator.evaluate(expression);
    console.log(result);
} catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
}
