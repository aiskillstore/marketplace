// SYNTHETIC: checkout orchestrates cart, catalog, currency, shipping, payment and email.
import { Controller, Inject } from '@nestjs/common';
import { GrpcMethod, ClientKafka } from '@nestjs/microservices';
import { OrderPlacedEvent } from '@shop/schemas';
import { PlaceOrderRequestDto, PlaceOrderResponseDto } from './dto/place-order.dto';

@Controller()
export class CheckoutController {
  constructor(@Inject('KAFKA') private readonly kafka: ClientKafka) {}

  @GrpcMethod('CheckoutService', 'PlaceOrder')
  async placeOrder(req: PlaceOrderRequestDto): Promise<PlaceOrderResponseDto> {
    const order = await this.run(req);
    this.kafka.emit('orders', { orderId: order.order.orderId, userId: req.userId, total: order.total, itemCount: 3 } satisfies OrderPlacedEvent);
    return order;
  }

  private async run(_req: PlaceOrderRequestDto): Promise<any> { return {}; }
}
