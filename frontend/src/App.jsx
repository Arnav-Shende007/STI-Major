import React, { useState, useEffect } from 'react';
import {
  Activity,
  Layers,
  ShieldAlert,
  Database,
  CheckCircle2,
  AlertTriangle,
  Upload,
  Sliders,
  Maximize2,
  ChevronRight,
  TrendingUp,
  Microscope,
  Stethoscope,
  Info,
  Sparkles,
  RefreshCw,
  Clock,
  ShieldCheck,
  AlertCircle,
  Cpu,
  Target,
  Percent,
  Compass,
  FileText,
  ExternalLink,
  Sun,
  Moon
} from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000/api";

const CLEAN_SITES = [
  "Oral Mucosa / Lip (Perioral)",
  "Cutaneous Skin - General (Trunk & Limbs)",
  "Upper Body / Torso (Chest & Back)",
  "Flexural Fold / Inguinal (Upper Thigh)",
  "Mucocutaneous Transition Zone",
  "Perianal Mucocutaneous Zone",
  "General Dermal Region"
];

// Modern Responsive SVG Multi-Drug AMR Trajectory Visualizer with Tooltip
function AmrTrendChart({ data, currentYear, theme }) {
  const [hoverData, setHoverData] = useState(null);

  if (!data || data.length === 0) return null;

  const width = 840;
  const height = 270;
  const padding = { top: 30, right: 35, bottom: 40, left: 50 };

  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const minYear = 2000;
  const maxYear = 2023;
  const maxVal = 45; // Max resistance %

  const getX = (yr) => padding.left + ((yr - minYear) / (maxYear - minYear)) * plotW;
  const getY = (val) => padding.top + plotH - (Math.min(val, maxVal) / maxVal) * plotH;

  const isDark = theme === 'dark';

  const drugs = [
    { key: 'Ciprofloxacin', name: 'Ciprofloxacin', color: '#EF4444', strokeWidth: 2.5 },
    { key: 'Azithromycin', name: 'Azithromycin', color: '#F59E0B', strokeWidth: 2.5 },
    { key: 'Cefixime', name: 'Cefixime', color: isDark ? '#3B82F6' : '#2563EB', strokeWidth: 2.0 },
    { key: 'Ceftriaxone', name: 'Ceftriaxone', color: isDark ? '#10B981' : '#059669', strokeWidth: 2.5 }
  ];

  const paths = drugs.map(drug => {
    const points = data
      .filter(d => d[drug.key] !== undefined && d.year >= minYear)
      .map(d => `${getX(d.year)},${getY(d[drug.key])}`);
    return {
      ...drug,
      d: points.length > 0 ? `M ${points.join(' L ')}` : ''
    };
  });

  const curX = getX(currentYear);

  return (
    <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
        onMouseLeave={() => setHoverData(null)}
      >
        {/* 5% CDC Guideline Alert Threshold Line */}
        <line
          x1={padding.left}
          y1={getY(5)}
          x2={width - padding.right}
          y2={getY(5)}
          stroke={isDark ? "rgba(245, 158, 11, 0.45)" : "rgba(217, 119, 6, 0.55)"}
          strokeWidth="1.5"
          strokeDasharray="5 5"
        />
        <text
          x={width - padding.right}
          y={getY(5) - 6}
          textAnchor="end"
          fontSize="10"
          fill={isDark ? "#F59E0B" : "#B45309"}
          fontWeight="600"
        >
          CDC 5% Alert Threshold (Dual-therapy discontinuation)
        </text>

        {/* Horizontal Grid lines & Y labels */}
        {[0, 10, 20, 30, 40].map((tick) => {
          const y = getY(tick);
          return (
            <g key={tick}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke={isDark ? "rgba(255,255,255,0.07)" : "rgba(203, 213, 225, 0.75)"}
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 12}
                y={y + 4}
                textAnchor="end"
                fontSize="11"
                fill={isDark ? "#64748B" : "#475569"}
                fontWeight="500"
                className="font-mono"
              >
                {tick}%
              </text>
            </g>
          );
        })}

        {/* X Axis year labels */}
        {[2000, 2004, 2008, 2012, 2016, 2020, 2023].map((yr) => {
          const x = getX(yr);
          return (
            <g key={yr}>
              <line
                x1={x}
                y1={height - padding.bottom}
                x2={x}
                y2={height - padding.bottom + 6}
                stroke={isDark ? "rgba(255,255,255,0.2)" : "rgba(148, 163, 184, 0.6)"}
              />
              <text
                x={x}
                y={height - padding.bottom + 20}
                textAnchor="middle"
                fontSize="11"
                fill={isDark ? "#94A3B8" : "#475569"}
                fontWeight="600"
                className="font-mono"
              >
                {yr}
              </text>
            </g>
          );
        })}

        {/* Drug Lines */}
        {paths.map((p) => (
          <path
            key={p.key}
            d={p.d}
            fill="none"
            stroke={p.color}
            strokeWidth={p.strokeWidth}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ))}

        {/* Data points for 2023 with pulsing ring */}
        {drugs.map(drug => {
          const lastPoint = data.find(d => d.year === 2023);
          if (!lastPoint) return null;
          const cx = getX(2023);
          const cy = getY(lastPoint[drug.key]);
          return (
            <g key={drug.key}>
              <circle
                cx={cx}
                cy={cy}
                r="4.5"
                fill={drug.color}
                stroke={isDark ? "#070A12" : "#FFFFFF"}
                strokeWidth="2"
              />
            </g>
          );
        })}

        {/* Current Selected Year Vertical Timeline Marker */}
        {currentYear && (
          <g>
            <line
              x1={curX}
              y1={padding.top}
              x2={curX}
              y2={height - padding.bottom}
              stroke={isDark ? "#60A5FA" : "#2563EB"}
              strokeWidth="2"
              strokeDasharray="3 3"
            />
            <rect
              x={curX - 32}
              y={padding.top - 20}
              width="64"
              height="20"
              rx="6"
              fill={isDark ? "#2563EB" : "#1D4ED8"}
              stroke="rgba(255,255,255,0.3)"
              strokeWidth="1"
            />
            <text
              x={curX}
              y={padding.top - 6}
              textAnchor="middle"
              fontSize="11"
              fill="#FFFFFF"
              fontWeight="700"
              className="font-mono"
            >
              Yr {currentYear}
            </text>
          </g>
        )}

        {/* Interactive Hover Area overlay columns */}
        {data.filter(d => d.year >= minYear).map((d) => {
          const x = getX(d.year);
          return (
            <rect
              key={d.year}
              x={x - 12}
              y={padding.top}
              width={24}
              height={plotH}
              fill="transparent"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHoverData(d)}
            />
          );
        })}
      </svg>

      {/* Floating Hover Tooltip */}
      {hoverData && (
        <div style={{
          position: 'absolute',
          top: '20px',
          right: '25px',
          background: 'var(--tooltip-bg)',
          border: '1px solid var(--tooltip-border)',
          borderRadius: '10px',
          padding: '10px 14px',
          fontSize: '0.8rem',
          backdropFilter: 'blur(12px)',
          boxShadow: '0 8px 25px rgba(0,0,0,0.3)',
          pointerEvents: 'none',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          zIndex: 10
        }}>
          <div style={{ fontWeight: 700, color: 'var(--primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '4px' }}>
            Year {hoverData.year} Resistance Telemetry
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px' }}>
            <span style={{ color: '#EF4444' }}>Ciprofloxacin:</span>
            <b className="font-mono">{Number(hoverData.Ciprofloxacin).toFixed(1)}%</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px' }}>
            <span style={{ color: '#F59E0B' }}>Azithromycin:</span>
            <b className="font-mono">{Number(hoverData.Azithromycin).toFixed(1)}%</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px' }}>
            <span style={{ color: isDark ? '#3B82F6' : '#2563EB' }}>Cefixime:</span>
            <b className="font-mono">{Number(hoverData.Cefixime).toFixed(1)}%</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px' }}>
            <span style={{ color: isDark ? '#10B981' : '#059669' }}>Ceftriaxone:</span>
            <b className="font-mono">{Number(hoverData.Ceftriaxone).toFixed(1)}%</b>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('neurosti_theme') || 'dark');
  const [activeTab, setActiveTab] = useState('diagnose');
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('case_1');
  const [cleanSite, setCleanSite] = useState("Oral Mucosa / Lip (Perioral)");
  const [gender, setGender] = useState("Male");
  const [surveillanceYear, setSurveillanceYear] = useState(2023);
  const [penicillinAllergic, setPenicillinAllergic] = useState(false);
  const [isPregnant, setIsPregnant] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);

  const [loading, setLoading] = useState(false);
  const [diagnosisData, setDiagnosisData] = useState(null);
  const [blendOpacity, setBlendOpacity] = useState(65);
  const [viewMode, setViewMode] = useState('trio'); // 'trio' or 'blender'

  // Benchmarks & AMR Data
  const [metricsData, setMetricsData] = useState(null);
  const [amrTrends, setAmrTrends] = useState([]);
  const [cohortStats, setCohortStats] = useState(null);

  // AMR Simulator Tab State
  const [simCondition, setSimCondition] = useState('Early_Syphilis');
  const [simYear, setSimYear] = useState(2023);
  const [simPen, setSimPen] = useState(false);
  const [simPreg, setSimPreg] = useState(false);
  const [simResults, setSimResults] = useState([]);

  // Apply theme to DOM
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('neurosti_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Fetch benchmark cases & system stats on mount
  useEffect(() => {
    fetch(`${API_BASE}/cases`)
      .then(res => res.json())
      .then(data => {
        setCases(data);
        if (data.length > 0) {
          triggerDiagnosis(data[0].id, cleanSite, gender, surveillanceYear, penicillinAllergic, isPregnant);
        }
      })
      .catch(err => console.error("Could not fetch cases:", err));

    fetch(`${API_BASE}/metrics`)
      .then(res => res.json())
      .then(data => setMetricsData(data))
      .catch(err => console.error(err));

    fetch(`${API_BASE}/amr-trends`)
      .then(res => res.json())
      .then(data => setAmrTrends(data))
      .catch(err => console.error(err));

    fetch(`${API_BASE}/cohort-stats`)
      .then(res => res.json())
      .then(data => setCohortStats(data))
      .catch(err => console.error(err));
  }, []);

  // Update simulator whenever params change
  useEffect(() => {
    fetch(`${API_BASE}/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        condition: simCondition,
        year: simYear,
        penicillin_allergic: simPen,
        is_pregnant: simPreg
      })
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setSimResults(data);
        }
      })
      .catch(err => console.error("Recs error:", err));
  }, [simCondition, simYear, simPen, simPreg]);

  const triggerDiagnosis = async (cId, site, g, yr, pen, preg, customImg = null) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: cId,
          image_base64: customImg,
          clean_site: site,
          gender: g,
          surveillance_year: yr,
          penicillin_allergic: pen,
          is_pregnant: preg
        })
      });
      const data = await res.json();
      setDiagnosisData(data);
    } catch (e) {
      console.error("Diagnosis error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleCaseSelect = (caseItem) => {
    setSelectedCaseId(caseItem.id);
    setCleanSite(caseItem.clean_site);
    setGender(caseItem.gender);
    setUploadedImage(null);
    triggerDiagnosis(caseItem.id, caseItem.clean_site, caseItem.gender, surveillanceYear, penicillinAllergic, isPregnant);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result);
        setSelectedCaseId('custom');
        triggerDiagnosis('custom', cleanSite, gender, surveillanceYear, penicillinAllergic, isPregnant, reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-app)', position: 'relative', zIndex: 1 }}>
      {/* SIDEBAR NAVIGATION */}
      <aside style={{
        width: '300px',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 18px',
        flexShrink: 0,
        zIndex: 20,
        transition: 'background-color 0.35s ease, border-color 0.35s ease'
      }}>
        {/* Brand Header with Theme Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '26px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #2563EB, #10B981)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(37,99,235,0.45)',
              border: '1px solid rgba(255,255,255,0.2)'
            }}>
              <Stethoscope size={24} color="#FFF" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1.2rem', letterSpacing: '-0.3px', color: 'var(--text-main)' }}>
                NeuroSTI <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Decision</span>
              </div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                Multimodal AI + AMR Guidance
              </div>
            </div>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'var(--bg-card-inner)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
            }}
            className="btn-secondary"
          >
            {theme === 'dark' ? (
              <Sun size={18} color="#FBBF24" style={{ transform: 'rotate(0deg)', transition: 'transform 0.4s ease' }} />
            ) : (
              <Moon size={18} color="#2563EB" style={{ transform: 'rotate(0deg)', transition: 'transform 0.4s ease' }} />
            )}
          </button>
        </div>

        {/* System Live Heartbeat Badge with Radar Wave */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          borderRadius: '12px',
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          marginBottom: '26px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.8rem', color: 'var(--success)', fontWeight: 600 }}>
            <span className="radar-beacon" style={{ width: '9px', height: '9px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }}></span>
            <span>ResNet-18 Multimodal</span>
          </div>
          <span className="badge badge-green" style={{ fontSize: '0.68rem', padding: '2px 7px' }}>ACTIVE</span>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
          <button
            onClick={() => setActiveTab('diagnose')}
            className={`nav-btn ${activeTab === 'diagnose' ? 'active' : ''}`}
          >
            <Activity size={18} />
            <span>Clinical Diagnosis & AMR</span>
          </button>

          <button
            onClick={() => setActiveTab('benchmarks')}
            className={`nav-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
          >
            <Layers size={18} />
            <span>Model Benchmarks & Ablation</span>
          </button>

          <button
            onClick={() => setActiveTab('amr')}
            className={`nav-btn ${activeTab === 'amr' ? 'active' : ''}`}
          >
            <ShieldAlert size={18} />
            <span>Smart AMR Surveillance</span>
          </button>

          <button
            onClick={() => setActiveTab('cohort')}
            className={`nav-btn ${activeTab === 'cohort' ? 'active' : ''}`}
          >
            <Database size={18} />
            <span>STIAtlas Cohort Audit</span>
          </button>
        </nav>

        {/* Telemetry Hardware Specs in Sidebar Footer */}
        <div style={{
          paddingTop: '18px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.76rem',
          color: 'var(--text-dim)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={14} color="var(--primary)" />
            <span>512-d Visual + 64-d Metadata</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Microscope size={14} color="var(--success)" />
            <span>Grad-CAM: layer4 conv2</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={14} color="var(--warning)" />
            <span>CDC GISP: 2,511 Records</span>
          </div>
        </div>
      </aside>

      {/* MAIN MAXIMIZED CONTENT WORKBENCH */}
      <main style={{ flex: 1, padding: '30px 42px', overflowY: 'auto', maxHeight: '100vh', position: 'relative' }}>

        {/* =================================================================== */}
        {/* TAB 1: CLINICAL DIAGNOSIS & SMART AMR WORKBENCH */}
        {/* =================================================================== */}
        {activeTab === 'diagnose' && (
          <div className="animate-entrance" key="tab-diagnose">
            {/* Header Telemetry Strip */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '22px' }}>
              <div>
                <h1 style={{ fontSize: '1.95rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
                  Multimodal Clinical Diagnosis & AMR Guidance
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginTop: '3px' }}>
                  Fuses high-resolution clinical photographs with anatomical priors, generating Grad-CAM heatmaps, lesion segmentation, and longitudinal AMR-aware drug rankings.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <label className="btn-secondary" style={{ cursor: 'pointer' }}>
                  <Upload size={16} />
                  <span>Upload Lesion Photo</span>
                  <input type="file" accept="image/*" onChange={handleFileUpload} style={{ display: 'none' }} />
                </label>
                <button
                  className="btn-primary"
                  onClick={() => triggerDiagnosis(selectedCaseId, cleanSite, gender, surveillanceYear, penicillinAllergic, isPregnant, uploadedImage)}
                  disabled={loading}
                >
                  <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                  <span>{loading ? 'Analyzing Neural Tensor...' : 'Re-Run Diagnostic'}</span>
                </button>
              </div>
            </div>

            {/* Benchmark Cases Horizontal Carousel */}
            <div style={{ marginBottom: '22px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                  Standard Clinical Benchmark Cases (Verified Ground Truth)
                </span>
                <span style={{ fontSize: '0.78rem', color: 'var(--primary)', fontWeight: 600 }}>Melbourne Sexual Health Centre (MSHC)</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px' }}>
                {cases.map((c) => {
                  const isSelected = selectedCaseId === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => handleCaseSelect(c)}
                      className={`glass-panel case-card ${isSelected ? 'pulse-glow' : ''}`}
                      style={{
                        padding: '10px',
                        cursor: 'pointer',
                        border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                        background: isSelected ? 'rgba(59,130,246,0.14)' : 'var(--bg-card)'
                      }}
                    >
                      <div style={{ position: 'relative', width: '100%', height: '85px', borderRadius: '8px', overflow: 'hidden', marginBottom: '8px' }}>
                        <img
                          src={c.image_thumb}
                          alt={c.title}
                          style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.3s ease' }}
                          className="hover-zoom"
                        />
                        {isSelected && (
                          <div style={{ position: 'absolute', top: '5px', right: '5px', background: 'var(--primary)', color: '#FFF', borderRadius: '50%', padding: '2px', display: 'flex' }}>
                            <CheckCircle2 size={13} />
                          </div>
                        )}
                      </div>
                      <div style={{ fontSize: '0.82rem', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {c.title}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>{c.clean_site}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Clinical Parameters Configuration Bar */}
            <div className="glass-panel" style={{ padding: '18px 22px', marginBottom: '24px', display: 'grid', gridTemplateColumns: '2fr 1fr 1.6fr 1.2fr 1fr', gap: '18px', alignItems: 'center' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>
                  Anatomical Location (Prior)
                </label>
                <select
                  value={cleanSite}
                  onChange={(e) => setCleanSite(e.target.value)}
                  className="custom-select"
                >
                  {CLEAN_SITES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>
                  Patient Gender
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="custom-select"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600 }}>AMR Surveillance Baseline</span>
                  <span style={{ color: 'var(--primary)', fontWeight: 700 }} className="font-mono">Year {surveillanceYear}</span>
                </div>
                <input
                  type="range"
                  min="2000"
                  max="2023"
                  value={surveillanceYear}
                  onChange={(e) => setSurveillanceYear(parseInt(e.target.value))}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={penicillinAllergic}
                    onChange={(e) => setPenicillinAllergic(e.target.checked)}
                  />
                  <span>Penicillin Allergy</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={isPregnant}
                    onChange={(e) => setIsPregnant(e.target.checked)}
                  />
                  <span>Patient Pregnant</span>
                </label>
              </div>

              <div>
                <button
                  className="btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                  onClick={() => triggerDiagnosis(selectedCaseId, cleanSite, gender, surveillanceYear, penicillinAllergic, isPregnant, uploadedImage)}
                >
                  <Sparkles size={16} />
                  <span>Update</span>
                </button>
              </div>
            </div>

            {/* Diagnostic Output View */}
            {diagnosisData && (
              <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1fr', gap: '24px' }}>
                {/* Left Column: Visual Explainability Suite */}
                <div>
                  <div className="glass-panel" style={{ padding: '22px', marginBottom: '22px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Microscope size={20} color="var(--primary)" />
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Visual Explainability Suite</h3>
                      </div>
                      <div style={{ display: 'flex', gap: '6px', background: 'var(--bg-card-inner)', padding: '3px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                        <button
                          className={`btn-tab ${viewMode === 'trio' ? 'active' : ''}`}
                          onClick={() => setViewMode('trio')}
                        >
                          3-Panel Inspection
                        </button>
                        <button
                          className={`btn-tab ${viewMode === 'blender' ? 'active' : ''}`}
                          onClick={() => setViewMode('blender')}
                        >
                          Alpha Blender Slider
                        </button>
                      </div>
                    </div>

                    {viewMode === 'trio' ? (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
                        <div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                            1. Input Lesion Photo
                          </div>
                          <img
                            src={diagnosisData.original_image_base64}
                            alt="Original"
                            style={{ width: '100%', height: '175px', objectFit: 'cover', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}
                          />
                        </div>
                        <div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                            2. Grad-CAM Saliency
                          </div>
                          <img
                            src={diagnosisData.heatmap_base64}
                            alt="Heatmap"
                            style={{ width: '100%', height: '175px', objectFit: 'cover', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}
                          />
                        </div>
                        <div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                            3. Lesion Contour Mask
                          </div>
                          <img
                            src={diagnosisData.contour_base64}
                            alt="Contours"
                            style={{ width: '100%', height: '175px', objectFit: 'cover', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div style={{ position: 'relative', width: '100%', height: '290px', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border-subtle)', marginBottom: '14px' }}>
                          <img
                            src={diagnosisData.original_image_base64}
                            alt="Base"
                            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
                          />
                          <img
                            src={diagnosisData.heatmap_base64}
                            alt="Heatmap Overlay"
                            style={{
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              opacity: blendOpacity / 100,
                              transition: 'opacity 0.05s ease'
                            }}
                          />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', fontWeight: 600 }}>
                            Heatmap Alpha Blend:
                          </span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={blendOpacity}
                            onChange={(e) => setBlendOpacity(parseInt(e.target.value))}
                          />
                          <span style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--primary)', minWidth: '45px' }} className="font-mono">
                            {blendOpacity}%
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Saliency Metrics footer */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.2fr', marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.82rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Percent size={15} color="var(--success)" />
                        <span>Coverage: <b style={{ color: 'var(--success)' }}>{diagnosisData.coverage_pct}%</b></span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Compass size={15} color="var(--primary)" />
                        <span>Centroid: <b>({diagnosisData.centroid ? diagnosisData.centroid.join(', ') : '320, 240'})</b></span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-dim)' }}>
                        <Target size={15} color="var(--warning)" />
                        <span>Layer: <b>backbone.layer4.conv2</b></span>
                      </div>
                    </div>
                  </div>

                  {/* Modality Attribution Cards */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px', marginBottom: '22px' }}>
                    <div className="glass-panel" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>Visual Morphology</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)', marginTop: '4px' }} className="font-mono">
                        {diagnosisData.modality_attribution.visual_pct}%
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>512-d ResNet Vector</div>
                    </div>

                    <div className="glass-panel" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>Anatomical Site Context</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--success)', marginTop: '4px' }} className="font-mono">
                        {diagnosisData.modality_attribution.site_pct}%
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>Regional Clinical Prior</div>
                    </div>

                    <div className="glass-panel" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>Demographics</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--warning)', marginTop: '4px' }} className="font-mono">
                        {diagnosisData.modality_attribution.gender_pct}%
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>Cohort Prior</div>
                    </div>
                  </div>
                </div>

                {/* Right Column: Diagnosis & Smart AMR Recommendations */}
                <div>
                  {/* Diagnosis Result Card */}
                  <div className="glass-panel pulse-glow" style={{ padding: '24px', marginBottom: '22px', borderLeft: '4px solid var(--primary)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="badge badge-blue">PRIMARY MULTIMODAL PREDICTION</span>
                      <span style={{ fontSize: '1.15rem', fontWeight: 800, color: diagnosisData.confidence > 70 ? 'var(--success)' : 'var(--warning)' }} className="font-mono">
                        {diagnosisData.confidence}% Confidence
                      </span>
                    </div>

                    <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '8px', color: 'var(--text-main)' }}>
                      {diagnosisData.display_name}
                    </h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
                      ICD-10: <b style={{ color: 'var(--text-main)' }}>{diagnosisData.icd10}</b> &nbsp;|&nbsp; Pathogen: <i>{diagnosisData.pathogen}</i>
                    </p>

                    {/* Differential Probabilities Bar */}
                    <div style={{ marginTop: '16px' }}>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 600 }}>
                        Differential Probability Spectrum:
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {diagnosisData.differential.map((d) => (
                          <div key={d.class_name} style={{ display: 'grid', gridTemplateColumns: '130px 1fr 45px', gap: '10px', alignItems: 'center', fontSize: '0.8rem' }}>
                            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.display_name}</span>
                            <div style={{ height: '7px', background: 'var(--bg-card-inner)', borderRadius: '4px', overflow: 'hidden' }} className="shimmer-active">
                              <div style={{ height: '100%', width: `${d.probability}%`, background: d.class_name === diagnosisData.predicted_class ? 'linear-gradient(90deg, #3B82F6, #60A5FA)' : 'rgba(148, 163, 184, 0.35)', borderRadius: '4px' }}></div>
                            </div>
                            <span style={{ textAlign: 'right', fontWeight: 700 }} className="font-mono">{d.probability}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Smart AMR Recommendation Table */}
                  <div className="glass-panel" style={{ padding: '22px', marginBottom: '22px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <ShieldAlert size={20} color="var(--warning)" />
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Smart AMR-Aware Recommendations</h3>
                      </div>
                      <span className="badge badge-yellow">CDC GISP Year {surveillanceYear}</span>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.84rem', textAlign: 'left' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                            <th style={{ padding: '8px' }}>Rank</th>
                            <th style={{ padding: '8px' }}>Regimen</th>
                            <th style={{ padding: '8px' }}>Suitability</th>
                            <th style={{ padding: '8px' }}>AMR %</th>
                            <th style={{ padding: '8px' }}>Clinical Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {diagnosisData.recommendations.map((rec) => {
                            let badgeClass = 'badge-green';
                            if (rec.status_badge === 'alternative') badgeClass = 'badge-yellow';
                            if (rec.status_badge === 'high_amr_risk' || rec.status_badge === 'contraindicated') badgeClass = 'badge-red';

                            return (
                              <tr key={rec.name} className="interactive-row" style={{ borderBottom: '1px solid var(--table-border)' }}>
                                <td style={{ padding: '10px 8px', fontWeight: 700 }}>#{rec.rank}</td>
                                <td style={{ padding: '10px 8px' }}>
                                  <div style={{ fontWeight: 600 }}>{rec.name}</div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{rec.drug_class} • {rec.route}</div>
                                </td>
                                <td style={{ padding: '10px 8px', fontWeight: 800, color: rec.suitability_score >= 80 ? 'var(--success)' : rec.suitability_score >= 50 ? 'var(--warning)' : 'var(--danger)' }} className="font-mono">
                                  {rec.suitability_score}%
                                </td>
                                <td style={{ padding: '10px 8px' }} className="font-mono">{rec.current_resistance_pct}%</td>
                                <td style={{ padding: '10px 8px' }}>
                                  <span className={`badge ${badgeClass}`}>{rec.status.split(' ')[1] || rec.status}</span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>

                    {/* Top Drug Rationale Callout */}
                    {diagnosisData.recommendations.length > 0 && (
                      <div style={{ marginTop: '16px', padding: '14px', background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.25)', borderRadius: '10px', fontSize: '0.82rem' }}>
                        <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '4px' }}>
                          Selected Regimen: {diagnosisData.recommendations[0].name}
                        </div>
                        <div style={{ color: 'var(--text-muted)' }}>
                          {diagnosisData.recommendations[0].rationale}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 2: BENCHMARKS & ABLATION STUDIO */}
        {/* =================================================================== */}
        {activeTab === 'benchmarks' && (
          <div className="animate-entrance" key="tab-benchmarks">
            <h1 style={{ fontSize: '1.95rem', fontWeight: 800, marginBottom: '6px' }}>
              Model Architecture & Master Ablation Studio
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '24px' }}>
              Empirical comparative benchmarking on 63 held-out test cases comparing unimodal baselines against the proposed multimodal fusion network.
            </p>

            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '28px' }}>
              <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid var(--success)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>Proposed Multimodal Accuracy</div>
                <div style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--success)', margin: '4px 0' }} className="font-mono">46.03%</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--success)', fontWeight: 600 }}>+9.52% vs Image-only Baseline</div>
              </div>

              <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid var(--primary)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>Image-only Baseline</div>
                <div style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--primary)', margin: '4px 0' }} className="font-mono">36.51%</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>ResNet-18 Backbone</div>
              </div>

              <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid var(--warning)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>Clinical Metadata Baseline</div>
                <div style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--warning)', margin: '4px 0' }} className="font-mono">25.40%</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Categorical MLP</div>
              </div>

              <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid var(--accent-purple)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>Macro Precision</div>
                <div style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--accent-purple)', margin: '4px 0' }} className="font-mono">46.15%</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Inverse Frequency Weights</div>
              </div>
            </div>

            {/* Master Ablation Table */}
            <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Master Ablation Table</h3>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Quantifies the individual contributions of image features, anatomical site priors, and demographics.
                  </p>
                </div>
                <span className="badge badge-blue">Held-out Test Cohort (N=63)</span>
              </div>

              {metricsData && metricsData.ablation_study && (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '12px' }}>Architecture / Modality Configuration</th>
                      <th style={{ padding: '12px' }}>Accuracy (%)</th>
                      <th style={{ padding: '12px' }}>Macro F1</th>
                      <th style={{ padding: '12px' }}>Macro Precision</th>
                      <th style={{ padding: '12px' }}>Macro Recall</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metricsData.ablation_study.map((row, idx) => {
                      const isProposed = row['Architecture / Modalities'].includes('Proposed');
                      return (
                        <tr key={idx} className="interactive-row" style={{
                          borderBottom: '1px solid var(--table-border)',
                          background: isProposed ? 'rgba(59,130,246,0.12)' : 'transparent',
                          fontWeight: isProposed ? 700 : 400
                        }}>
                          <td style={{ padding: '12px', color: isProposed ? 'var(--primary)' : 'inherit' }}>{row['Architecture / Modalities']}</td>
                          <td style={{ padding: '12px' }} className="font-mono">{row['Accuracy (%)']}%</td>
                          <td style={{ padding: '12px' }} className="font-mono">{row['Macro F1']}</td>
                          <td style={{ padding: '12px' }} className="font-mono">{row['Macro Precision']}</td>
                          <td style={{ padding: '12px' }} className="font-mono">{row['Macro Recall']}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>

            {/* Per-Class Metrics */}
            <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>
                Per-Class Diagnostic Performance (Held-out Test Cohort)
              </h3>
              {metricsData && metricsData.metrics_summary && metricsData.metrics_summary.multimodal_fusion && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                  {Object.entries(metricsData.metrics_summary.multimodal_fusion.per_class).map(([k, v]) => (
                    <div key={k} className="case-card" style={{ padding: '16px', background: 'var(--bg-card-inner)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.98rem', marginBottom: '10px' }}>{v.display_name}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                        <span>Precision: <b style={{ color: 'var(--text-main)' }}>{(v.precision * 100).toFixed(1)}%</b></span>
                        <span>Recall: <b style={{ color: 'var(--text-main)' }}>{(v.recall * 100).toFixed(1)}%</b></span>
                        <span>F1: <b style={{ color: 'var(--primary)' }} className="font-mono">{v.f1_score.toFixed(4)}</b></span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Confusion Matrix Section */}
            {metricsData && metricsData.confusion_matrix_base64 && (
              <div className="glass-panel" style={{ padding: '26px' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>Multimodal Test Confusion Matrix</h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
                  Empirical classification matrix across 63 held-out test cases with stratified distribution.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '26px', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center', background: 'var(--bg-card-inner)', padding: '18px', borderRadius: '14px', border: '1px solid var(--border-subtle)' }}>
                    <img
                      src={metricsData.confusion_matrix_base64}
                      alt="Multimodal Test Confusion Matrix"
                      style={{ maxWidth: '100%', maxHeight: '420px', borderRadius: '10px' }}
                    />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <div style={{ padding: '16px', background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.25)', borderRadius: '12px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '4px' }}>Ulcerative & Vesicular Texture Separation</div>
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                        Early Syphilis and Herpes Simplex achieve robust true-positive localization due to deep convolutional extraction of edge borders combined with anatomical site priors.
                      </div>
                    </div>
                    <div style={{ padding: '16px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: '12px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--success)', marginBottom: '4px' }}>Class Weight Stabilization</div>
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                        Inverse-frequency cross-entropy penalty prevented the classifier from collapsing onto majority classes, preserving diagnostic recall for minority conditions like Tinea and Molluscum.
                      </div>
                    </div>
                    <div style={{ padding: '16px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: '12px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--warning)', marginBottom: '4px' }}>Cross-Modal Complementarity</div>
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                        Fusing visual vectors (512-d) with categorical clinical indicators (64-d) generated an absolute accuracy gain of +9.52% over the image-only ResNet-18 baseline.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 3: SMART AMR SURVEILLANCE & DRUG RANKING */}
        {/* =================================================================== */}
        {activeTab === 'amr' && (
          <div className="animate-entrance" key="tab-amr">
            <h1 style={{ fontSize: '1.95rem', fontWeight: 800, marginBottom: '6px' }}>
              Smart AMR Surveillance & Longitudinal Drug Ranking
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '24px' }}>
              Direct mathematical integration with 2,511 longitudinal CDC GISP resistance records (1999–2023) to govern empirical prescribing.
            </p>

            {/* AMR KPI Badges */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
              <div className="glass-panel" style={{ padding: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Surveillance Records</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', margin: '4px 0' }} className="font-mono">2,511</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>CDC GISP Repository</div>
              </div>
              <div className="glass-panel" style={{ padding: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Surveillance Pathogen</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--success)', margin: '8px 0' }}>N. gonorrhoeae</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>WHO Priority Pathogen</div>
              </div>
              <div className="glass-panel" style={{ padding: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Longitudinal Timeframe</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning)', margin: '4px 0' }} className="font-mono">25 Years</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>1999 to 2023</div>
              </div>
              <div className="glass-panel" style={{ padding: '20px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Frontline Preservation</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--success)', margin: '4px 0' }} className="font-mono">99.9%</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>Ceftriaxone Efficacy</div>
              </div>
            </div>

            {/* Longitudinal Trend Chart Card */}
            <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Longitudinal Antimicrobial Resistance Trajectories (%)</h3>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Tracking Ciprofloxacin, Azithromycin, Cefixime, and Ceftriaxone resistance patterns over 25 years.
                  </p>
                </div>
                {/* Chart Legend */}
                <div style={{ display: 'flex', gap: '14px', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#EF4444' }}></span>
                    <span>Ciprofloxacin (~39.6%)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#F59E0B' }}></span>
                    <span>Azithromycin (~5.8%)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--primary)' }}></span>
                    <span>Cefixime (~0.5%)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--success)' }}></span>
                    <span>Ceftriaxone (~0.1%)</span>
                  </div>
                </div>
              </div>

              {/* Responsive SVG Chart */}
              <AmrTrendChart data={amrTrends} currentYear={simYear} theme={theme} />
            </div>

            {/* Simulator Controls */}
            <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Interactive Longitudinal Drug Suitability Simulator</h3>
                <span className="badge badge-blue">Dynamic Mathematical Recalculation</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 2fr 1fr 1fr', gap: '20px', alignItems: 'center' }}>
                <div>
                  <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>Simulate Condition</label>
                  <select value={simCondition} onChange={(e) => setSimCondition(e.target.value)} className="custom-select">
                    <option value="Early_Syphilis">Early Syphilis</option>
                    <option value="Herpes_Simplex">Herpes Simplex</option>
                    <option value="Genital_Warts">Genital Warts (HPV)</option>
                    <option value="Lichen_Sclerosus">Lichen Sclerosus</option>
                    <option value="Molluscum_Contagiosum">Molluscum Contagiosum</option>
                    <option value="Tinea">Tinea (Fungal)</option>
                  </select>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 600 }}>Surveillance Year Timeline</span>
                    <span style={{ color: 'var(--primary)', fontWeight: 700 }} className="font-mono">Year {simYear}</span>
                  </div>
                  <input type="range" min="2000" max="2023" value={simYear} onChange={(e) => setSimYear(parseInt(e.target.value))} />
                </div>

                <div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
                    <input type="checkbox" checked={simPen} onChange={(e) => setSimPen(e.target.checked)} />
                    <span>Penicillin Allergy</span>
                  </label>
                </div>

                <div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
                    <input type="checkbox" checked={simPreg} onChange={(e) => setSimPreg(e.target.checked)} />
                    <span>Patient Pregnant</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Simulator Table */}
            <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '14px' }}>Ranked Regimens for Year {simYear}</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '10px' }}>Rank</th>
                    <th style={{ padding: '10px' }}>Medication</th>
                    <th style={{ padding: '10px' }}>Class</th>
                    <th style={{ padding: '10px' }}>Route</th>
                    <th style={{ padding: '10px' }}>Suitability Score</th>
                    <th style={{ padding: '10px' }}>Resistance Rate</th>
                    <th style={{ padding: '10px' }}>Clinical Status</th>
                  </tr>
                </thead>
                <tbody>
                  {simResults.map((r) => (
                    <tr key={r.name} className="interactive-row" style={{ borderBottom: '1px solid var(--table-border)' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700 }}>#{r.rank}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 600 }}>{r.name}</td>
                      <td style={{ padding: '12px 10px', color: 'var(--text-dim)' }}>{r.drug_class}</td>
                      <td style={{ padding: '12px 10px' }}>{r.route}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 800, color: r.suitability_score >= 80 ? 'var(--success)' : r.suitability_score >= 50 ? 'var(--warning)' : 'var(--danger)' }} className="font-mono">
                        {r.suitability_score}%
                      </td>
                      <td style={{ padding: '12px 10px' }} className="font-mono">{r.current_resistance_pct}%</td>
                      <td style={{ padding: '12px 10px' }}>
                        <span className={`badge ${r.suitability_score >= 80 ? 'badge-green' : r.suitability_score >= 50 ? 'badge-yellow' : 'badge-red'}`}>
                          {r.status.split(' ')[1] || r.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Clinical Milestones */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div className="glass-panel" style={{ padding: '22px' }}>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F87171', marginBottom: '8px' }}>
                  Ciprofloxacin Abandonment (2002–2007)
                </h4>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                  Surveillance data revealed resistance climbing from 0.3% in 2000 past 15% in 2006 and reaching ~46% in 2023. This led the CDC to completely ban fluoroquinolones as empirical therapy.
                </p>
              </div>

              <div className="glass-panel" style={{ padding: '22px' }}>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '8px' }}>
                  The Landmark 2020 Azithromycin Shift
                </h4>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                  Azithromycin resistance rose above the 5% threshold to 9.1%. To protect frontline cephalosporins from co-selection, the CDC discontinued dual therapy in favor of Ceftriaxone 500mg IM monotherapy.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 4: STIATLAS COHORT AUDIT */}
        {/* =================================================================== */}
        {activeTab === 'cohort' && (
          <div className="animate-entrance" key="tab-cohort">
            <h1 style={{ fontSize: '1.95rem', fontWeight: 800, marginBottom: '6px' }}>
              STIAtlas Clinical Cohort Audit
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '24px' }}>
              Verified distribution across 314 clinical photographs from the Melbourne Sexual Health Centre (MSHC).
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px', marginBottom: '28px' }}>
              <div className="glass-panel" style={{ padding: '26px' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Disease Class Distribution (314 Verified Cases)</h3>
                {cohortStats && cohortStats.classes.map((cls) => (
                  <div key={cls.name} style={{ marginBottom: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', marginBottom: '5px' }}>
                      <span style={{ fontWeight: 600 }}>{cls.name}</span>
                      <span style={{ fontWeight: 700, color: 'var(--primary)' }} className="font-mono">{cls.count} cases</span>
                    </div>
                    <div style={{ height: '9px', background: 'var(--bg-card-inner)', borderRadius: '5px', overflow: 'hidden' }} className="shimmer-active">
                      <div style={{ height: '100%', width: `${(cls.count / 314) * 100}%`, background: 'linear-gradient(90deg, #3B82F6, #60A5FA)', borderRadius: '5px' }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="glass-panel" style={{ padding: '26px' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Anatomical Site Groupings</h3>
                {cohortStats && cohortStats.sites.map((st) => (
                  <div key={st.region} className="case-card" style={{ marginBottom: '16px', padding: '14px', background: 'var(--bg-card-inner)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, fontSize: '0.92rem' }}>
                      <span>{st.region}</span>
                      <span style={{ color: 'var(--primary)' }} className="font-mono">{st.count}</span>
                    </div>
                  </div>
                ))}

                <div style={{ padding: '16px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: '10px', fontSize: '0.84rem', marginTop: '18px', lineHeight: '1.5' }}>
                  <b style={{ color: 'var(--success)' }}>Quality Assurance Audit:</b> 316 downloaded $\to$ 2 non-lesion microscopy slides excluded $\to$ 314 confirmed clinical photographs with zero duplicate hashes across 6 target classes.
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
