// SYNTHETIC: cart service, gRPC via NestJS. DTOs come from the shared package.
import { Controller } from '@nestjs/common';
import { GrpcMethod } from '@nestjs/microservices';
import { GetCartRequestDto, CartDto, EmptyCartRequestDto } from '@shop/schemas';

@Controller()
export class CartController {
  @GrpcMethod('CartService', 'GetCart')
  async getCart(req: GetCartRequestDto): Promise<CartDto> {
    return { userId: req.userId, items: [] };
  }

  @GrpcMethod('CartService', 'EmptyCart')
  async emptyCart(req: EmptyCartRequestDto): Promise<void> {}
}
