import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DescriptionEditor } from "./DescriptionEditor";

describe("DescriptionEditor", () => {
  it("renderuje listę odchyleń i pole tekstowe", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(
      <DescriptionEditor
        value="szkic"
        onChange={onChange}
        deviations={[
          {
            nerve_key: "nerw_pośrodkowy",
            parameter: "latency_ms",
            value: 6.5,
            limit: 4.2,
            direction: "above",
          },
        ]}
      />,
    );

    expect(screen.getByText(/Flagi od norm/i)).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: /Treść opisu/i })).toHaveValue(
      "szkic",
    );

    await user.clear(screen.getByRole("textbox", { name: /Treść opisu/i }));
    await user.type(
      screen.getByRole("textbox", { name: /Treść opisu/i }),
      "nowy",
    );

    expect(onChange).toHaveBeenCalled();
  });

  it("informuje gdy brak odchyleń", () => {
    render(
      <DescriptionEditor value="" onChange={() => undefined} deviations={[]} />,
    );

    expect(screen.getByText(/Brak przekroczeń/i)).toBeInTheDocument();
  });
});
