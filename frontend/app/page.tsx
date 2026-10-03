"use client";

import { useRef, useState, type ReactNode } from "react";

type RiskIndicator = {
  id: string;
  title: string;
  severity: string;
  explanation: string;
  matched_terms: string[];
};

type Claim = {
  claim: string;
  source: string;
  verification: string;
};

type TimelineItem = {
  date: string;
  event: string;
};

type AIClaim = {
  claim: string;
  evidence: string;
  verification: string;
};

type AITimelineItem = {
  date_or_time: string;
  event: string;
  source: string;
};

type AIData = {
  incident_narrative: string;
  claims: AIClaim[];
  timeline: AITimelineItem[];
  missing_evidence: string[];
  plain_language_explanation: string;
  documentation_questions: string[];
};

type AIReconstruction = {
  enabled: boolean;
  model?: string;
  error?: string;
  data?: AIData;
};

type Analysis = {
  success: boolean;
  assessment: {
    level: string;
    indicator_score: number;
    confidence_note: string;
  };
  summary: string;
  risk_indicators: RiskIndicator[];
  claims: Claim[];
  timeline: TimelineItem[];
  safe_actions: string[];
  limitations: string[];
  ai_reconstruction?: AIReconstruction;
};

const API = "http://127.0.0.1:8000";

const demoEvidence = `1 Oct, 10:42 AM

SEBI approved investment. Guaranteed 30% return in 30 days. Limited slots available.

2 Oct, 6:15 PM

Your investment has generated ₹18,500 profit.

3 Oct, 11:30 AM

Pay ₹4,999 processing fee to withdraw your profit.

4 Oct, 9:20 AM

Install this application and share your screen to complete withdrawal.`;

export default function Home() {
  const [evidence, setEvidence] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDemo = () => {
    setEvidence(demoEvidence);
    setAnalysis(null);
    setError("");
  };

  const analyzeIncident = async () => {
    if (!evidence.trim()) {
      setError("Please provide some incident evidence first.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const res = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          evidence,
          language: "en",
        }),
      });

      if (!res.ok) {
        throw new Error("The analysis service returned an error.");
      }

      const data = await res.json();

      if (!data.success) {
        throw new Error(data.error || "Analysis failed.");
      }

      setAnalysis(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the analysis service."
      );
    } finally {
      setLoading(false);
    }
  };

  const uploadEvidence = async (file: File) => {
    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("language", "en");

      const isPdf = file.type === "application/pdf";

      const res = await fetch(
        isPdf ? `${API}/analyze-pdf` : `${API}/analyze-image`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) {
        throw new Error("The evidence analysis service returned an error.");
      }

      const data = await res.json();

      if (!data.success) {
        throw new Error(
          data.error || "Unable to read the uploaded evidence."
        );
      }

      setEvidence(data.extracted_text || "");
      setAnalysis(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze the uploaded evidence."
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!evidence.trim()) {
      setError("There is no incident evidence to include in the report.");
      return;
    }

    setReportLoading(true);
    setError("");

    try {
      const res = await fetch(`${API}/generate-report`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          evidence,
          language: "en",
          ai_reconstruction: analysis?.ai_reconstruction,
        }),
      });

      if (!res.ok) {
        throw new Error("Unable to generate the incident report.");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "invoresc-incident-report.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate the incident report."
      );
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="mb-12">
          <div className="mb-3 text-sm font-semibold tracking-[0.25em] text-cyan-400">
            INVORESC
          </div>

          <h1 className="max-w-4xl text-4xl font-bold tracking-tight sm:text-5xl">
            Understand suspicious financial incidents before they become bigger
            problems.
          </h1>

          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-400">
            Reconstruct what happened, identify concerning patterns, organize
            evidence, and understand safer next steps.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
          <div className="mb-5 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-xl font-semibold">Incident evidence</h2>

              <p className="mt-1 text-sm text-slate-400">
                Paste messages, emails, payment details, or other relevant
                text.
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,application/pdf"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];

                if (file) {
                  uploadEvidence(file);
                }

                e.target.value = "";
              }}
            />

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
                className="rounded-xl border border-slate-700 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-500 hover:text-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Upload evidence
              </button>

              <button
                type="button"
                onClick={loadDemo}
                disabled={loading}
                className="rounded-xl border border-slate-700 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan-500 hover:text-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Load demo
              </button>
            </div>
          </div>

          <textarea
            value={evidence}
            onChange={(e) => setEvidence(e.target.value)}
            placeholder="Paste the suspicious message or incident details here..."
            className="min-h-64 w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-4 text-sm leading-7 text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
          />

          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              disabled={loading}
              onClick={analyzeIncident}
              className="rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Analyzing incident..." : "Analyze incident"}
            </button>

            <button
              type="button"
              onClick={downloadReport}
              disabled={reportLoading || !evidence.trim()}
              className="rounded-xl border border-slate-700 px-6 py-3 font-medium text-slate-300 transition hover:border-cyan-500 hover:text-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {reportLoading
                ? "Generating report..."
                : "Download Evidence Report"}
            </button>
          </div>

          {error && (
            <div className="mt-5 rounded-xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
              {error}
            </div>
          )}
        </section>

        {!analysis && !loading && (
          <section className="mt-10 grid gap-5 md:grid-cols-3">
            <InfoCard
              title="Incident timeline"
              text="Reconstruct the sequence of messages, requests, payments, and other events."
            />

            <InfoCard
              title="Claims & evidence"
              text="Separate claims from the evidence you provided and clearly mark what has not been independently verified."
            />

            <InfoCard
              title="Risk indicators"
              text="Identify patterns such as urgency, authority claims, additional payment requests, and credential requests."
            />
          </section>
        )}

        {loading && (
          <section className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
            <div className="mx-auto mb-5 h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />

            <div className="text-lg font-semibold">
              Reconstructing the incident...
            </div>

            <p className="mt-2 text-sm text-slate-400">
              Reconstructing the incident, extracting claims, and identifying
              risk indicators.
            </p>
          </section>
        )}

        {analysis && (
          <section className="mt-10 space-y-6">
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
                <div>
                  <p className="text-sm font-medium text-slate-400">
                    Incident assessment
                  </p>

                  <h2
                    className={`mt-2 text-3xl font-bold ${
                      analysis.assessment.level === "HIGH"
                        ? "text-red-400"
                        : analysis.assessment.level === "ELEVATED"
                          ? "text-orange-400"
                          : analysis.assessment.level === "MODERATE"
                            ? "text-yellow-400"
                            : "text-emerald-400"
                    }`}
                  >
                    {analysis.assessment.level}
                  </h2>
                </div>

                <div className="min-w-32 rounded-xl border border-slate-700 bg-slate-950 px-5 py-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Indicator score
                  </p>

                  <p className="mt-1 text-2xl font-bold">
                    {analysis.assessment.indicator_score}
                  </p>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-cyan-500 transition-all"
                      style={{
                        width: `${Math.min(
                          analysis.assessment.indicator_score,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>

              <p className="mt-6 leading-7 text-slate-300">
                {analysis.summary}
              </p>

              <p className="mt-4 text-sm text-slate-500">
                {analysis.assessment.confidence_note}
              </p>
            </section>

            {analysis.ai_reconstruction?.enabled &&
              analysis.ai_reconstruction.data && (
                <AIReconstructionCard
                  data={analysis.ai_reconstruction.data}
                />
              )}

            {!analysis.ai_reconstruction?.enabled && (
              <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-cyan-400">
                    AI
                  </div>

                  <div>
                    <h2 className="text-lg font-semibold">
                      AI-assisted reconstruction unavailable
                    </h2>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      The deterministic incident analysis is still available.
                      AI reconstruction could not be completed for this
                      request.
                    </p>
                  </div>
                </div>
              </section>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
              <ResultCard title="Risk indicators">
                {analysis.risk_indicators.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    No predefined indicators found.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {analysis.risk_indicators.map((item) => (
                      <div
                        key={item.id}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <h3 className="font-semibold">{item.title}</h3>

                          <span
                            className={`rounded-full px-3 py-1 text-xs font-semibold ${
                              item.severity === "HIGH"
                                ? "bg-red-950 text-red-300"
                                : item.severity === "MEDIUM"
                                  ? "bg-orange-950 text-orange-300"
                                  : "bg-slate-800 text-slate-300"
                            }`}
                          >
                            {item.severity}
                          </span>
                        </div>

                        <p className="mt-2 text-sm leading-6 text-slate-400">
                          {item.explanation}
                        </p>

                        <p className="mt-3 text-xs text-slate-500">
                          Matched: {item.matched_terms.join(", ")}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </ResultCard>

              <ResultCard title="Claims & evidence">
                {analysis.claims.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    No financial claims found.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {analysis.claims.map((item, index) => (
                      <div
                        key={index}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <p className="text-sm leading-6 text-slate-200">
                          {item.claim}
                        </p>

                        <div className="mt-3 space-y-1 text-xs text-slate-500">
                          <p>Source: {item.source}</p>

                          <p className="text-amber-400">
                            {item.verification}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ResultCard>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <ResultCard title="Incident timeline">
                {analysis.timeline.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    No explicit timeline events were found.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {analysis.timeline.map((item, index) => (
                      <div
                        key={index}
                        className="border-l-2 border-cyan-500 pl-4"
                      >
                        <p className="text-xs font-semibold uppercase tracking-wide text-cyan-400">
                          {item.date}
                        </p>

                        <p className="mt-1 text-sm leading-6 text-slate-300">
                          {item.event}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </ResultCard>

              <ResultCard title="Safe response plan">
                {analysis.safe_actions.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    No specific response actions were generated.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {analysis.safe_actions.map((action, index) => (
                      <div
                        key={index}
                        className="flex gap-3 text-sm leading-6 text-slate-300"
                      >
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-cyan-950 text-xs font-bold text-cyan-400">
                          {index + 1}
                        </span>

                        <span>{action}</span>
                      </div>
                    ))}
                  </div>
                )}
              </ResultCard>
            </div>

            {analysis.limitations.length > 0 && (
              <section className="rounded-2xl border border-amber-900/60 bg-amber-950/20 p-6">
                <h2 className="font-semibold text-amber-300">
                  Important limitations
                </h2>

                <ul className="mt-4 space-y-2 text-sm leading-6 text-amber-200/70">
                  {analysis.limitations.map((item, index) => (
                    <li key={index}>• {item}</li>
                  ))}
                </ul>
              </section>
            )}
          </section>
        )}

        <footer className="mt-12 border-t border-slate-800 pt-6 text-sm leading-6 text-slate-500">
          Invoresc is designed to help investors understand and document
          incidents. It does not provide investment recommendations, trading
          signals, or guarantee that an incident is fraud.
        </footer>
      </div>
    </main>
  );
}

function AIReconstructionCard({ data }: { data: AIData }) {
  return (
    <section className="rounded-2xl border border-cyan-900/60 bg-cyan-950/20 p-6">
      <div className="mb-6">
        <p className="text-sm font-medium text-cyan-400">
          AI-assisted reconstruction
        </p>

        <h2 className="mt-2 text-2xl font-bold">
          What the evidence shows
        </h2>

        <p className="mt-2 text-sm leading-6 text-slate-400">
          Gemini organizes the supplied evidence. Claims remain independently
          unverified.
        </p>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="font-semibold">Incident narrative</h3>

          <p className="mt-2 text-sm leading-7 text-slate-300">
            {data.incident_narrative}
          </p>
        </div>

        <div>
          <h3 className="font-semibold">Plain-language explanation</h3>

          <p className="mt-2 text-sm leading-7 text-slate-300">
            {data.plain_language_explanation}
          </p>
        </div>

        {data.claims.length > 0 && (
          <div>
            <h3 className="font-semibold">
              Claims reconstructed from evidence
            </h3>

            <div className="mt-3 space-y-3">
              {data.claims.map((item, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                >
                  <p className="text-sm font-medium text-slate-200">
                    {item.claim}
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Evidence: {item.evidence}
                  </p>

                  <p className="mt-2 text-xs text-amber-400">
                    {item.verification}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.timeline.length > 0 && (
          <div>
            <h3 className="font-semibold">AI-reconstructed timeline</h3>

            <div className="mt-3 space-y-4">
              {data.timeline.map((item, index) => (
                <div
                  key={index}
                  className="border-l-2 border-cyan-500 pl-4"
                >
                  <p className="text-xs font-semibold uppercase tracking-wide text-cyan-400">
                    {item.date_or_time}
                  </p>

                  <p className="mt-1 text-sm leading-6 text-slate-300">
                    {item.event}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Source: {item.source}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.missing_evidence.length > 0 && (
          <div>
            <h3 className="font-semibold">Missing evidence</h3>

            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-400">
              {data.missing_evidence.map((item, index) => (
                <li key={index}>• {item}</li>
              ))}
            </ul>
          </div>
        )}

        {data.documentation_questions.length > 0 && (
          <div>
            <h3 className="font-semibold">What to document or verify</h3>

            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-400">
              {data.documentation_questions.map((item, index) => (
                <li key={index}>• {item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <p className="mt-6 border-t border-slate-800 pt-4 text-xs leading-5 text-slate-500">
        AI-generated reconstruction is based only on the evidence provided. It
        does not establish that fraud occurred and does not provide investment
        recommendations.
      </p>
    </section>
  );
}

function InfoCard({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="font-semibold">{title}</h2>

      <p className="mt-3 text-sm leading-6 text-slate-400">{text}</p>
    </div>
  );
}

function ResultCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-5 text-xl font-semibold">{title}</h2>

      {children}
    </div>
  );
}