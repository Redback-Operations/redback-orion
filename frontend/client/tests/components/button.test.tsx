import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/button";
//verifies react component behavior and user interactions
describe("Button component", () => {
  it("renders the button text", () => {
    render(<Button>Upload Footage</Button>);
    expect(
      screen.getByRole("button", {
        name: "Upload Footage",
      })
    ).toBeInTheDocument();
  });

  it("calls the click handler when clicked", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    render(
      <Button onClick={handleClick}> Upload Footage</Button>
    );
    await user.click(
      screen.getByRole("button", {
        name: "Upload Footage",
      })
    );
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("prevents interaction when disabled", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    render(
      <Button disabled onClick={handleClick}> Upload Footage </Button>
    );
    const button = screen.getByRole("button", {
      name: "Upload Footage",
    });
    expect(button).toBeDisabled();
    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

});