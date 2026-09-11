export function scheduleWindow(now: number): string {
  return new Date(now).toISOString().slice(0, 10);
}
