"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

const API = "http://127.0.0.1:8000";

const COLORS = ["#22c55e", "#f43f5e", "#a5b4fc", "#8b5cf6", "#06b6d4"];

export default function Home() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [query, setQuery] = useState("");
  const [chat, setChat] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API}/dashboard`).then((res) => setDashboard(res.data));
    axios.get(`${API}/brands`).then((res) => setBrands(res.data.brands));
  }, []);

  useEffect(() => {
    if (!selectedBrand) {
      axios.get(`${API}/dashboard`).then((res) => setDashboard(res.data));
      return;
    }

    axios
      .post(`${API}/brand-dashboard`, { brand: selectedBrand })
      .then((res) => setDashboard(res.data));
  }, [selectedBrand]);

  const askAI = async () => {
    if (!query.trim()) return;

    setLoading(true);
    const res = await axios.post(`${API}/chat`, {
      query,
      k: 3,
      model: "llama3:latest",
    });
    setChat(res.data);
    setLoading(false);
  };

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-8">
        Loading dashboard...
      </div>
    );
  }

  const sentimentData = Object.entries(dashboard.sentiment_overview || {}).map(
    ([name, value]: any) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value: Number((value * 100).toFixed(1)),
    })
  );

  const aspectData = Object.entries(dashboard.top_aspects || {}).map(
    ([name, value]: any) => ({
      aspect: name.charAt(0).toUpperCase() + name.slice(1),
      rating: Number(Number(value).toFixed(2)),
    })
  );

  const volumeData = Object.entries(dashboard.review_volume || {}).map(
    ([month, count]: any) => ({
      month,
      reviews: Number(count),
    })
  );

  const issueData = Object.entries(dashboard.common_issues || {}).map(
    ([name, count]: any) => ({
      issue: name.charAt(0).toUpperCase() + name.slice(1),
      count: Number(count),
    })
  );

  return (
    <main className="min-h-screen bg-[#0b1220] text-white p-8">
      <h1 className="text-3xl font-bold mb-2">
        Customer Review Intelligence System
      </h1>

      <p className="text-slate-400 mb-6">
        {selectedBrand
          ? `Brand-specific review analytics for ${selectedBrand}`
          : "Global analytics across all analyzed headphone reviews"}
      </p>

      <div className="mb-8">
        <label className="text-sm text-slate-300 mr-3">Select view:</label>
        <select
          value={selectedBrand}
          onChange={(e) => setSelectedBrand(e.target.value)}
          className="bg-slate-900 border border-purple-500 rounded-lg px-4 py-3 text-white min-w-[240px]"
        >
          <option value="">Global Dashboard</option>
          {brands.map((brand) => (
            <option key={brand} value={brand}>
              {brand}
            </option>
          ))}
        </select>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
        <MetricCard title="Reviews Analyzed" value={dashboard.total_reviews} />
        <MetricCard title="Average Rating" value={`${dashboard.average_rating} / 5`} />
        <MetricCard title="Products" value={dashboard.total_products} />
        <MetricCard title="Aspects Tracked" value={dashboard.total_aspects} />
      </section>

      {dashboard.pm_summary && (
        <section className="bg-slate-900/80 border border-white/10 rounded-2xl p-5 mb-8">
          <h2 className="text-xl font-semibold mb-2">Brand Summary</h2>
          <p className="text-slate-300">{dashboard.pm_summary}</p>
        </section>
      )}

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
        <ChartCard
          title="Sentiment Overview"
          subtitle="Percentage split of positive, neutral, and negative reviews"
        >
          <ResponsiveContainer width="100%" height={290}>
            <PieChart>
              <Pie
                data={sentimentData}
                dataKey="value"
                nameKey="name"
                innerRadius={65}
                outerRadius={100}
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {sentimentData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Top Aspects by Average Rating"
          subtitle="Higher rating means customers are more satisfied with that aspect"
        >
          <ResponsiveContainer width="100%" height={290}>
            <BarChart data={aspectData} margin={{ bottom: 35 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="aspect"
                stroke="#cbd5e1"
                angle={-25}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                stroke="#cbd5e1"
                domain={[0, 5]}
                label={{
                  value: "Average Rating (0–5)",
                  angle: -90,
                  position: "insideLeft",
                  fill: "#cbd5e1",
                }}
              />
              <Tooltip />
              <Bar dataKey="rating" name="Average Rating" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Review Volume Over Time"
          subtitle="Number of reviews received in recent months"
        >
          <ResponsiveContainer width="100%" height={290}>
            <BarChart data={volumeData} margin={{ bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="month"
                stroke="#cbd5e1"
                angle={-20}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                stroke="#cbd5e1"
                label={{
                  value: "Review Count",
                  angle: -90,
                  position: "insideLeft",
                  fill: "#cbd5e1",
                }}
              />
              <Tooltip />
              <Bar dataKey="reviews" name="Review Count" fill="#06b6d4" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        <ChartCard
          title="Common Issues"
          subtitle="Most frequent aspects mentioned in low-rated reviews"
        >
          <div className="space-y-4">
            {issueData.map((item) => (
              <div
                key={item.issue}
                className="flex items-center justify-between border-b border-white/10 pb-3"
              >
                <span className="text-slate-200">{item.issue}</span>
                <span className="text-rose-400 font-semibold">
                  {item.count} negative mentions
                </span>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard
          title="AI Chat"
          subtitle="Ask questions grounded in retrieved customer review evidence"
        >
          <div className="flex gap-3 mb-4">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: What are the biggest problems with Bose headphones?"
              className="flex-1 bg-slate-950 border border-white/10 rounded-xl px-4 py-3 text-white outline-none"
            />
            <button
              onClick={askAI}
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 rounded-xl px-6 py-3 font-semibold"
            >
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {chat && (
            <div className="space-y-4 text-sm">
              <div>
                <h3 className="text-purple-300 font-semibold mb-1">Summary</h3>
                <p className="text-slate-300">{chat.summary}</p>
              </div>

              <div>
                <h3 className="text-purple-300 font-semibold mb-1">Key Evidence</h3>
                <p className="text-slate-300 whitespace-pre-line">
                  {chat.key_evidence}
                </p>
              </div>

              <div>
                <h3 className="text-purple-300 font-semibold mb-1">
                  Recommendation
                </h3>
                <p className="text-slate-300">{chat.recommendation}</p>
              </div>
            </div>
          )}
        </ChartCard>
      </section>
    </main>
  );
}

function MetricCard({ title, value }: any) {
  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-5">
      <p className="text-slate-400 text-sm">{title}</p>
      <h2 className="text-2xl font-bold mt-2">{value}</h2>
    </div>
  );
}

function ChartCard({ title, subtitle, children }: any) {
  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-5">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-slate-400 text-sm mb-4">{subtitle}</p>
      {children}
    </div>
  );
}