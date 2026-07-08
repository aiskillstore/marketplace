#!/usr/bin/env bun
/**
 * TUI Filter Manager
 * Manages session filtering and sorting
 */

import type { TmuxSession, SessionCategory, SessionStatus } from './types/index.js';

export interface FilterOptions {
  category?: SessionCategory | 'all';
  status?: SessionStatus | 'all';
  searchQuery?: string;
  sortBy?: 'name' | 'createdAt' | 'lastActivityAt';
  sortOrder?: 'asc' | 'desc';
}

class FilterManager {
  private filters: FilterOptions;

  constructor() {
    this.filters = {
      category: 'all',
      status: 'all',
      searchQuery: '',
      sortBy: 'lastActivityAt',
      sortOrder: 'desc',
    };
  }

  setCategory(category: SessionCategory | 'all'): void {
    this.filters.category = category;
  }

  setStatus(status: SessionStatus | 'all'): void {
    this.filters.status = status;
  }

  setSearchQuery(query: string): void {
    this.filters.searchQuery = query;
  }

  setSortBy(sortBy: 'name' | 'createdAt' | 'lastActivityAt'): void {
    this.filters.sortBy = sortBy;
  }

  setSortOrder(order: 'asc' | 'desc'): void {
    this.filters.sortOrder = order;
  }

  getFilters(): FilterOptions {
    return { ...this.filters };
  }

  reset(): void {
    this.filters = {
      category: 'all',
      status: 'all',
      searchQuery: '',
      sortBy: 'lastActivityAt',
      sortOrder: 'desc',
    };
  }

  apply(sessions: TmuxSession[]): TmuxSession[] {
    let filtered = [...sessions];

    // Filter by category
    if (this.filters.category && this.filters.category !== 'all') {
      filtered = filtered.filter(s => s.category === this.filters.category);
    }

    // Filter by status
    if (this.filters.status && this.filters.status !== 'all') {
      filtered = filtered.filter(s => s.status === this.filters.status);
    }

    // Filter by search query
    if (this.filters.searchQuery && this.filters.searchQuery.trim()) {
      const query = this.filters.searchQuery.toLowerCase();
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(query) ||
        s.id.toLowerCase().includes(query) ||
        s.command.toLowerCase().includes(query)
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (this.filters.sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'createdAt':
          comparison = a.createdAt.localeCompare(b.createdAt);
          break;
        case 'lastActivityAt':
          comparison = a.lastActivityAt.localeCompare(b.lastActivityAt);
          break;
      }

      return this.filters.sortOrder === 'desc' ? -comparison : comparison;
    });

    return filtered;
  }

  getFilterSummary(sessions: TmuxSession[]): string {
    const filtered = this.apply(sessions);
    const parts: string[] = [];

    if (this.filters.category && this.filters.category !== 'all') {
      parts.push(`分类: ${this.filters.category}`);
    }

    if (this.filters.status && this.filters.status !== 'all') {
      parts.push(`状态: ${this.filters.status}`);
    }

    if (this.filters.searchQuery && this.filters.searchQuery.trim()) {
      parts.push(`搜索: "${this.filters.searchQuery}"`);
    }

    if (parts.length === 0) {
      return `显示全部 ${sessions.length} 个会话`;
    }

    return `${parts.join(' | ')} - 显示 ${filtered.length}/${sessions.length}`;
  }
}

export { FilterManager };