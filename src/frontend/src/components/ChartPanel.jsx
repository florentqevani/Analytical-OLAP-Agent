import React, { useRef, useState } from "react";
import html2canvas from "html2canvas";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Cell,
    LabelList,
    ResponsiveContainer,
    PieChart,
    Pie,
    Legend,
    LineChart,
    Line,
} from "recharts";

// Excel-style distinct colour palette
const PALETTE = [
    "#4472C4",
    "#ED7D31",
    "#A9D18E",
    "#FFC000",
    "#5B9BD5",
    "#70AD47",
    "#FF6B6B",
    "#9E7BB5",
    "#4ECDC4",
    "#FFE66D",
];

const CHART_TYPES = ["Bar", "Pie", "Line"];

function formatValue(v) {
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
    return Number.isInteger(v) ? String(v) : v.toFixed(2);
}

function CustomTooltip({ active, payload, label, unit }) {
    if (!active || !payload || payload.length === 0) return null;
    const entry = payload[0];
    return (
        <div className="chart-tooltip">
            <p className="tooltip-label">{label || entry.name}</p>
            <p className="tooltip-value" style={{ color: entry.fill || entry.stroke || "#e0f0ff" }}>
                {formatValue(entry.value ?? 0)}
                {unit ? ` ${unit}` : ""}
            </p>
        </div>
    );
}

function BarChartView({ data, unit }) {
    return (
        <ResponsiveContainer width="100%" height={320}>
            <BarChart
                data={data}
                margin={{ top: 30, right: 24, left: 10, bottom: 64 }}
                barCategoryGap="32%"
            >
                <CartesianGrid
                    strokeDasharray="4 2"
                    stroke="rgba(150,185,220,0.15)"
                    vertical={false}
                />
                <XAxis
                    dataKey="name"
                    tick={{ fill: "#9ab4cc", fontSize: 11 }}
                    angle={-38}
                    textAnchor="end"
                    interval={0}
                    stroke="rgba(108,158,195,0.35)"
                    tickLine={false}
                />
                <YAxis
                    tick={{ fill: "#9ab4cc", fontSize: 11 }}
                    tickFormatter={formatValue}
                    stroke="rgba(108,158,195,0.35)"
                    tickLine={false}
                    width={68}
                />
                <Tooltip content={<CustomTooltip unit={unit} />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={60}>
                    {data.map((_, i) => (
                        <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                    ))}
                    <LabelList
                        dataKey="value"
                        position="top"
                        formatter={formatValue}
                        style={{ fill: "#d5eaff", fontSize: 11, fontWeight: 600 }}
                    />
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

const RADIAN = Math.PI / 180;

function renderPieLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {
    if (percent < 0.04) return null;
    const r = innerRadius + (outerRadius - innerRadius) * 0.55;
    const x = cx + r * Math.cos(-midAngle * RADIAN);
    const y = cy + r * Math.sin(-midAngle * RADIAN);
    return (
        <text
            x={x}
            y={y}
            fill="#fff"
            textAnchor="middle"
            dominantBaseline="central"
            fontSize={11}
            fontWeight={700}
        >
            {`${(percent * 100).toFixed(1)}%`}
        </text>
    );
}

function PieChartView({ data }) {
    return (
        <ResponsiveContainer width="100%" height={320}>
            <PieChart>
                <Pie
                    data={data}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="46%"
                    outerRadius={118}
                    labelLine={false}
                    label={renderPieLabel}
                >
                    {data.map((_, i) => (
                        <Cell
                            key={i}
                            fill={PALETTE[i % PALETTE.length]}
                            stroke="rgba(0,0,0,0.35)"
                            strokeWidth={2}
                        />
                    ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                    wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
                    formatter={(value) => (
                        <span style={{ color: "#b8d4ec" }}>{value}</span>
                    )}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}

function LineChartView({ data, unit }) {
    return (
        <ResponsiveContainer width="100%" height={320}>
            <LineChart
                data={data}
                margin={{ top: 30, right: 24, left: 10, bottom: 64 }}
            >
                <CartesianGrid
                    strokeDasharray="4 2"
                    stroke="rgba(150,185,220,0.15)"
                />
                <XAxis
                    dataKey="name"
                    tick={{ fill: "#9ab4cc", fontSize: 11 }}
                    angle={-38}
                    textAnchor="end"
                    interval={0}
                    stroke="rgba(108,158,195,0.35)"
                    tickLine={false}
                />
                <YAxis
                    tick={{ fill: "#9ab4cc", fontSize: 11 }}
                    tickFormatter={formatValue}
                    stroke="rgba(108,158,195,0.35)"
                    tickLine={false}
                    width={68}
                />
                <Tooltip content={<CustomTooltip unit={unit} />} />
                <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#4472C4"
                    strokeWidth={2.5}
                    dot={(props) => {
                        const { cx, cy, index } = props;
                        return (
                            <circle
                                key={index}
                                cx={cx}
                                cy={cy}
                                r={5}
                                fill={PALETTE[index % PALETTE.length]}
                                stroke="#fff"
                                strokeWidth={1.5}
                            />
                        );
                    }}
                    activeDot={{ r: 7, fill: "#ED7D31", stroke: "#fff", strokeWidth: 2 }}
                />
            </LineChart>
        </ResponsiveContainer>
    );
}

async function captureChartAsImage(containerEl, title) {
    const canvas = await html2canvas(containerEl, {
        backgroundColor: "#0a1f35",
        scale: 2,
        useCORS: true,
        logging: false,
    });

    return new Promise((resolve, reject) => {
        canvas.toBlob(async (pngBlob) => {
            if (!pngBlob) {
                reject(new Error("toBlob failed"));
                return;
            }
            try {
                await navigator.clipboard.write([
                    new ClipboardItem({ "image/png": pngBlob }),
                ]);
                resolve("copied");
            } catch {
                // Clipboard API blocked → fall back to file download
                const a = document.createElement("a");
                a.href = URL.createObjectURL(pngBlob);
                a.download = `${title || "chart"}.png`;
                a.click();
                resolve("downloaded");
            }
        }, "image/png");
    });
}

export default function ChartPanel({ chartModel }) {
    const [chartType, setChartType] = useState("Bar");
    const [copyLabel, setCopyLabel] = useState("Copy");
    const wrapRef = useRef(null);

    const data = (chartModel?.series ?? []).map((item) => ({
        name: item.label,
        value: item.value,
    }));
    const title = chartModel?.title || "Chart";
    const unit = chartModel?.unit || "";
    const hasData = data.length > 0;

    async function handleCopy() {
        const containerEl = wrapRef.current;
        if (!containerEl) return;
        setCopyLabel("Copying…");
        try {
            const outcome = await captureChartAsImage(containerEl, title);
            setCopyLabel(outcome === "copied" ? "✓ Copied!" : "✓ Saved!");
        } catch {
            setCopyLabel("Failed");
        } finally {
            setTimeout(() => setCopyLabel("Copy"), 2200);
        }
    }

    return (
        <section className="panel charts-panel">
            <div className="panel-head chart-panel-head">
                <div className="chart-head-left">
                    <h2>Charts</h2>
                    <span className="pill metric-pill">
                        {chartModel?.dimension || "—"} / {chartModel?.metric || "—"}
                    </span>
                </div>
                <div className="chart-head-right">
                    <div className="chart-type-toggle">
                        {CHART_TYPES.map((t) => (
                            <button
                                key={t}
                                type="button"
                                className={`toggle-btn${chartType === t ? " toggle-btn-active" : ""}`}
                                onClick={() => setChartType(t)}
                            >
                                {t}
                            </button>
                        ))}
                    </div>
                    {hasData && (
                        <button
                            type="button"
                            className="secondary-btn copy-btn"
                            onClick={handleCopy}
                        >
                            {copyLabel}
                        </button>
                    )}
                </div>
            </div>

            {!hasData ? (
                <p className="meta">
                    Run an agent to generate chart data from the analysis response.
                </p>
            ) : (
                <div className="chart-container" ref={wrapRef}>
                    <p className="chart-title">
                        {title}
                        {unit ? ` (${unit})` : ""}
                    </p>
                    {chartType === "Bar" && <BarChartView data={data} unit={unit} />}
                    {chartType === "Pie" && <PieChartView data={data} />}
                    {chartType === "Line" && <LineChartView data={data} unit={unit} />}
                </div>
            )}
        </section>
    );
}
