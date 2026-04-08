/** Replace underscores with spaces, title case (e.g. valentines_day -> Valentines Day). */
export function formatTagLabel(value: string): string {
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}
