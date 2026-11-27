import { describe, it, expect } from "vitest";
import { cn } from "@/lib/utils";
// Groups related tests for the cn utility function and provides a description for the test suite
describe("cn utility function", () => {
  it("combines multiple class names", () => {
    const result = cn("text-white", "bg-black");
    expect(result).toBe("text-white bg-black");
  });
  it("ignores false conditional classes", () => {
    const result = cn("text-white", false && "hidden");
    expect(result).toBe("text-white");
  });
  it("resolves conflicting Tailwind classes", () => {
    const result = cn("p-2", "p-4");
    expect(result).toBe("p-4");
  });

});