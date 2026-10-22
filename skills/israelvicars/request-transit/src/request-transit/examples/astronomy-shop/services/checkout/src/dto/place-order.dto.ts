import { IsString, IsEmail, Length, ValidateNested, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

export class AddressDto {
  @IsString() streetAddress!: string;
  @IsString() city!: string;
  @IsOptional() @IsString() state?: string;
  @IsString() country!: string;
  @IsString() zipCode!: string;
}

export class PlaceOrderRequestDto {
  @IsString() userId!: string;
  @IsString() @Length(3, 3) userCurrency!: string;
  @ValidateNested() @Type(() => AddressDto) address!: AddressDto;
  @IsEmail() email!: string;
}

export class OrderItemDto {
  @IsString() productId!: string;
  quantity!: number;
}

export class PlaceOrderResponseDto {
  order!: { orderId: string; shippingTrackingId: string; items: OrderItemDto[] };
  total!: { currencyCode: string; units: number };
}
