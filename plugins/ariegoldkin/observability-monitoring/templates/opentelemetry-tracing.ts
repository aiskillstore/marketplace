/**
 * OpenTelemetry Distributed Tracing Setup
 */

import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { trace, SpanStatusCode, Span } from '@opentelemetry/api';

// =============================================
// SDK SETUP
// =============================================

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'app',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.APP_VERSION || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-express': { enabled: true },
      '@opentelemetry/instrumentation-http': { enabled: true },
      '@opentelemetry/instrumentation-pg': { enabled: true },
      '@opentelemetry/instrumentation-redis': { enabled: true },
    }),
  ],
});

// Start the SDK
sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});

// =============================================
// MANUAL SPAN CREATION
// =============================================

const tracer = trace.getTracer('app');

// Example: Tracing an order processing operation
async function processPayment(_orderId: string): Promise<void> {
  // Payment implementation
}

async function updateInventory(_orderId: string): Promise<void> {
  // Inventory implementation
}

export async function processOrder(orderId: string) {
  return tracer.startActiveSpan('processOrder', async (span: Span) => {
    try {
      span.setAttribute('order.id', orderId);

      // Child span for payment processing
      await tracer.startActiveSpan('processPayment', async (paymentSpan: Span) => {
        paymentSpan.setAttribute('payment.method', 'credit_card');
        await processPayment(orderId);
        paymentSpan.end();
      });

      // Child span for inventory update
      await tracer.startActiveSpan('updateInventory', async (inventorySpan: Span) => {
        await updateInventory(orderId);
        inventorySpan.end();
      });

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: (error as Error).message,
      });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}

// =============================================
// SPAN HELPER UTILITIES
// =============================================

export function withSpan<T>(
  name: string,
  attributes: Record<string, string | number | boolean>,
  fn: (span: Span) => Promise<T>
): Promise<T> {
  return tracer.startActiveSpan(name, async (span: Span) => {
    Object.entries(attributes).forEach(([key, value]) => {
      span.setAttribute(key, value);
    });

    try {
      const result = await fn(span);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: (error as Error).message,
      });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}

export default sdk;
export { tracer };
