/** @vitest-environment jsdom */

import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { ChartChipButton } from "../src/components/discovery/chart-controls/ChartChipButton";
import { ChartComboControl } from "../src/components/discovery/chart-controls/ChartComboControl";
import { ChartControlField } from "../src/components/discovery/chart-controls/ChartControlField";
import { ChartNumberInputControl } from "../src/components/discovery/chart-controls/ChartNumberInputControl";
import { ChartSelectControl } from "../src/components/discovery/chart-controls/ChartSelectControl";
import { ChartSurfaceCard } from "../src/components/discovery/chart-controls/ChartSurfaceCard";
import { ChartToggleGroup } from "../src/components/discovery/chart-controls/ChartToggleGroup";
import {
  ChartTooltipDate,
  ChartTooltipDivider,
  ChartTooltipRoot,
  ChartTooltipText,
  ChartTooltipValue,
} from "../src/components/discovery/chart-controls/ChartTooltip";
import { renderMarkup } from "./test-utils";

vi.mock("@heroui/react", () => {
  type MockBaseProps = {
    children?: React.ReactNode;
    className?: string;
    [key: string]: unknown;
  };

  const Button = ({
    children,
    isDisabled,
    onPress,
    ...props
  }: MockBaseProps & { isDisabled?: boolean; onPress?: () => void }) => (
    <button
      {...(props as React.ButtonHTMLAttributes<HTMLButtonElement>)}
      disabled={Boolean(isDisabled)}
      type="button"
      onClick={() => {
        onPress?.();
      }}
    >
      {children}
    </button>
  );

  const ButtonGroup = ({
    children,
    isDisabled,
    ...props
  }: MockBaseProps & { isDisabled?: boolean }) => (
    <div
      {...(props as React.HTMLAttributes<HTMLDivElement>)}
      data-group-disabled={isDisabled ? "true" : "false"}
    >
      {children}
    </div>
  );

  const Card = ({ children, ...props }: MockBaseProps) => (
    <section {...(props as React.HTMLAttributes<HTMLElement>)}>{children}</section>
  );

  const Input = ({
    onChange,
    ...props
  }: MockBaseProps & {
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  }) => <input {...(props as React.InputHTMLAttributes<HTMLInputElement>)} onChange={onChange} />;

  const Select = ({
    children,
    isDisabled,
    onChange,
    ...props
  }: MockBaseProps & {
    isDisabled?: boolean;
    onChange?: (value: string | null) => void;
  }) => {
    const testId = typeof props["data-testid"] === "string" ? props["data-testid"] : "select";

    return (
      <div
        {...(props as React.HTMLAttributes<HTMLDivElement>)}
        data-select-disabled={isDisabled ? "true" : "false"}
      >
        <button
          data-testid={`${testId}-change`}
          type="button"
          onClick={() => {
            onChange?.("mock-value");
          }}
        >
          trigger-change
        </button>
        <button
          data-testid={`${testId}-change-null`}
          type="button"
          onClick={() => {
            onChange?.(null);
          }}
        >
          trigger-change-null
        </button>
        {children}
      </div>
    );
  };

  Select.Trigger = ({ children }: MockBaseProps) => <>{children}</>;
  Select.Value = () => <span data-testid="select-value" />;
  Select.Indicator = () => <span data-testid="select-indicator" />;
  Select.Popover = ({ children, className }: MockBaseProps) => (
    <div data-popover-class={className ?? ""}>{children}</div>
  );

  const ComboBox = ({
    children,
    inputValue,
    isDisabled,
    items,
    onInputChange,
    onSelectionChange,
    selectedKey,
    ...props
  }: MockBaseProps & {
    inputValue?: string;
    isDisabled?: boolean;
    items?: unknown[];
    onInputChange?: (value: string) => void;
    onSelectionChange?: (value: string) => void;
    selectedKey?: string;
  }) => {
    const testId = typeof props["data-testid"] === "string" ? props["data-testid"] : "combo";

    void inputValue;
    void items;
    void selectedKey;

    return (
      <div
        {...(props as React.HTMLAttributes<HTMLDivElement>)}
        data-combo-disabled={isDisabled ? "true" : "false"}
      >
        <input
          aria-label={String(props["aria-label"] ?? "")}
          data-testid={`${testId}-input`}
          onChange={(event) => {
            onInputChange?.((event.target as HTMLInputElement).value);
          }}
        />
        <button
          data-testid={`${testId}-select`}
          type="button"
          onClick={() => {
            onSelectionChange?.("mock-selection");
          }}
        >
          select-value
        </button>
        {children}
      </div>
    );
  };

  ComboBox.InputGroup = ({ children, ...props }: MockBaseProps) => (
    <div {...(props as React.HTMLAttributes<HTMLDivElement>)}>{children}</div>
  );
  ComboBox.Trigger = ({ children }: MockBaseProps) => <>{children}</>;
  ComboBox.Input = ({ ...props }: MockBaseProps) => (
    <span {...(props as React.HTMLAttributes<HTMLSpanElement>)} data-testid="combo-input-proxy" />
  );
  ComboBox.Indicator = () => <span data-testid="combo-indicator" />;
  ComboBox.Popover = ({ children, className }: MockBaseProps) => (
    <div data-popover-class={className ?? ""}>{children}</div>
  );

  const ListBox = ({ children }: MockBaseProps) => <ul>{children}</ul>;
  ListBox.Item = ({ children, className, id, textValue }: MockBaseProps) => (
    <li data-class={className ?? ""} data-id={id} data-text={textValue}>
      {children}
    </li>
  );
  const ListBoxItem = ({ children, className, id, textValue }: MockBaseProps) => (
    <li data-class={className ?? ""} data-id={id} data-text={textValue}>
      {children}
    </li>
  );

  const Spinner = (props: MockBaseProps) =>
    React.createElement("span", props as React.HTMLAttributes<HTMLSpanElement>, "loading");

  return {
    Button,
    ButtonGroup,
    Card,
    ComboBox,
    Input,
    ListBox,
    ListBoxItem,
    Select,
    Spinner,
  };
});

describe("chart control shared components", () => {
  it("renders tooltip primitives with defaults and overrides", () => {
    const markup = renderMarkup(
      <ChartTooltipRoot className="custom-root">
        <ChartTooltipDate>Date</ChartTooltipDate>
        <ChartTooltipDivider className="custom-divider" />
        <ChartTooltipValue className="custom-value">12.3</ChartTooltipValue>
        <ChartTooltipText className="custom-text">Details</ChartTooltipText>
      </ChartTooltipRoot>,
    );

    expect(markup).toContain("custom-root");
    expect(markup).toContain("custom-divider");
    expect(markup).toContain("custom-value");
    expect(markup).toContain("custom-text");
    expect(markup).toContain("Date");
  });

  it("renders tooltip value with default styling when no class override is provided", () => {
    const markup = renderMarkup(
      <ChartTooltipRoot>
        <ChartTooltipValue>99.9</ChartTooltipValue>
      </ChartTooltipRoot>,
    );

    expect(markup).toContain("mt-5");
    expect(markup).toContain("99.9");
  });

  it("renders chart surface with optional title and test id", () => {
    const markup = renderMarkup(
      <ChartSurfaceCard className="surface-extra" testId="surface-card" title="Trend">
        <div>Body</div>
      </ChartSurfaceCard>,
    );

    expect(markup).toContain("surface-extra");
    expect(markup).toContain('data-testid="surface-card"');
    expect(markup).toContain("Trend");
  });

  it("renders chart surface without optional title/test-id overrides", () => {
    const markup = renderMarkup(
      <ChartSurfaceCard>
        <div>Body</div>
      </ChartSurfaceCard>,
    );

    expect(markup).not.toContain("data-testid");
    expect(markup).not.toContain("<h2");
  });

  it("renders chart control field with optional htmlFor", () => {
    const markup = renderMarkup(
      <ChartControlField htmlFor="offset" label="Offset">
        <input id="offset" />
      </ChartControlField>,
    );

    expect(markup).toContain("Offset");
    expect(markup).toContain('for="offset"');
  });

  it("toggles options and ignores disabled button presses", () => {
    const onChange = vi.fn();

    render(
      <ChartToggleGroup
        activeValue="a"
        options={[
          { label: "A", value: "a" },
          { disabled: true, label: "B", value: "b" },
        ]}
        onChange={onChange}
      />,
    );

    fireEvent.click(screen.getByText("A"));
    fireEvent.click(screen.getByText("B"));

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith("a");
  });

  it("renders chip button with default and custom accent colors", () => {
    const onPress = vi.fn();

    const { rerender } = render(<ChartChipButton label="Dataset" onPress={onPress} />);
    fireEvent.click(screen.getByText("Dataset"));

    rerender(<ChartChipButton accentColor="#123456" label="Dataset" onPress={onPress} />);

    expect(onPress).toHaveBeenCalledTimes(1);
    expect(document.body.innerHTML).toContain("rgb(18, 52, 86)");
  });

  it("maps select changes and null values", () => {
    const onChange = vi.fn();

    render(
      <ChartSelectControl
        isDisabled
        label="Mode"
        onChange={onChange}
        optionClassName="option"
        options={[{ label: "Observed", value: "observed" }]}
        placeholder="Select mode"
        popoverClassName="popover"
        testId="mode-select"
        value="observed"
      />,
    );

    fireEvent.click(screen.getByTestId("mode-select-change"));
    fireEvent.click(screen.getByTestId("mode-select-change-null"));

    expect(onChange).toHaveBeenNthCalledWith(1, "mock-value");
    expect(onChange).toHaveBeenNthCalledWith(2, "");
    expect(document.body.innerHTML).toContain("popover");
    expect(document.body.innerHTML).toContain("option");
  });

  it("renders select control without optional class overrides", () => {
    const onChange = vi.fn();

    render(
      <ChartSelectControl
        label="Baseline"
        onChange={onChange}
        options={[{ label: "Rolling", value: "rolling" }]}
        placeholder="Select baseline"
        value="rolling"
      />,
    );

    fireEvent.click(screen.getByTestId("select-change"));
    expect(onChange).toHaveBeenCalledWith("mock-value");
  });

  it("forwards number input changes", () => {
    const onChange = vi.fn();

    render(
      <ChartNumberInputControl
        className="number-control"
        disabled
        id="offset"
        label="Offset"
        max={12}
        min={1}
        value="1"
        onChange={onChange}
      />,
    );

    fireEvent.change(screen.getByLabelText("Offset"), { target: { value: "3" } });

    expect(onChange).toHaveBeenCalledWith("3");
    expect(document.body.innerHTML).toContain("number-control");
  });

  it("renders number input control with default class path", () => {
    const onChange = vi.fn();

    render(<ChartNumberInputControl id="window" label="Window" value="2" onChange={onChange} />);

    fireEvent.change(screen.getByLabelText("Window"), { target: { value: "4" } });
    expect(onChange).toHaveBeenCalledWith("4");
  });

  it("renders combo control including empty fallback and loading sentinel", () => {
    const onInputChange = vi.fn();

    render(
      <ChartComboControl
        className="combo-control"
        emptyLabel="No options"
        inputValue=""
        label="Date"
        onInputChange={onInputChange}
        onSelect={onInputChange}
        options={[]}
        selectedValue=""
        testId="combo"
      />,
    );

    fireEvent.change(screen.getByTestId("combo-input"), { target: { value: "2026" } });

    expect(onInputChange).toHaveBeenCalledWith("2026");
    expect(document.body.innerHTML).toContain("No options");
  });

  it("renders combo control paginated sentinel and loading states", () => {
    const onSelect = vi.fn();

    render(
      <ChartComboControl
        emptyLabel="No options"
        inputValue=""
        label="Date"
        onSelect={onSelect}
        options={[{ label: "Jan 2024", value: "2024-01" }]}
        paginated
        selectedValue=""
        testId="combo"
        visibleCount={0}
        isInfiniteLoading
      />,
    );

    const comboSelectButtons = screen.getAllByTestId("combo-select");
    fireEvent.click(comboSelectButtons.at(-1) as HTMLElement);

    expect(onSelect).toHaveBeenCalledWith("mock-selection");
    expect(screen.getByTestId("combo-infinite-sentinel")).toBeTruthy();
    expect(screen.getByTestId("combo-infinite-loading")).toBeTruthy();
  });
});
