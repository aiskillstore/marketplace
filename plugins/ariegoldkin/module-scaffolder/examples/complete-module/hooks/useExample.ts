import { useState, useEffect } from "react";

import type { IExampleData, TExampleStatus } from "../types";

interface IUseExampleReturn {
  data: IExampleData[];
  isLoading: boolean;
  error: Error | null;
  status: TExampleStatus;
  refetch: () => Promise<void>;
}

/**
 * useExample - Example Module
 *
 * Demonstrates proper hook structure:
 * - Return type interface with I prefix
 * - use prefix in hook name
 * - State management with proper types
 * - Error handling
 */
export function useExample(): IUseExampleReturn {
  const [data, setData] = useState<IExampleData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [status, setStatus] = useState<TExampleStatus>("pending");

  const fetchData = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulated API call
      // In real code: const response = await trpc.example.list.query();
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const mockData: IExampleData[] = [
        {
          id: "1",
          title: "Example 1",
          description: "First example item",
          createdAt: new Date(),
          isActive: true,
        },
      ];

      setData(mockData);
      setStatus("active");
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
      setStatus("archived");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    data,
    isLoading,
    error,
    status,
    refetch: fetchData,
  };
}
