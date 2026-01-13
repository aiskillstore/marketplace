# API Documentation Generator Examples

## Express.js Example

### Input Route Code
```javascript
// routes/users.js
const express = require('express');
const router = express.Router();

/**
 * Get user by ID
 * @route GET /api/users/:id
 * @param {string} id - User ID
 * @returns {User} 200 - User object
 * @returns {Error} 404 - User not found
 */
router.get('/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

/**
 * Create new user
 * @route POST /api/users
 * @param {CreateUserDTO} request.body - User data
 * @returns {User} 201 - Created user
 */
router.post('/', async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json(user);
});

module.exports = router;
```

### Generated OpenAPI
```yaml
paths:
  /api/users/{id}:
    get:
      summary: Get user by ID
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          description: User ID
          schema:
            type: string
      responses:
        '200':
          description: User object
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /api/users:
    post:
      summary: Create new user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserDTO'
      responses:
        '201':
          description: Created user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

## FastAPI Example

### Input Route Code
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["Users"])

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

class CreateUserRequest(BaseModel):
    email: str
    name: str
    password: str

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user by ID

    Returns user details if found, otherwise 404
    """
    user = await User.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: CreateUserRequest):
    """Create a new user account"""
    user = await User.create(**data.dict())
    return user
```

### Generated OpenAPI
FastAPI auto-generates OpenAPI, but this skill can enhance it with:
- Additional examples from tests
- More detailed descriptions
- Security scheme configurations
- Server configurations

## NestJS Example

### Input Controller Code
```typescript
import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('users')
@Controller('api/users')
export class UsersController {

  @Get(':id')
  @ApiOperation({ summary: 'Get user by ID' })
  @ApiResponse({ status: 200, description: 'User found', type: UserDto })
  @ApiResponse({ status: 404, description: 'User not found' })
  async getUser(@Param('id') id: string): Promise<UserDto> {
    return this.usersService.findOne(id);
  }

  @Post()
  @ApiOperation({ summary: 'Create new user' })
  @ApiResponse({ status: 201, description: 'User created', type: UserDto })
  async createUser(@Body() createUserDto: CreateUserDto): Promise<UserDto> {
    return this.usersService.create(createUserDto);
  }
}
```

### Generated OpenAPI
NestJS with Swagger decorators already provides good documentation. This skill:
- Ensures consistency across all controllers
- Adds missing error responses
- Extracts DTOs for complete schemas
- Validates documentation completeness

## Flask Example

### Input Route Code
```python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class UserResource(Resource):
    """User management endpoints"""

    def get(self, user_id):
        """
        Get user by ID
        ---
        parameters:
          - name: user_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: User details
          404:
            description: User not found
        """
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict()

    def post(self):
        """
        Create new user
        ---
        parameters:
          - name: body
            in: body
            schema:
              type: object
              properties:
                email:
                  type: string
                name:
                  type: string
        responses:
          201:
            description: User created
        """
        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

api.add_resource(UserResource, '/api/users/<user_id>', '/api/users')
```

## Rails Example

### Input Routes
```ruby
# config/routes.rb
Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :users, only: [:index, :show, :create, :update, :destroy]
      post 'auth/login', to: 'authentication#login'
    end
  end
end

# app/controllers/api/v1/users_controller.rb
module Api
  module V1
    class UsersController < ApplicationController
      # GET /api/v1/users
      def index
        @users = User.all
        render json: @users
      end

      # GET /api/v1/users/:id
      def show
        @user = User.find(params[:id])
        render json: @user
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'User not found' }, status: :not_found
      end

      # POST /api/v1/users
      def create
        @user = User.new(user_params)
        if @user.save
          render json: @user, status: :created
        else
          render json: { errors: @user.errors }, status: :unprocessable_entity
        end
      end
    end
  end
end
```

### Generated OpenAPI
```yaml
paths:
  /api/v1/users:
    get:
      summary: List all users
      tags:
        - Users
      responses:
        '200':
          description: Array of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

    post:
      summary: Create new user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
        '422':
          description: Validation errors

  /api/v1/users/{id}:
    get:
      summary: Get user by ID
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User details
        '404':
          description: User not found
```
