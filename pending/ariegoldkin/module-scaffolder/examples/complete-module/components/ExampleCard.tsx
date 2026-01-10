import React from "react";

import type { IExampleData } from "../types";
import { Button } from "@shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@shared/ui/card";
import { formatDate } from "../utils/helpers";

interface IExampleCardProps {
  data: IExampleData;
  onSelect?: (id: string) => void;
  className?: string;
}

/**
 * ExampleCard - Example Module
 *
 * Demonstrates proper component structure:
 * - Props interface with I prefix
 * - Named function export
 * - React.ReactElement return type
 * - Path aliases for imports
 * - Within-module relative imports
 */
export function ExampleCard({
  data,
  onSelect,
  className = "",
}: IExampleCardProps): React.ReactElement {
  const handleClick = (): void => {
    if (onSelect) {
      onSelect(data.id);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground mb-4">{data.description}</p>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Created: {formatDate(data.createdAt)}
          </span>

          {onSelect && (
            <Button onClick={handleClick} variant="default">
              Select
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
