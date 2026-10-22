// SYNTHETIC: accounting consumes the orders topic.
import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { OrderPlacedEvent } from '@shop/schemas';

@Controller()
export class OrdersConsumer {
  @EventPattern('orders')
  record(@Payload() event: OrderPlacedEvent): void {}
}
