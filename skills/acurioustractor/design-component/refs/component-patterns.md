# Component Patterns

## Card Structure
```tsx
<Card className="hover:shadow-lg transition-shadow">
  <CardHeader className="pb-3">
    <Avatar />
    <Badges />
  </CardHeader>
  <CardContent>
    <Title />
    <CulturalContext />
    <Metrics />
  </CardContent>
  <CardFooter>
    <Actions />
  </CardFooter>
</Card>
```

## Avatar Fallback
```tsx
<Avatar>
  <AvatarImage src={avatar_url} alt={display_name} />
  <AvatarFallback className="bg-earth-100 text-earth-700">
    {getInitials(display_name)}
  </AvatarFallback>
</Avatar>
```

## Badge Variants
```tsx
<Badge variant="elder">Elder</Badge>        // Gold
<Badge variant="featured">Featured</Badge>  // Amber
<Badge variant="sacred">Knowledge Keeper</Badge> // Purple
<Badge variant="active">Active</Badge>      // Emerald
```

## Loading States
```tsx
// Skeleton for cards
<Card>
  <Skeleton className="h-12 w-12 rounded-full" />
  <Skeleton className="h-4 w-[200px]" />
  <Skeleton className="h-3 w-[150px]" />
</Card>
```

## Empty States
- Show encouraging message
- Suggest next action
- Use cultural imagery appropriately
