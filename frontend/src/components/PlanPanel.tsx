import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

import { approveAction, rejectAction } from "../services/api";
import type { Recommendation } from "../types";

interface PlanPanelProps {
  state: any;
  onUpdateState: (newState: any) => void;
}

export default function PlanPanel({
  state,
  onUpdateState,
}: PlanPanelProps) {
  const p = state?.plan;

  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [showExplain, setShowExplain] = useState(true);

  if (!p) {
    return (
      <div className="empty-plan-state">
        <Sparkles size={28} className="sparkle-icon" />

        <h3>Awaiting Multi-Agent Synthesis</h3>

        <p>
          Trigger a crisis simulation or click <b>START DEMO</b> to
          initiate the agent network.
        </p>
      </div>
    );
  }

  const handleApprove = async (rec: Recommendation) => {
    if (!rec?.id) {
      console.error("Cannot approve recommendation: missing ID", rec);
      return;
    }

    setLoadingAction(rec.id);

    try {
      console.log("Approving action:", rec.id);

      const updated = await approveAction(rec.id);

      console.log("Approve API response:", updated);

      if (!updated) {
        throw new Error("Approve API returned no data");
      }

      onUpdateState(updated);
    } catch (error) {
      console.error("Approve action failed:", error);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleReject = async (rec: Recommendation) => {
    if (!rec?.id) {
      console.error("Cannot reject recommendation: missing ID", rec);
      return;
    }

    setLoadingAction(rec.id);

    try {
      console.log("Rejecting action:", rec.id);

      const updated = await rejectAction(
        rec.id,
        "Disapproved by operator"
      );

      console.log("Reject API response:", updated);

      if (!updated) {
        throw new Error("Reject API returned no data");
      }

      onUpdateState(updated);
    } catch (error) {
      console.error("Reject action failed:", error);
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="plan-container">

      {/* HEADER */}
      <div className="plan-head">
        <div>
          <span className="eyebrow">
            COMMANDER AGENT RESPONSE PLAN
          </span>

          <h2>
            Tactical Directives <em>v{p.version}</em>
          </h2>
        </div>

        <span
          className={`badge ${
            p.status === "APPROVED" ? "green" : "orange"
          }`}
        >
          {p.status === "APPROVED"
            ? "OPERATOR AUTHORIZED"
            : "HUMAN APPROVAL REQUIRED"}
        </span>
      </div>

      {/* REPLANNING ALERT */}
      {p.changes && p.changes.length > 0 && (
        <div className="change-box">
          <div className="change-title">
            <AlertTriangle size={16} />

            <b>
              SITUATION SHIFT DETECTED — AUTONOMOUS
              RE-PLANNING (v{p.version})
            </b>
          </div>

          {p.changes.map((change: string, index: number) => (
            <div key={index} className="change-item">
              ↳ {change}
            </div>
          ))}
        </div>
      )}

      {/* RECOMMENDATIONS */}
      <div className="recommendations-list">
        {p.recommendations?.map(
          (r: Recommendation, index: number) => {
            const isCritical = r.priority === "CRITICAL";
            const isHigh = r.priority === "HIGH";

            const isApproved =
              r.approval_status === "APPROVED";

            const isRejected =
              r.approval_status === "REJECTED";

            const isLoading =
              loadingAction === r.id;

            return (
              <div
                className={`recommendation-card ${
                  isCritical
                    ? "critical-border"
                    : isHigh
                    ? "high-border"
                    : ""
                } ${
                  isApproved
                    ? "approved-card"
                    : ""
                } ${
                  isRejected
                    ? "rejected-card"
                    : ""
                }`}
                key={r.id || r.action}
              >

                {/* RECOMMENDATION HEADER */}
                <div className="rec-header">
                  <span
                    className={`badge ${
                      isCritical
                        ? "red"
                        : isHigh
                        ? "orange"
                        : "amber"
                    }`}
                  >
                    {r.priority}
                  </span>

                  <span className="agent-tag">
                    ⚡ {r.agent || "Commander Agent"}
                  </span>

                  <span className="confidence-pill">
                    {r.confidence || 92}% Confidence
                  </span>
                </div>

                {/* RECOMMENDATION BODY */}
                <div className="rec-body">
                  <h4 className="rec-action">
                    {index + 1}. {r.action}
                  </h4>

                  <p className="rec-reason">
                    {r.reason}
                  </p>

                  <div className="rec-meta">
                    <span>
                      Target: <b>{r.affected_area}</b>
                    </span>

                    {r.affected_count && (
                      <span>
                        Exposed:{" "}
                        <b>
                          {r.affected_count.toLocaleString()} people
                        </b>
                      </span>
                    )}

                    {r.assigned_resource && (
                      <span>
                        Asset: <b>{r.assigned_resource}</b>
                      </span>
                    )}
                  </div>
                </div>

                {/* APPROVAL CONTROLS */}
                <div className="rec-footer">
                  {isApproved ? (
                    <div className="status-badge approved">
                      <CheckCircle2 size={16} />

                      <span>
                        HUMAN APPROVED & SIMULATED
                      </span>
                    </div>
                  ) : isRejected ? (
                    <div className="status-badge rejected">
                      <XCircle size={16} />

                      <span>
                        REJECTED BY OPERATOR
                      </span>
                    </div>
                  ) : (
                    <div className="approval-controls">

                      {/* APPROVE BUTTON */}
                      <button
                        type="button"
                        className="btn success btn-sm"
                        disabled={isLoading}
                        onClick={() => handleApprove(r)}
                      >
                        {isLoading
                          ? "Executing..."
                          : "✓ Approve Action"}
                      </button>

                      {/* REJECT BUTTON */}
                      <button
                        type="button"
                        className="btn warning btn-sm"
                        disabled={isLoading}
                        onClick={() => handleReject(r)}
                      >
                        {isLoading
                          ? "Processing..."
                          : "✗ Reject"}
                      </button>

                    </div>
                  )}
                </div>
              </div>
            );
          }
        )}
      </div>

      {/* EXPLAINABILITY SECTION */}
      <div className="explainability-section">
        <button
          type="button"
          className="explain-toggle"
          onClick={() => setShowExplain(!showExplain)}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <ShieldCheck
              size={16}
              color="#38bdf8"
            />

            <span className="eyebrow">
              AI DECISION EXPLAINABILITY & DATA PROVENANCE
            </span>
          </div>

          {showExplain ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {showExplain && (
          <div className="explain-body">
            {p.explanation?.map(
              (item: string, index: number) => (
                <div
                  key={index}
                  className="explain-point"
                >
                  <span className="check-icon">
                    ✓
                  </span>

                  <p>{item}</p>
                </div>
              )
            )}
          </div>
        )}
      </div>

    </div>
  );
}