"use client";

import { useEffect, useState } from "react";
import { getUsage, UsageResponse } from "../lib/api";

const metricLabels: Record<string, string> = {
  message: "本月消息",
  code_execution: "本月代码执行",
  uploaded_file_bytes: "上传文件大小",
  generated_file_bytes: "生成文件大小",
};

function formatValue(metric: string, value: number) {
  if (metric.endsWith("_bytes")) {
    if (value >= 1024 * 1024) return `${(value / 1024 / 1024).toFixed(2)} MB`;
    if (value >= 1024) return `${(value / 1024).toFixed(2)} KB`;
    return `${value} B`;
  }
  return String(value);
}

export function UsagePanel({ token, refreshKey }: { token: string; refreshKey: number }) {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getUsage(token)
      .then(setUsage)
      .catch((err) => setError(err instanceof Error ? err.message : "用量加载失败"));
  }, [token, refreshKey]);

  return (
    <aside className="panel usage-panel">
      <h3>用量</h3>
      {error ? <p className="error">{error}</p> : null}
      {usage?.items.map((item) => {
        const percent = item.limit ? Math.min(100, Math.round((item.used / item.limit) * 100)) : 0;
        return (
          <div className="usage-item" key={item.metric}>
            <div className="usage-row">
              <span>{metricLabels[item.metric] ?? item.metric}</span>
              <b>
                {formatValue(item.metric, item.used)}
                {item.limit ? ` / ${formatValue(item.metric, item.limit)}` : ""}
              </b>
            </div>
            {item.limit ? <progress value={percent} max={100} /> : null}
          </div>
        );
      })}
    </aside>
  );
}
