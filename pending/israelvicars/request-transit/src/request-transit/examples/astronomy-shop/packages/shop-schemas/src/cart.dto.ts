import { IsString, IsInt, Min, ValidateNested, IsArray } from 'class-validator';
import { Type } from 'class-transformer';

export class CartItemDto {
  @IsString() productId!: string;
  @IsInt() @Min(1) quantity!: number;
}

export class GetCartRequestDto {
  @IsString() userId!: string;
}

export class CartDto {
  @IsString() userId!: string;
  @IsArray() @ValidateNested({ each: true }) @Type(() => CartItemDto) items!: CartItemDto[];
}

export class EmptyCartRequestDto {
  @IsString() userId!: string;
}
